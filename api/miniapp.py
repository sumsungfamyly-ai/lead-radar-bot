# -*- coding: utf-8 -*-
"""Бэкенд Telegram Mini App.

Не дублирует логику бота: search вызывает УЖЕ готовый webhook.find_leads(),
а скрипты собираются из тех же шаблонов api/sales.py через webhook.body_*().

Маршруты:
  GET  /api/miniapp           -> HTML интерфейса
  GET  /api/miniapp/config    -> настройки (ниши, режимы, языки, цена)
  POST /api/miniapp/search    -> поиск лидов
  POST /api/miniapp/scripts   -> готовые тексты для выбранного лида
"""

import os
import re
import json
import html as htmllib
import hashlib

from api import webhook as w
from lib import ledger
from lib.miniapp_ui import HTML

FLAG_LABELS = [("p", "📞 С телефоном"), ("e", "✉️ С email"), ("c", "🏪 Без сетей")]


# ---------- мелкие утилиты ----------
def _page(start_response, status="200 OK"):
    body = HTML.encode("utf-8")
    start_response(status, [("Content-Type", "text/html; charset=utf-8"),
                            ("Content-Length", str(len(body)))])
    return [body]


def _json(start_response, obj, status="200 OK"):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    start_response(status, [("Content-Type", "application/json; charset=utf-8"),
                            ("Content-Length", str(len(body)))])
    return [body]


def _payload(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        return {}
    if not length:
        return {}
    try:
        data = json.loads(environ["wsgi.input"].read(length))
        return data if isinstance(data, dict) else {}
    except Exception as err:
        print("miniapp bad payload", err)
        return {}


def _plain(s):
    """Убирает telegram-разметку <b>/<i> из памяток перед показом в <pre>."""
    return htmllib.unescape(re.sub(r"<[^>]+>", "", str(s or ""))).strip()


def _esc(s):
    return htmllib.escape(str(s or ""))


# ---------- endpoint-ы ----------
def config():
    default_niche = os.environ.get("MINIAPP_DEFAULT_NICHE") or "barber"
    if default_niche not in w.NICHES:
        default_niche = "barber"
    return {
        "ok": True,
        "niches": [{"key": k, "label": v[0]} for k, v in w.NICHES.items()],
        "modes": [{"key": k, "label": v} for k, v in w.MODES.items()],
        "flags": [{"key": k, "label": lab} for k, lab in FLAG_LABELS],
        "langs": [{"key": k, "label": lab} for k, lab in w.LANGS],
        "default_lang": w.DEFAULT_LANG,
        "default_niche": default_niche,
        "price": w.PRICE,
        "statuses": [{"key": k, "label": lab} for k, lab in ledger.STATUSES],
    }


def _lead(it, city="", new_ids=(), crm=None):
    """Приводит лид к JSON-виду, понятному интерфейсу."""
    if it.get("kind") == "weak":
        keys = list(dict.fromkeys(k for k, _ in it.get("issues", [])))
    else:
        keys = ["nosite"]
    issues = [[k, t] for k, t in it.get("issues", [])]
    lid = str(it.get("id") or ledger.lead_id(it.get("name"), it.get("addr"),
                                              it.get("site"), city,
                                              it.get("lat"), it.get("lon")))
    status = ledger.get_status(lid)
    if status == "new" and crm:
        old = (crm.get(lid) or {}).get("status")
        if old == "refused":
            status = "lost"
        elif old in ledger.STATUS_KEYS:
            status = old
    audit = it.get("audit") or w.lead_audit(it, it.get("issues", []))
    return {
        "id": lid,
        "is_new": lid in set(new_ids),
        "status": status,
        "name": it.get("name", ""),
        "kind": it.get("kind", "nosite"),
        "site": it.get("site", ""),
        "phone": it.get("phone", ""),
        "email": it.get("email", ""),
        "addr": it.get("addr", ""),
        "lat": it.get("lat"),
        "lon": it.get("lon"),
        "score": it.get("score", 0),
        "issues": issues,
        "socials": it.get("socials") or [],
        "hours": it.get("hours") or "",
        "audit": audit,
        "pitch": [w.PITCH[k] for k in keys[:3] if k in w.PITCH],
    }


def _cache_token(key, mode, city, flags=""):
    return hashlib.md5(f"{key}|{mode}|{city.lower()}|{flags}".encode()).hexdigest()[:10]


def _stale(key, mode, city, flags):
    try:
        hit = w.cache_load(_cache_token(key, mode, city, flags))
        if hit and hit.get("res"):
            return hit["res"]
    except Exception:
        pass
    return None


def _niche_keys(data):
    raw = data.get("keys")
    keys = []
    if isinstance(raw, list):
        for k in raw:
            k = str(k or "").strip()
            if k in w.NICHES and k not in keys:
                keys.append(k)
    if not keys:
        k = data.get("key")
        if k in w.NICHES:
            keys = [k]
    if not keys:
        keys = ["barber"]
    return keys[:4]


def _label_for(keys):
    labels = []
    for k in keys:
        lab = w.NICHES[k][0]
        # убираем ведущий emoji для компактности
        lab = re.sub(r"^[^\wА-Яа-яA-Za-z]+", "", lab).strip() or lab
        labels.append(lab)
    if len(labels) <= 2:
        return " + ".join(labels)
    return labels[0] + " + " + labels[1] + f" + ещё {len(labels)-2}"


def search(data):
    keys = _niche_keys(data)
    mode = data.get("mode") if data.get("mode") in w.MODES else "n"
    city = " ".join(str(data.get("city") or "").split())[:80]
    if not city:
        return {"ok": False, "error": "Напишите город"}
    flags = "".join(ch for ch in str(data.get("flags") or "") if ch in "pec")

    merged, seen = [], set()
    n_no = n_weak = n_with = 0
    errors = 0
    used_stale = False
    per_budget = 45 if len(keys) == 1 else 18 if len(keys) == 2 else 14
    for key in keys:
        try:
            try:
                res = w.find_leads(key, mode, city, flags, budget_s=per_budget)
            except TypeError:
                res = w.find_leads(key, mode, city, flags)
        except Exception as err:
            print("miniapp search fail", key, err)
            if str(err) == "geocode down":
                # геокодер недоступен — пробуем stale, иначе понятная ошибка
                res = _stale(key, mode, city, flags)
                if res:
                    used_stale = True
                else:
                    errors += 1
                    if len(keys) == 1:
                        return {"ok": False, "error": "Сервис геокодирования временно недоступен. Попробуйте ещё раз через 20 секунд или укажите город и страну."}
                    continue
            else:
                res = _stale(key, mode, city, flags)
                if res:
                    used_stale = True
                else:
                    errors += 1
                    continue
        if res is None:
            if len(keys) == 1:
                return {"ok": False,
                        "error": "Не нашёл такой город. Напишите по-английски или добавьте страну."}
            continue
        items, a, b, c = res
        n_no += a; n_weak += b; n_with += c
        for it in items:
            it = dict(it)
            it.setdefault("niche_key", key)
            it["id"] = ledger.lead_id(it.get("name"), it.get("addr"),
                                      it.get("site"), city,
                                      it.get("lat"), it.get("lon"))
            if len(keys) > 1 and it["id"] in seen:
                continue
            seen.add(it["id"])
            merged.append(it)

    if not merged and errors:
        return {"ok": False, "error": "Карты временно недоступны. Попробуйте ещё раз через 20-30 секунд."}

    label = _label_for(keys)
    q = ledger.query_id("+".join(sorted(keys)), mode, city, flags)
    try:
        new_ids = ledger.record_search(q, city, label, mode, flags, merged, "+".join(sorted(keys)))
    except Exception as err:
        print("miniapp history error", err)
        new_ids = [it["id"] for it in merged]
    try:
        crm = w.crm_all() if w.CRM_ON else {}
    except Exception:
        crm = {}

    if mode == "n":
        count = n_no
    elif mode == "w":
        count = n_weak
    else:
        count = n_no + n_weak

    return {
        "ok": True,
        "query_id": q,
        "new_ids": new_ids,
        "city": city,
        "niche_label": label,
        "niche_keys": keys,
        "nosite": n_no,
        "weak": n_weak,
        "total": len(merged),
        "stale": used_stale,
        "partial": errors > 0,
        "potential": _plain(w.potential_text(count)),
        "items": [_lead(it, city, new_ids, crm) for it in merged],
    }


def _objections(ctx, v):
    L = w.T[ctx["lang"]]
    out = "<h4>🛡 Что ответить на возражение</h4>"
    for key, (label, advice) in w.OBJECTIONS.items():
        if key not in L["obj"]:
            continue
        txt = ("Совет: " + _plain(advice) + "\n\nОтвет клиенту:\n"
               + L["obj"][key].format(**v))
        out += "<h4>" + _esc(label) + "</h4><pre>" + _esc(txt) + "</pre>"
    return out


def _plan(ctx):
    plan = w.PLAN_NOSITE if ctx["kind"] == "nosite" else w.PLAN_WEAK
    return ("<h4>📋 План сделки</h4><pre>" + _esc(_plain(plan)) + "</pre>"
            "<h4>🎯 Продающие привычки</h4><pre>" + _esc(_plain(w.GENERAL_TIPS)) + "</pre>")


def scripts(data):
    lang = data.get("lang") if data.get("lang") in w.T else w.DEFAULT_LANG
    kind = "weak" if data.get("kind") == "weak" else "nosite"
    keys, texts = [], []
    for x in (data.get("issues") or []):
        if isinstance(x, (list, tuple)):
            if x:
                keys.append(str(x[0]))
            if len(x) > 1:
                texts.append(str(x[1]))
        elif isinstance(x, str):
            keys.append(x)
    domain = str(data.get("domain") or data.get("site") or "")
    domain = re.sub(r"^https?://", "", domain).rstrip("/")
    ctx = {
        "name": str(data.get("name") or "Клиент")[:80],
        "kind": kind,
        "domain": domain,
        "issues": ", ".join(texts),
        "keys": keys,
        "lang": lang,
    }
    v = w.vars_for(ctx)
    close = w.T[lang]["close_deal"].format(**v)
    return {
        "ok": True,
        "lang": lang,
        "langs": [{"key": k, "label": lab} for k, lab in w.LANGS],
        "body": {
            "dm": w.body_dm(ctx),
            "call": w.body_call(ctx),
            "em": w.body_email(ctx),
            "fu": w.body_fu(ctx),
            "obj": _objections(ctx, v),
            "plan": _plan(ctx),
            "close": "<h4>🤝 Как довести клиента до оплаты</h4><pre>"
                     + _esc(_plain(close)) + "</pre>",
        },
    }


def history():
    return ledger.history_list()


def status(data):
    lid = str(data.get("id") or "")[:64]
    if not lid:
        return {"ok": False, "error": "Нет id лида"}
    state = ledger.set_status(lid, data.get("status") or "new",
                              str(data.get("name") or "")[:80],
                              str(data.get("site") or "")[:200])
    funnel_data = ledger.funnel(limit=1)
    return {"ok": True, "status": state, "counts": funnel_data["counts"]}


def funnel():
    return ledger.funnel()


def audit(data):
    """Детальный аудит сайта через Google PageSpeed (скриншот, если доступен)."""
    site = re.sub(r"^https?://", "", str(data.get("site") or "").strip()).rstrip("/")
    if not site:
        return {"ok": False, "error": "Нет адреса сайта"}
    try:
        data = w.pagespeed("https://" + site)
        lh = data.get("lighthouseResult") or {}
        a = lh.get("audits") or {}
        score = round((((lh.get("categories") or {}).get("performance") or {}).get("score") or 0) * 100)
        shot = ((a.get("final-screenshot") or {}).get("details") or {}).get("data") or ""

        def metric(key):
            v = (a.get(key) or {}).get("numericValue")
            return round(v / 1000, 1) if v is not None else None

        return {
            "ok": True, "site": site, "score": score,
            "fcp": metric("first-contentful-paint"),
            "lcp": metric("largest-contentful-paint"),
            "tbt": metric("total-blocking-time"),
            "cls": metric("cumulative-layout-shift"),
            "screenshot": shot if shot.startswith("data:image") else "",
        }
    except Exception as err:
        print("miniapp audit fail", err)
        return {"ok": False, "error": "Google не смог проверить сайт — попробуйте позже"}


# ---------- WSGI ----------
def app(environ, start_response):
    path = (environ.get("PATH_INFO") or "/").rstrip("/") or "/"
    method = environ.get("REQUEST_METHOD", "GET")

    if path in ("/", "/api/miniapp"):
        return _page(start_response)
    if path.endswith("/config") and method == "GET":
        return _json(start_response, config())
    if path.endswith("/search") and method == "POST":
        return _json(start_response, search(_payload(environ)))
    if path.endswith("/scripts") and method == "POST":
        return _json(start_response, scripts(_payload(environ)))
    if path.endswith("/history") and method == "GET":
        return _json(start_response, history())
    if path.endswith("/status") and method == "POST":
        return _json(start_response, status(_payload(environ)))
    if path.endswith("/funnel") and method == "GET":
        return _json(start_response, funnel())
    if path.endswith("/audit") and method == "POST":
        return _json(start_response, audit(_payload(environ)))
    return _json(start_response, {"ok": False, "error": "not found"}, "404 Not Found")
