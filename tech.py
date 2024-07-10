import asyncio
import json
import telebot
from telebot.async_telebot import AsyncTeleBot

config = {}
def get_config():
    with open('config.json', 'r') as file:
        global config
        config = json.loads(file.read())

bot = AsyncTeleBot(config['tech_bot_api_key'])


async def start_with(message, array):
    for i in array:
        if message.startswith(i):
            return True
    return False


@bot.message_handler(func=lambda message: True)
async def handle_text(message):
    try:
        text = message.text.lower()
        if text in config["commands"] or start_with(text, config["startwith_commands"]):
            await bot.reply_to(message, config['tech_text'])
    except Exception as e:
        await bot.send_message(message.chat.id, "Временная ошибка в обработке, повторите позже.")
        for i in config['allowed_users']:
            await bot.send_message(i,
                               f"Произошла ошибка при обработке команды: в чате: {message.chat.id}. Ошибка: {e}")


async def main():
    await bot.infinity_polling(timeout=10, request_timeout=120)


if __name__ == "__main__":
    asyncio.run(main())
