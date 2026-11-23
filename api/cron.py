"""Ежедневная задача: новые лиды по сохранённым запросам + follow-up.

Vercel Cron вызывает этот файл раз в сутки (0 9 * * *).
Работает с Upstash; без него — в памяти процесса (локально).
"""
import os
import json
import time
import urllib.request

from lib import ledger
from api import webhook as w

URL = (os.environ.get("UPSTASH_REDIS_REST_URL") or "").rstrip("/")
TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or ""
CHAT = os.environ.get("MY_CHAT_ID") or ""
BOT = os.environ.get("BOT_TOKEN") or ""
CRON_SECRET = os.environ.get("CRON_SECRET") or ""
APP_URL = (os.environ.get("APP_URL")
           or (("https://" + os.environ["VERCEL_URL"]) if os.environ.get("VERCEL_URL") else "")).rstrip("/")


def kv(*args):
    req = urllib.request.Request(URL, data=json.dumps(list(args)).encode(),
                                 headers={"Authorization": "Bearer " + TOKEN,
                                          "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=10).read()).get("result")


def send(text):
    req = urllib.request.Request(f"https://api.telegram.org/bot{BOT}/sendMessage",
                                 data=json.dumps({"chat_id": CHAT, "text": text,
                                                  "parse_mode": "HTML"}).encode(),
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10).read()


def _esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def followups():
    """Напоминания тем, кому уже написали и кто не ответил."""
    raw = kv("GET", ledger.CRM_KEY) if ledger.enabled() else None
    try:
        db = json.loads(raw) if raw else ledger._MEM.get(ledger.CRM_KEY, {})
    except Exception:
        db = {}
    if not isinstance(db, dict):
        db = {}
    now = int(time.time())
    due = [(k, r) for k, r in db.items()
           if r.get("status") == "contacted" and r.get("next") and r["next"] <= now]
    for k, r in due[:20]:
        fu = r.get("fu", 1)
        if fu >= 2:
            r.pop("next", None)
            tail = "Это было последнее напоминание — дальше не беспокоим."
        else:
            r["fu"] = fu + 1
            r["next"] = now + 4 * 86400
            tail = "Если снова тишина — напомню ещё раз через 4 дня."
        text = (f"🔁 <b>Пора напомнить о себе:</b> {_esc(r.get('name', 'клиент'))}\n"
                + (f"Сайт: {_esc(r.get('site', ''))}\n" if r.get("site") else "")
                + f"Открой скрипт «🔁 Follow-up» и отправь короткое сообщение.\n{tail}")
        try:
            send(text)
        except Exception as e:
            print("cron send error", e)
    if due:
        ledger._save(ledger.CRM_KEY, db)


def digest():
    """Перепроверяет сохранённые запросы и сообщает о действительно новых лидах."""
    rows = ledger.history()[:3]
    if not rows:
        return
    lines = []
    for row in rows:
        key = row.get("niche_key") or "barber"
        if key not in w.NICHES:
            continue
        city = row.get("city") or ""
        try:
            res = w.find_leads(key, row.get("mode") or "n", city, row.get("flags") or "")
        except Exception as e:
            print("cron search fail", e)
            continue
        if not res:
            continue
        items = res[0]
        for it in items:
            it.setdefault("id", ledger.lead_id(it.get("name"), it.get("addr"),
                                                it.get("site"), city))
        fresh_ids = set(ledger.record_search(
            row.get("q") or ledger.query_id(key, row.get("mode") or "n", city,
                                             row.get("flags") or ""),
            city, row.get("label") or w.NICHES[key][0], row.get("mode") or "n",
            row.get("flags") or "", items, key))
        if not fresh_ids:
            continue
        fresh = [it for it in items if it.get("id") in fresh_ids][:4]
        lines.append(f"🆕 <b>{_esc(city)} · {_esc(row.get('label') or w.NICHES[key][0])}</b> "
                     f"— новых: {len(fresh_ids)}")
        for it in fresh:
            contact = it.get("site") or it.get("phone") or "без контактов"
            lines.append("• " + _esc(it.get("name", "без названия")) + " — " + _esc(contact))
    if not lines:
        return
    if APP_URL:
        lines.append(f'\n<a href="{_esc(APP_URL + "/api/miniapp")}">Открыть мини-приложение</a>')
    send("☀️ <b>Утренний дайджест лидов</b>\n\n" + "\n".join(lines))


def app(environ, start_response):
    if CRON_SECRET and environ.get("HTTP_AUTHORIZATION") != "Bearer " + CRON_SECRET:
        start_response("403 Forbidden", [("Content-Type", "text/plain")])
        return [b"forbidden"]
    try:
        if BOT and CHAT:
            followups()
            try:
                digest()
            except Exception as e:
                print("cron digest error", e)
    except Exception as e:
        print("cron error", e)
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"ok"]
