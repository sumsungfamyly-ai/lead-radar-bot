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

from api import webhook as w
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
    }


def _lead(it):
    """Приводит лид к JSON-виду, понятному интерфейсу."""
    if it.get("kind") == "weak":
        keys = list(dict.fromkeys(k for k, _ in it.get("issues", [])))
    else:
        keys = ["nosite"]
    issues = [[k, t] for k, t in it.get("issues", [])]
    return {
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
        "pitch": [w.PITCH[k] for k in keys[:3] if k in w.PITCH],
    }


def search(data):
    key = data.get("key") if data.get("key") in w.NICHES else "barber"
    mode = data.get("mode") if data.get("mode") in w.MODES else "n"
    city = " ".join(str(data.get("city") or "").split())[:80]
    if not city:
        return {"ok": False, "error": "Напишите город"}
    flags = "".join(ch for ch in str(data.get("flags") or "") if ch in "pec")

    try:
        res = w.find_leads(key, mode, city, flags)
    except Exception as err:
        print("miniapp search fail", err)
        return {"ok": False, "error": "Карты временно недоступны — попробуйте ещё раз"}
    if res is None:
        return {"ok": False,
                "error": "Не нашёл такой город. Напишите по-английски или добавьте страну."}

    items, n_no, n_weak, n_with = res
    if mode == "n":
        count = n_no
    elif mode == "w":
        count = n_weak
    else:
        count = n_no + n_weak
    return {
        "ok": True,
        "city": city,
        "niche_label": w.NICHES[key][0].replace("🦷", "").replace("🩺", "").strip() or w.NICHES[key][0],
        "nosite": n_no,
        "weak": n_weak,
        "total": len(items),
        "potential": _plain(w.potential_text(count)),
        "items": [_lead(it) for it in items],
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
    return _json(start_response, {"ok": False, "error": "not found"}, "404 Not Found")
