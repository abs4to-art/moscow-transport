import os
import json
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from data import DATA, find_section

TOKEN = os.getenv("VK_TOKEN")

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, vk.group_id)

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

print("Бот запущен...")
for event in longpoll.listen():
    if event.type != VkBotEventType.MESSAGE_NEW:
        continue

    msg = event.obj.message
    text = msg.get("text", "").strip()
    peer_id = msg["peer_id"]

    section = find_section(text)
    if section:
        send(peer_id, DATA[section]["text"], section)
    else:
        send(peer_id, DATA["start"]["text"], "start")
