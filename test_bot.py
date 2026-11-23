# -*- coding: utf-8 -*-
"""Smoke-тест: имитируем Telegram и карты, проверяем логику бота и чистоту чата."""
import os, sys, json
os.environ["BOT_TOKEN"] = "test"
os.environ["MY_NAME"] = "Алекс"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api import webhook as w

calls = []          # все вызовы "Telegram"
msgs = {}           # message_id -> текст (живые сообщения)
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

w.tg = fake_tg

FAKE = ([{"name": "Кафе Ромашка", "site": "", "lat": 60.1, "lon": 24.9,
          "phone": "+358401234567", "email": "", "addr": "Mannerheimintie 1",
          "score": 0, "issues": [], "kind": "nosite"}] * 12, 12, 0, 0)
searches = [0]
def fake_find(key, mode, city):
    searches[0] += 1
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

def methods():
    return [c[0] for c in calls]

# 1. /start
w.handle(user("/start"))
assert any("Выбери нишу" in t for t in msgs.values()), "меню не отправлено"
menu_mid = [m for m, t in msgs.items() if "Выбери нишу" in t][0]
assert 9000 not in msgs, "команда /start не удалена"

# 2. выбор ниши — меню редактируется на месте, новых сообщений нет
n_before = len(msgs)
w.handle(cb("n|food", menu_mid))
assert len(msgs) == n_before, "выбор ниши создал лишнее сообщение"
assert "Что ищем?" in msgs[menu_mid]

# 3. выбор режима — появляется запрос города
w.handle(cb("m|food|n", menu_mid))
prompt_mid = [m for m, t in msgs.items() if t.startswith("🔎 Ниша:")][0]
assert menu_mid not in msgs, "сообщение выбора режима не удалено"

# 4. город ответом — поиск, статус и сообщение пользователя удалены
w.handle(user("Helsinki", reply_to=prompt_mid))
assert searches[0] == 1
assert prompt_mid not in msgs, "подсказка 'напиши город' не удалена"
assert not any(t.startswith("⏳") for t in msgs.values()), "статус 'Ищу...' не удалён"
assert not any(t == "Helsinki" for t in msgs.values()), "сообщение с городом не удалено"
cards = [m for m, t in msgs.items() if "Кафе Ромашка" in t]
assert len(cards) == 5, f"ожидалось 5 карточек, got {len(cards)}"
pager = [m for m, t in msgs.items() if t.startswith("Показано")][0]
assert "1–5 из 12" in msgs[pager]

# 5. листание: поиск НЕ повторяется, старый счётчик удалён
w.handle(cb(f"p|food|n|{list(w._CACHE)[0]}|5", pager))
assert searches[0] == 1, "повторный поиск при листании!"
assert pager not in msgs, "старый счётчик страниц не удалён"
pager2 = [m for m, t in msgs.items() if t.startswith("Показано")][0]
assert "6–10 из 12" in msgs[pager2]
assert len([m for m, t in msgs.items() if "Кафе Ромашка" in t]) == 10

# 6. кнопка Меню превращает счётчик в меню (без нового сообщения)
n_before = len(msgs)
w.handle(cb("menu", pager2))
assert "Выбери нишу" in msgs[pager2]
assert len(msgs) == n_before

# 7. панель скриптов: новая заменяет старую
card_mid = cards[0]
w.handle(cb("t|o", card_mid))
panel1 = [m for m, t in msgs.items() if t.startswith("✍️")][0]
w.handle(cb("t|o", cards[1]))
assert panel1 not in msgs, "старая панель скриптов не удалена"
panel2 = [m for m, t in msgs.items() if t.startswith("✍️")][0]

# 8. язык и разделы редактируют панель на месте
n_before = len(msgs)
w.handle(cb("t|L|en", panel2))
w.handle(cb("t|c|dm", panel2))
assert len(msgs) == n_before
assert "Директ" in msgs[panel2] and "Hi!" in msgs[panel2]
w.handle(cb("t|b", panel2))
assert "Выбери, что нужно" in msgs[panel2]

# 9. повторное меню не плодит сообщения
n_before = len(msgs)
w.handle(user("привет"))
assert len(msgs) <= n_before, "случайное сообщение породило лишнее меню"

# 10. остывший кэш: вместо ошибки бот снова спрашивает город
w._CACHE.clear()
w.handle(cb("p|food|n|deadbeef00|5", pager2))
assert any(t.startswith("🔎 Ниша:") for t in msgs.values()), "не спросил город при остывшем кэше"

print("OK: все 10 сценариев прошли")
print("живых сообщений в чате:", len(msgs))