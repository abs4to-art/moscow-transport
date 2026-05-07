import os
import sys
import json
import time
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
GROUP_NAME = group_info["screen_name"]
print(f"Группа: @{GROUP_NAME} (ID: {GROUP_ID})", flush=True)

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

try:
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    print("LongPoll подключён успешно", flush=True)
except Exception as e:
    print(f"Ошибка LongPoll: {e}", flush=True)
    sys.exit(1)

print("Бот работает. Напишите сообщение в группу ВК.", flush=True)

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        try:
            msg = event.obj.get("message", event.obj)
            text = msg.get("text", "").strip()
            peer_id = msg.get("peer_id", msg.get("from_id"))
            print(f"[{peer_id}] {text}", flush=True)

            section = find_section(text)
            if not section:
                section = "start"
            send(peer_id, DATA[section]["text"], section)
        except Exception as e:
            print(f"Ошибка обработки: {e}", flush=True)
            import traceback
            traceback.print_exc()
    else:
        print(f"Пропуск: {event.type}", flush=True)
