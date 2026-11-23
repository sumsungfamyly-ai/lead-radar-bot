# -*- coding: utf-8 -*-
"""История поисков, «новые лиды» и статусы сделок.

Одно хранилище на три места: бот, мини-приложение и ежедневный cron.
Если Upstash не задан, работает в памяти процесса (для локальной разработки).
"""

import hashlib
import json
import os
import re
import time
import urllib.request

URL = (os.environ.get("UPSTASH_REDIS_REST_URL") or "").rstrip("/")
TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or ""

HISTORY_KEY = "lr_history"
SEEN_KEY = "lr_seen"
CRM_KEY = "crm"

STATUSES = [
    ("new", "🆕 Новый"),
    ("contacted", "📨 Написал"),
    ("replied", "💬 Ответил"),
    ("meeting", "📅 Встреча"),
    ("deal", "✅ Сделка"),
    ("lost", "🚫 Отказ"),
]
STATUS_KEYS = [k for k, _ in STATUSES]

_MEM = {}


def enabled():
    return bool(URL and TOKEN)


def kv(*args):
    """Выполняет команду Upstash REST. Возвращает None при любой ошибке."""
    if not enabled():
        return None
    try:
        req = urllib.request.Request(
            URL,
            data=json.dumps(list(args)).encode("utf-8"),
            headers={"Authorization": "Bearer " + TOKEN,
                     "Content-Type": "application/json"},
        )
        return json.loads(urllib.request.urlopen(req, timeout=8).read()).get("result")
    except Exception as err:
        print("ledger kv error", err)
        return None


def _load(key, default):
    raw = kv("GET", key)
    if raw is None:
        return _MEM.get(key, default)
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return default


def _save(key, value):
    _MEM[key] = value
    kv("SET", key, json.dumps(value, ensure_ascii=False))
    return value


def _norm_name(name):
    s = str(name or "").lower().strip()
    s = re.sub(r"[\"'`’]", "", s)
    s = re.sub(r"[^0-9a-zа-яёіїєäöüßåøæ\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def lead_id(name, addr="", site="", city="", lat=None, lon=None):
    """Стабильный id лида: нормализованное имя + город/координаты."""
    nm = _norm_name(name)
    ct = str(city or "").strip().lower()
    try:
        if lat is not None and lon is not None and str(lat) != "" and str(lon) != "":
            base = f"{nm}|{ct}|{round(float(lat), 3)}|{round(float(lon), 3)}"
        else:
            ad = re.sub(r"\s+", " ", str(addr or "").strip().lower())
            base = f"{nm}|{ct}|{ad}"
    except Exception:
        base = f"{nm}|{ct}|{str(addr or '').lower()}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()[:12]


def query_id(key, mode, city, flags=""):
    base = "|".join([str(key or ""), str(mode or ""), str(city or "").lower(),
                     str(flags or "")])
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


def history():
    v = _load(HISTORY_KEY, [])
    return v if isinstance(v, list) else []


def seen():
    v = _load(SEEN_KEY, {})
    return v if isinstance(v, dict) else {}


def record_search(q, city, niche_label, mode, flags, items, niche_key=""):
    """Сохраняет поиск и возвращает список id лидов, которых не было раньше."""
    now = int(time.time())
    ids = []
    for it in items or []:
        lid = str(it.get("id") or lead_id(it.get("name"), it.get("addr"),
                                           it.get("site"), city))
        ids.append(lid)

    previous = set()
    for row in history():
        if row.get("q") == q:
            previous = set(row.get("ids") or [])
            break
    new_ids = [i for i in ids if i not in previous]
    if not previous:  # первый поиск — все лиды впервые
        new_ids = list(ids)

    rows = [r for r in history() if r.get("q") != q]
    rows.insert(0, {
        "q": q,
        "city": city,
        "label": niche_label or "",
        "niche": niche_label or "",
        "niche_key": niche_key or "",
        "mode": mode,
        "flags": flags,
        "ts": now,
        "count": len(ids),
        "new_count": len(new_ids),
        "ids": ids,
    })
    _save(HISTORY_KEY, rows[:30])

    db = seen()
    for it in items or []:
        lid = str(it.get("id") or lead_id(it.get("name"), it.get("addr"),
                                           it.get("site"), city))
        old = db.get(lid) or {}
        db[lid] = {
            "id": lid,
            "name": it.get("name") or old.get("name") or "",
            "site": it.get("site") or old.get("site") or "",
            "city": city,
            "kind": it.get("kind") or old.get("kind") or "nosite",
            "status": old.get("status") or "new",
            "first_ts": old.get("first_ts") or now,
            "last_ts": now,
        }
    # не даём базе расти бесконечно
    if len(db) > 800:
        keep = sorted(db.values(), key=lambda r: r.get("last_ts") or 0)[-600:]
        db = {r["id"]: r for r in keep}
    _save(SEEN_KEY, db)
    return new_ids


def get_status(lid):
    return (seen().get(str(lid)) or {}).get("status") or "new"


def set_status(lid, status, name="", site=""):
    """Меняет статус лида и синхронизирует напоминания с CRM бота."""
    status = status if status in STATUS_KEYS else "new"
    db = seen()
    row = db.get(str(lid)) or {
        "id": str(lid), "name": name or "", "site": site or "",
        "first_ts": int(time.time()),
    }
    row["status"] = status
    row["last_ts"] = int(time.time())
    if name:
        row["name"] = name
    if site:
        row["site"] = site
    db[str(lid)] = row
    _save(SEEN_KEY, db)
    _sync_crm(str(lid), row)
    return status


def _sync_crm(lid, row):
    """Старый cron ищет status == 'contacted' с полем next."""
    raw = kv("GET", CRM_KEY)
    try:
        crm = json.loads(raw) if raw else {}
    except Exception:
        crm = _MEM.get(CRM_KEY, {})
    if not isinstance(crm, dict):
        crm = {}
    entry = crm.get(lid) or {}
    entry.update({"name": row.get("name", ""), "site": row.get("site", ""),
                  "fu": entry.get("fu", 0)})
    if row.get("status") == "contacted":
        entry["status"] = "contacted"
        entry.setdefault("next", int(time.time()) + 3 * 86400)
    else:
        entry["status"] = row.get("status")
        entry.pop("next", None)
    crm[lid] = entry
    _save(CRM_KEY, crm)


def counts():
    c = {k: 0 for k in STATUS_KEYS}
    for row in seen().values():
        s = row.get("status") if row.get("status") in c else "new"
        c[s] += 1
    return c


def funnel(limit=60):
    rows = sorted(seen().values(),
                  key=lambda r: r.get("last_ts") or 0, reverse=True)[:limit]
    return {
        "ok": True,
        "counts": counts(),
        "statuses": [{"key": k, "label": lab} for k, lab in STATUSES],
        "items": [{"id": r.get("id"), "name": r.get("name", ""),
                   "site": r.get("site", ""), "status": r.get("status", "new")}
                  for r in rows],
    }


def history_list(limit=15):
    rows = []
    for r in history()[:limit]:
        rows.append({
            "q": r.get("q", ""),
            "city": r.get("city", ""),
            "label": r.get("label") or r.get("niche") or "",
            "niche": r.get("niche") or r.get("label") or "",
            "niche_key": r.get("niche_key") or "",
            "mode": r.get("mode", "n"),
            "flags": r.get("flags", ""),
            "ts": r.get("ts", 0),
            "count": r.get("count", 0),
            "new_count": r.get("new_count", 0),
        })
    return {"ok": True, "items": rows}
