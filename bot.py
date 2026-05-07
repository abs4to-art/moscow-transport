import os
import sys
import json
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from data import DATA, find_section

TOKEN = os.getenv("VK_TOKEN")
if not TOKEN:
    print("Ошибка: VK_TOKEN не задан!", flush=True)
    sys.exit(1)

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

group_info = vk.groups.getById()[0]
GROUP_ID = group_info["id"]
print(f"Группа ID: {GROUP_ID}", flush=True)

def make_keyboard(section):
    items = DATA[section]["buttons"]
    buttons = []
    for label in items:
        buttons.append([{
            "action": {"type": "text", "label": label},
            "color": "primary"
        }])
    return json.dumps({"inline": False, "buttons": buttons}, ensure_ascii=False)

def send(peer_id, text, section):
    vk.messages.send(
        peer_id=peer_id,
        message=text,
        keyboard=make_keyboard(section),
        random_id=0
    )

print("Подключаюсь к LongPoll...", flush=True)
lp = VkBotLongPoll(vk_session, GROUP_ID)
print("LongPoll подключён", flush=True)

for event in lp.listen():
    print(f"Событие: {event.type}", flush=True)
    try:
        obj = event.object if hasattr(event, 'object') else event.obj
        msg = obj.get("message", obj)
        if not isinstance(msg, dict):
            print(f"Неизвестный формат: {msg}", flush=True)
            continue

        text = msg.get("text", "").strip()
        peer_id = msg.get("peer_id") or msg.get("from_id")
        print(f"Текст: {text} от {peer_id}", flush=True)

        section = find_section(text)
        send(peer_id, DATA[section]["text"] if section else DATA["start"]["text"], section or "start")
        print("Ответ отправлен", flush=True)
    except Exception as e:
        print(f"Ошибка: {e}", flush=True)
