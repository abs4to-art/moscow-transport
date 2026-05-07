import os
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from data import DATA

TOKEN = os.getenv("VK_TOKEN")

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, vk.group_id)

def make_keyboard(section="start"):
    items = DATA[section]["buttons"]
    buttons = []
    for label in items:
        buttons.append([{"action": {"type": "text", "label": label}, "color": "primary"}])
    import json
    return json.dumps({"inline": False, "buttons": buttons}, ensure_ascii=False)

def send_msg(peer_id, text, section="start"):
    vk.messages.send(
        peer_id=peer_id,
        message=text,
        keyboard=make_keyboard(section),
        random_id=0
    )

print("Бот запущен...")
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.obj.message
        text = msg.get("text", "").strip()
        peer_id = msg["peer_id"]

        if text in ("Начать", "Старт", ""):
            send_msg(peer_id, DATA["start"]["text"], "start")
        elif text == "Назад":
            send_msg(peer_id, DATA["start"]["text"], "start")
        elif text in DATA:
            send_msg(peer_id, DATA[text]["text"], text)
        else:
            send_msg(peer_id, DATA["start"]["text"], "start")
