import os
from vkbottle import Bot, Message
from vkbottle.bot import Message
from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback
from data import DATA

TOKEN = os.getenv("VK_TOKEN")
bot = Bot(TOKEN)

def get_keyboard(section="start"):
    items = DATA[section]["buttons"]
    keyboard = Keyboard()
    for i, label in enumerate(items):
        keyboard.add(Text(label))
        if i < len(items) - 1:
            keyboard.row()
    return keyboard

@bot.on.message(text="Начать")
@bot.on.message(text="Старт")
@bot.on.message(payload={"cmd": "start"})
async def start_handler(message: Message):
    data = DATA["start"]
    keyboard = get_keyboard("start")
    await message.answer(data["text"], keyboard=keyboard)

@bot.on.message(text=DATA["start"]["buttons"])
async def menu_handler(message: Message):
    section = message.text
    if section in DATA:
        data = DATA[section]
        keyboard = get_keyboard(section)
        await message.answer(data["text"], keyboard=keyboard)

@bot.on.message(text="Назад")
async def back_handler(message: Message):
    data = DATA["start"]
    keyboard = get_keyboard("start")
    await message.answer(data["text"], keyboard=keyboard)

@bot.on.message()
async def any_message(message: Message):
    data = DATA["start"]
    keyboard = get_keyboard("start")
    await message.answer("Пожалуйста, воспользуйтесь кнопками меню.", keyboard=keyboard)

if __name__ == "__main__":
    bot.run_forever()
