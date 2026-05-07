import os
import sys
import json
import time
import requests
import vk_api
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

# Ручной LongPoll
server = vk.groups.getLongPollServer(group_id=GROUP_ID)
print(f"LongPoll сервер получен: {server['server']}", flush=True)

while True:
    try:
        srv = server["server"]
        if not srv.startswith("http"):
            srv = f"https://{srv}"
        response = requests.post(srv,
            data={
                "act": "a_check",
                "key": server["key"],
                "ts": server["ts"],
                "wait": 25
            },
            timeout=30
        ).json()

        if "ts" in response:
            server["ts"] = response["ts"]

        if "updates" not in response or not response["updates"]:
            continue

        for update in response["updates"]:
            print(f"Обновление: type={update.get('type')}", flush=True)

            if update.get("type") == "message_new":
                msg = update.get("object", {}).get("message", {})
                text = msg.get("text", "").strip()
                peer_id = msg.get("peer_id") or msg.get("from_id")
                print(f"Сообщение от {peer_id}: {text}", flush=True)

                section = find_section(text)
                if section:
                    send(peer_id, DATA[section]["text"], section)
                else:
                    send(peer_id, DATA["start"]["text"], "start")

                print(f"Ответ отправлен {peer_id}", flush=True)

    except Exception as e:
        print(f"Ошибка: {e}", flush=True)
        time.sleep(3)
        try:
            server = vk.groups.getLongPollServer(group_id=GROUP_ID)
        except:
            pass
