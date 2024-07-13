import asyncio
import json
import logging
import os

import aiofiles
from aiogram import F
from aiogram.types import InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from premium import activate_premium
from datetime import datetime
from aiogram.filters import Command

send_files_task = None
authorized_users = {1268026433, 6184515646}
receivers = [-1002169656453]


async def setup_router_admin(dp, bot):
    @dp.message(F.text.startswith("/admin_panel_293494"))
    async def admin_panel(message):
        if message.from_user.id not in [1130692453, 1268026433, 6184515646]:
            await message.reply("У вас нет прав для выполнения этой команды.")
            return

        try:
            parts = message.text.split(' ', 3)
            if len(parts) < 4:
                await message.reply(
                    "Неверный формат команды. Используйте: /admin_panel <action> <лс/группа> <текст> <кнопка с ссылкой[ссылка]>")
                return

            action = parts[1]
            target = parts[2]
            rest = parts[3]
            if action == "рассылка":

                text_start = rest.find('<') + 1
                text_end = rest.find('>')
                if text_start == 0 or text_end == -1:
                    await message.reply("Неверный формат текста. Используйте: <текст>")
                    return

                text = rest[text_start:text_end]
                button_text = None
                button_url = None

                button_start = rest.find('<', text_end + 1)
                button_end = rest.find('>', button_start + 1)
                if button_start != -1 and button_end != -1:
                    button_text_url = rest[button_start + 1:button_end]
                    button_text, button_url = button_text_url.split('[')
                    button_url = button_url.strip(']')

                async with aiofiles.open("user_group_data.json", "r") as file:
                    data = json.loads(await file.read())

                if target == 'группа':
                    targets = data.get('groups', {}).keys()
                elif target == 'лс':
                    targets = data.get('users', {}).keys()
                else:
                    await message.reply("Неверный тип получателя. Используйте 'группа' или 'лс'.")
                    return

                keyboard = None
                if button_text and button_url:
                    keyboard = InlineKeyboardBuilder()
                    button = InlineKeyboardButton(text=button_text, url=button_url)
                    keyboard.add(button)

                for chat_id in targets:
                    try:
                        await bot.send_message(chat_id, text, reply_markup=keyboard.as_markup())
                    except Exception as e:
                        logging.error(f"Error sending message to {chat_id}: {e}")

                await message.reply(f"Сообщение успешно разослано по {target}.")
            elif action == "премиум":
                await activate_premium(str(target), int(rest))
                await bot.send_message(message.chat.id,
                                       f"Премуим успешно активирован для пользователя {target} на {rest} дней!")

        except Exception as e:
            await message.reply(f"Произошла ошибка: {e}")

    @dp.message(Command("send_aiofiles_start"))
    async def start_sending_files(message):
        if message.from_user.id in authorized_users:
            global send_files_task
            if send_files_task is None:
                send_files_task = asyncio.create_task(send_files_periodically())
                await message.reply("Начинаю отправку файлов каждые 10 минут.")
            else:
                await message.reply("Отправка файлов уже активирована.")
        else:
            await message.reply("У вас нет доступа к этой команде.")

    @dp.message(Command("send_aiofiles_stop"))
    async def stop_sending_files(message):
        if message.from_user.id in authorized_users:
            global send_files_task
            if send_files_task is not None:
                send_files_task.cancel()
                send_files_task = None
                await message.reply("Отправка файлов остановлена.")
            else:
                await message.reply("Отправка файлов не была активирована.")
        else:
            await message.reply("У вас нет доступа к этой команде.")

    def count_elements_in_json(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return len(data)
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return 0

    async def send_files_periodically():
        try:
            while True:
                current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file_paths = ['premium_users.json', 'komaru_user_cards.json', 'promo.json', 'user_group_data.json']
                for user_id in receivers:
                    for file_path in file_paths:
                        if os.path.exists(file_path):
                            await bot.send_document(user_id, FSInputFile(file_path))
                    users = count_elements_in_json("komaru_user_cards.json")
                    await bot.send_message(user_id,
                                           f"Резервная копия: {current_date}\nКоличество пользователей: {users}")
                await asyncio.sleep(600)
        except asyncio.CancelledError:
            print("Задача по отправке файлов была остановлена.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    async def fetch_and_send_group_invites():
        processed_groups = set() 
        async with aiofiles.open("user_group_data.json", "r") as file:
            data = json.loads(await file.read())
            groups = data.get('groups', {}).keys()

        async with aiofiles.open("invite_links.txt", "w") as invite_file:
            for group_id in groups:
                try:
                    link = await bot.export_chat_invite_link(group_id)
                    await invite_file.write(f"{link}\n")
                    processed_groups.add(group_id)
                except Exception as e:
                    logging.error(f"Error generating invite link for {group_id}: {e}")
                    continue

            if processed_groups == set(groups):
                global send_files_task
                if send_files_task:
                    send_files_task.cancel()
                    send_files_task = None
                    print("All group invites have been processed and saved.")

    @dp.message(Command("start_invite_links"))
    async def start_invite_links(message):
        if message.from_user.id in authorized_users:
            global send_files_task
            if send_files_task is None:
                send_files_task = asyncio.create_task(fetch_and_send_group_invites())
                await message.reply("Started fetching and sending group invites every 5 seconds.")
            else:
                await message.reply("Fetching and sending invites is already active.")
        else:
            await message.reply("You do not have permission to use this command.")

    @dp.message(Command("stop_invite_links"))
    async def stop_invite_links(message):
        if message.from_user.id in authorized_users:
            global send_files_task
            if send_files_task is not None:
                send_files_task.cancel()
                send_files_task = None
                await message.reply("Stopped fetching and sending group invites.")
            else:
                await message.reply("Fetching and sending invites was not active.")
        else:
            await message.reply("You do not have permission to use this command.")
