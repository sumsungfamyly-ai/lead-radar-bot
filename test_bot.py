# -*- coding: utf-8 -*-
"""Smoke-тест: имитируем Telegram и карты, проверяем логику бота и чистоту чата."""
import os, sys, json
os.environ["BOT_TOKEN"] = "test"
os.environ["MY_NAME"] = "Алекс"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api import webhook as w

calls = []          # все вызовы "Telegram"
msgs = {}           # message_id -> текст (живые сообщения)
uploads = []        # загруженные файлы (CSV и т.д.)
_next = [100]

def fake_tg(method, **params):
    calls.append((method, params))
    if method == "sendMessage":
        _next[0] += 1
        mid = _next[0]
        msgs[mid] = params.get("text", "")
        return {"message_id": mid}
    if method == "editMessageText":
        mid = params["message_id"]
        if mid not in msgs:
            return None
        msgs[mid] = params["text"]
        return {"message_id": mid}
    if method == "deleteMessage":
        msgs.pop(params["message_id"], None)
        return True
    if method == "answerCallbackQuery":
        return True
    return None

def fake_upload(method, fields, filename, content, field="document"):
    uploads.append((method, filename, content))
    return {"message_id": 1}

w.tg = fake_tg
w.tg_upload = fake_upload

FAKE = ([{"name": "Кафе Ромашка", "site": "", "lat": 60.1, "lon": 24.9,
          "phone": "+358401234567", "email": "", "addr": "Mannerheimintie 1",
          "score": 0, "issues": [], "kind": "nosite"}] * 12, 12, 0, 0)
searches = [0]
last_flags = [""]
def fake_find(key, mode, city, flags=""):
    searches[0] += 1
    last_flags[0] = flags
    return FAKE
w.find_leads = fake_find

def cb(data, mid):
    return {"callback_query": {"id": "1", "data": data,
                               "message": {"message_id": mid, "chat": {"id": 1},
                                           "text": msgs.get(mid, "")}}}

def user(text, reply_to=None):
    m = {"message_id": 9000 + len(calls), "chat": {"id": 1}, "text": text}
    if reply_to:
        m["reply_to_message"] = {"message_id": reply_to, "text": msgs.get(reply_to, "")}
    return {"message": m}

# 1. /start
w.handle(user("/start"))
assert any("Выбери нишу" in t for t in msgs.values()), "меню не отправлено"
menu_mid = [m for m, t in msgs.items() if "Выбери нишу" in t][0]
assert 9000 not in msgs, "команда /start не удалена"

# 2. выбор ниши — меню редактируется на месте
n_before = len(msgs)
w.handle(cb("n|food", menu_mid))
assert len(msgs) == n_before, "выбор ниши создал лишнее сообщение"
assert "Что ищем?" in msgs[menu_mid]

# 2b. фильтры переключаются на месте
w.handle(cb("f|food|p", menu_mid))
assert "только с телефоном" in msgs[menu_mid]
assert len(msgs) == n_before

# 3. выбор режима — появляется запрос города (с фильтром)
w.handle(cb("m|food|n|p", menu_mid))
prompt_mid = [m for m, t in msgs.items() if t.startswith("🔎 Ниша:")][0]
assert menu_mid not in msgs, "сообщение выбора режима не удалено"
assert "только с телефоном" in msgs[prompt_mid]

# 4. город ответом — поиск, статус и сообщение пользователя удалены
w.handle(user("Helsinki", reply_to=prompt_mid))
assert searches[0] == 1
assert last_flags[0] == "p", "фильтр не дошёл до поиска"
assert prompt_mid not in msgs, "подсказка 'напиши город' не удалена"
assert not any(t.startswith("⏳") for t in msgs.values()), "статус 'Ищу...' не удалён"
assert not any(t == "Helsinki" for t in msgs.values()), "сообщение с городом не удалено"
cards = [m for m, t in msgs.items() if "Кафе Ромашка" in t]
assert len(cards) == 5, f"ожидалось 5 карточек, got {len(cards)}"
pager = [m for m, t in msgs.items() if t.startswith("Показано")][0]
assert "1–5 из 12" in msgs[pager]

# 5. листание: поиск НЕ повторяется, старый счётчик удалён
token = list(w._CACHE)[0]
w.handle(cb(f"p|food|n|{token}|5|p", pager))
assert searches[0] == 1, "повторный поиск при листании!"
assert pager not in msgs, "старый счётчик страниц не удалён"
pager2 = [m for m, t in msgs.items() if t.startswith("Показано")][0]
assert "6–10 из 12" in msgs[pager2]

# 5b. CSV-выгрузка
w.handle(cb(f"e|{token}", pager2))
assert uploads and uploads[0][1].endswith(".csv"), "CSV не отправлен"
assert "Кафе Ромашка" in uploads[0][2].decode("utf-8-sig")

# 6. кнопка Меню превращает счётчик в меню
n_before = len(msgs)
w.handle(cb("menu", pager2))
assert "Выбери нишу" in msgs[pager2]
assert len(msgs) == n_before

# 7. панель скриптов: новая заменяет старую (карточки текущей страницы)
cards_now = [m for m, t in msgs.items() if "Кафе Ромашка" in t]
w.handle(cb("t|o", cards_now[0]))
panel1 = [m for m, t in msgs.items() if t.startswith("✍️")][0]
w.handle(cb("t|o", cards_now[1]))
assert panel1 not in msgs, "старая панель скриптов не удалена"
panel2 = [m for m, t in msgs.items() if t.startswith("✍️")][0]

# 8. язык и разделы редактируют панель на месте; новые языки работают
n_before = len(msgs)
w.handle(cb("t|L|de", panel2))
w.handle(cb("t|c|dm", panel2))
assert len(msgs) == n_before
assert "gute Lage" in msgs[panel2], "немецкий текст не подставился"
w.handle(cb("t|L|et", panel2))
w.handle(cb("t|c|em", panel2))
assert "Tere!" in msgs[panel2], "эстонский текст не подставился"
w.handle(cb("t|L|ru", panel2))
w.handle(cb("t|z", panel2))
assert "Как довести до оплаты" in msgs[panel2], "блок закрытия сделки не открылся"
w.handle(cb("t|b", panel2))
assert "Выбери, что нужно" in msgs[panel2]

# 9. повторное меню не плодит сообщения
n_before = len(msgs)
w.handle(user("привет"))
assert len(msgs) <= n_before, "случайное сообщение породило лишнее меню"

# 10. остывший кэш: вместо ошибки бот снова спрашивает город
w._CACHE.clear()
w.handle(cb("p|food|n|deadbeef00|5|p", pager2))
assert any(t.startswith("🔎 Ниша:") for t in msgs.values()), "не спросил город при остывшем кэше"

# 11. радиус парсится корректно
assert w.parse_city("Helsinki, 10 км") == ("Helsinki", 10)
assert w.parse_city("Turku, 5 km") == ("Turku", 5)
assert w.parse_city("Helsinki") == ("Helsinki", 0)

# 12. /stats и /fav без CRM дают понятную подсказку, а не ошибку
w.handle(user("/stats"))
w.handle(user("/fav"))
assert any("Upstash" in t or "upstash" in t for t in msgs.values())

# 13. город просто текстом (без reply) — поиск запускается, ниша барбершопов есть
assert "barber" in w.NICHES, "ниша барбершопов не добавлена"
w.handle(user("/start"))
menu_mid = [m for m, t in msgs.items() if "Выбери нишу" in t][0]
w.handle(cb("n|barber", menu_mid))
w.handle(cb("m|barber|n|", menu_mid))
prompt_mid = [m for m, t in msgs.items() if t.startswith("🔎 Ниша:")][0]
n_search = searches[0]
w.handle(user("Helsinki"))
assert searches[0] == n_search + 1, "город без reply не запустил поиск"
assert prompt_mid not in msgs, "подсказка не удалена после поиска без reply"

# 14. 🙈 Скрыть / 📂 Показать снова — без повторного поиска
token = list(w._CACHE)[0]
pager = [m for m, t in msgs.items() if t.startswith("Показано")][0]
w.handle(cb(f"hide|{token}", pager))
assert not any("Кафе Ромашка" in t for t in msgs.values()), "карточки не скрылись"
hidden = [m for m, t in msgs.items() if t.startswith("🙈")][0]
n_search = searches[0]
w.handle(cb(f"show|{token}|0", hidden))
assert searches[0] == n_search, "«Показать снова» запустил поиск заново"
assert len([m for m, t in msgs.items() if "Кафе Ромашка" in t]) == 5, "карточки не вернулись"
assert hidden not in msgs, "сообщение «скрыто» не удалено"

# 15. ❌ Закрыть убирает подсказки
pager = [m for m, t in msgs.items() if t.startswith("Показано")][0]
w.handle(cb("menu", pager))
w.handle(cb("tips", pager))
tips_mid = w._CHAT[1]["tips"]
w.handle(cb("del", tips_mid))
assert tips_mid not in msgs, "подсказки не закрылись кнопкой"

# 16. ⬅️ Назад с экрана режимов возвращает в меню на месте
w.handle(cb("n|food", pager))
assert "Что ищем?" in msgs[pager]
w.handle(cb("back_menu", pager))
assert "Выбери нишу" in msgs[pager], "кнопка Назад не вернула меню"

# 17. мини-приложение: HTML и JSON-маршруты отвечают без ошибок
import io
from api import miniapp as ma

def wsgi(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else b""
    env = {"PATH_INFO": path, "REQUEST_METHOD": method,
           "CONTENT_LENGTH": str(len(data)), "wsgi.input": io.BytesIO(data)}
    got = {}
    def start(status, headers):
        got["status"] = status
    raw = b"".join(ma.app(env, start))
    return got["status"], raw

status, raw = wsgi("/api/miniapp")
assert status == "200 OK" and b"LEAD RADAR" in raw and b"radar" in raw, "HTML мини-приложения не отдан"
status, raw = wsgi("/api/miniapp/config")
cfg = json.loads(raw)
assert cfg["ok"] and any(n["key"] == "barber" for n in cfg["niches"]), "нет ниш в конфиге"
assert cfg["default_niche"] == "barber" and len(cfg["langs"]) == 6

# 18. поиск в мини-приложении использует ту же функцию, что и бот
n_search = searches[0]
status, raw = wsgi("/api/miniapp/search", "POST",
                   {"key": "barber", "mode": "n", "city": "Helsinki", "flags": "p"})
r = json.loads(raw)
assert r["ok"] and searches[0] == n_search + 1, "мини-приложение не вызвало поиск бота"
assert r["total"] == 12 and r["items"][0]["kind"] == "nosite" and r["items"][0]["pitch"]
assert json.loads(wsgi("/api/miniapp/search", "POST", {"city": ""})[1])["ok"] is False

# 19. скрипты мини-приложения: все 7 вкладок на всех 6 языках
issue = [["mobile", "не адаптирован под телефон"], ["https", "нет HTTPS"]]
for lang in w.T:
    status, raw = wsgi("/api/miniapp/scripts", "POST",
                       {"name": "Тест", "kind": "weak", "issues": issue,
                        "domain": "site.fi", "site": "http://site.fi", "lang": lang})
    rr = json.loads(raw)
    assert rr["ok"] and set(("dm", "call", "em", "fu", "obj", "plan", "close")) <= set(rr["body"])
    assert all(rr["body"].values()), f"пустая вкладка на языке {lang}"
nosite_dm = json.loads(wsgi("/api/miniapp/scripts", "POST",
                            {"name": "Тест", "kind": "nosite", "lang": "ru"})[1])["body"]["dm"]
assert "Тест" in nosite_dm, "скрипт для лида без сайта не подставил имя"

# 20. «Отправить в чат» и кнопка в меню
payload = json.dumps({"name": "Тест", "kind": "nosite", "site": "", "issues": [], "lang": "ru"})
w.handle({"message": {"message_id": 7777, "chat": {"id": 1},
                      "web_app_data": {"data": payload}}})
assert 7777 not in msgs, "служебное сообщение мини-приложения не удалено"
assert any(t.startswith("✍️") and "Тест" in t for t in msgs.values()), "панель скриптов не открылась"
w.MINIAPP_URL = "https://example.vercel.app/api/miniapp"
buttons = [b for row in w.menu_markup()["inline_keyboard"] for b in row]
assert any("web_app" in b for b in buttons), "в меню нет кнопки мини-приложения"
w.MINIAPP_URL = ""

print("OK: все 20 сценариев прошли")
print("живых сообщений в чате:", len(msgs))