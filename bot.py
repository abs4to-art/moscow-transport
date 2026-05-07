import os
import sys
import json
from flask import Flask, request
import vk_api
from data import DATA, find_section

TOKEN = os.getenv("VK_TOKEN")
if not TOKEN:
    print("Ошибка: VK_TOKEN не задан!", flush=True)
    sys.exit(1)

CONFIRM_CODE = os.getenv("CONFIRM_CODE", "")

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

group_info = vk.groups.getById()[0]
GROUP_ID = group_info["id"]
print(f"Группа: @{group_info['screen_name']} (ID: {GROUP_ID})", flush=True)

app = Flask(__name__)

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

@app.route("/", methods=["POST"])
def callback():
    data = request.get_json(force=True)
    print(f"Callback: {data.get('type')}", flush=True)

    if data.get("type") == "confirmation":
        return CONFIRM_CODE, 200

    if data.get("type") == "message_new":
        msg = data.get("object", {}).get("message", {})
        text = msg.get("text", "").strip()
        peer_id = msg.get("peer_id") or msg.get("from_id")
        print(f"[{peer_id}] {text}", flush=True)

        section = find_section(text) or "start"
        send(peer_id, DATA[section]["text"], section)

    return "ok", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
