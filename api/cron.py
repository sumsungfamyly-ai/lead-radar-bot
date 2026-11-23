"""Ежедневные напоминания о follow-up. Vercel Cron вызывает этот файл раз в сутки.
Работает, только если заданы UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN и MY_CHAT_ID.
"""
import os, json, time, urllib.request

URL = (os.environ.get("UPSTASH_REDIS_REST_URL") or "").rstrip("/")
TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or ""
CHAT = os.environ.get("MY_CHAT_ID") or ""
BOT = os.environ.get("BOT_TOKEN") or ""
CRON_SECRET = os.environ.get("CRON_SECRET") or ""


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


def app(environ, start_response):
    if CRON_SECRET and environ.get("HTTP_AUTHORIZATION") != "Bearer " + CRON_SECRET:
        start_response("403 Forbidden", [("Content-Type", "text/plain")])
        return [b"forbidden"]
    try:
        if URL and TOKEN and CHAT and BOT:
            raw = kv("GET", "crm")
            db = json.loads(raw) if raw else {}
            now = int(time.time())
            due = [(k, r) for k, r in db.items()
                   if r.get("status") == "contacted" and r.get("next") and r["next"] <= now]
            for k, r in due[:20]:
                fu = r.get("fu", 1)
                if fu >= 2:
                    r.pop("next", None)  # после двух напоминаний останавливаемся
                    tail = "Это было последнее напоминание — дальше не беспокоим. Вернуться можно через 1–2 месяца."
                else:
                    r["fu"] = fu + 1
                    r["next"] = now + 4 * 86400
                    tail = "Если снова тишина — напомню ещё раз через 4 дня, потом остановлюсь."
                name = r.get("name", "клиент")
                site = r.get("site", "")
                text = (f"🔁 <b>Пора напомнить о себе:</b> {name}\n"
                        + (f"Сайт: {site}\n" if site else "")
                        + f"Прошло 3+ дня с первого сообщения. Отправь follow-up (кнопка «🔁 Follow-up» в скриптах).\n{tail}")
                try:
                    send(text)
                except Exception as e:
                    print("cron send error", e)
            if due:
                kv("SET", "crm", json.dumps(db, ensure_ascii=False))
    except Exception as e:
        print("cron error", e)
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"ok"]