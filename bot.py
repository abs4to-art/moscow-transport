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
print(f"Группа: {group_info['screen_name']} (ID: {GROUP_ID})", flush=True)

longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

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

print("Бот запущен, ожидание сообщений...", flush=True)
for event in longpoll.listen():
    print(f"Получено событие: type={event.type}", flush=True)

    if event.type == VkBotEventType.MESSAGE_NEW:
        try:
            msg = event.obj.message
            text = msg.get("text", "").strip()
            peer_id = msg["from_id"]
            print(f"Сообщение от {peer_id}: {text}", flush=True)

            section = find_section(text)
            if section:
                send(peer_id, DATA[section]["text"], section)
            else:
                send(peer_id, DATA["start"]["text"], "start")

            print(f"Ответ отправлен {peer_id}", flush=True)
        except Exception as e:
            print(f"Ошибка: {e}", flush=True)
    else:
        print(f"Игнорируем событие: {event.type}", flush=True)
