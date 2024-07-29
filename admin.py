import asyncio
import json
import logging
from datetime import datetime, timedelta

import aiofiles
from aiogram import F
from aiogram.types import InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from premium import activate_premium
import os

send_files_task = None
authorized_users = {1268026433, 6184515646}
receivers = [-1002169656453]


async def collect_season_data(message):
    try:
        async with aiofiles.open("komaru_user_cards.json", "r+") as file:
            data = json.loads(await file.read())

            for user_id, user_data in data.items():
                user_data['cats'] = []
                user_data['last_usage'] = 1
                user_data['points'] = 0

            await file.seek(0)
            await file.write(json.dumps(data, ensure_ascii=False, indent=4))
            await file.truncate()

        await message.reply("Данные сезона успешно собраны и обновлены.")
    except Exception as e:
        logging.error(f"Ошибка при сборе данных сезона: {e}")
        await message.reply(f"Произошла ошибка при сборе данных сезона: {e}")


async def setup_router_admin(dp, bot):
    @dp.message(F.text.startswith("/admin_panel_293494"))
    async def admin_panel(message):
        if message.from_user.id not in authorized_users:
            await message.reply("У вас нет прав для выполнения этой команды.")
            return

        try:
            parts = message.text.split(' ', 3)
            if len(parts) < 4:
                await message.reply(
                    "Неверный формат команды. Используйте: /admin_panel <action> <лс/группа/user_id> <текст> <кнопка с ссылкой[ссылка]>")
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
            elif action == "смена_ника":
                await change_nickname(target, rest)
                await message.reply(f"Никнейм для пользователя {target} успешно изменен на {rest}.")
            elif action == "бан_юзер":
                if rest == "навсегда":
                    await ban_user(target, forever=True)
                    await message.reply(f"Пользователь {target} забанен навсегда.")
                else:
                    await ban_user(target, int(rest))
                    await message.reply(f"Пользователь {target} забанен на {rest} дней.")
            elif action == "анбан_юзер":
                await unban_user(target)
                await message.reply(f"Пользователь {target} разбанен.")
            elif action == "сброс":
                target = parts[2]
                password = parts[3]
                if target == "сезона":
                    if password == "sfduygshfihdiufgishdhif":
                        await collect_season_data(message)
                        await message.reply("Сезон обнулен")
                else:
                    await message.reply("Неверный поддействие команды. Используйте: сезона Siberia100")

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

    async def count_users_and_groups(file_path: str):
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            contents = await file.read()
            data = json.loads(contents)
    
        num_users = len(data['users'])
        num_groups = len(data['groups'])
    
        return f"Количество лс: {num_users}\nКоличество групп: {num_groups}"

    async def count_elements_in_json(file_path: str):
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                contents = await file.read()
                data = json.loads(contents)
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
                        else:
                            logging.error(f"File not found: {file_path}")
                    users = await count_elements_in_json("komaru_user_cards.json")
                    users_ang_groups = await count_users_and_groups("user_group_data.json")
                    await bot.send_message(user_id,
                                           f"Резервная копия: {current_date}\nКоличество пользователей: {users}\n{users_ang_groups}")
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
                    for user_id in receivers:
                        await bot.send_message(user_id, f"группа добавлена")
                except Exception as e:
                    for user_id in receivers:
                        await bot.send_message(user_id, f"ошибка при записи.")
                    logging.error(f"Error generating invite link for {group_id}: {e}")
                    continue

            if processed_groups == set(groups):
                global send_files_task
                if send_files_task:
                    send_files_task.cancel()
                    send_files_task = None
                    for user_id in receivers:
                        await bot.send_message(user_id, f"All group invites have been processed and saved.")
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

async def change_nickname(user_id, new_nickname):
    async with aiofiles.open("komaru_user_cards.json", "r+") as file:
        data = json.loads(await file.read())
        user_id = str(user_id)
        if user_id in data:
            data[user_id]['nickname'] = new_nickname
            await file.seek(0)
            await file.write(json.dumps(data, ensure_ascii=False, indent=4))
            await file.truncate()
        else:
            logging.error(f"User ID {user_id} not found in the data.")

async def ban_user(user_id, ban_duration_days=None, forever=False):
    async with aiofiles.open("banned_users.json", "r+") as file:
        try:
            data = json.loads(await file.read())
        except json.JSONDecodeError:
            data = {}
        
        user_id = str(user_id)
        if forever:
            ban_end_date = "forever"
        else:
            ban_end_date = (datetime.now() + timedelta(days=ban_duration_days)).strftime('%Y-%m-%d')
        data[user_id] = {"ban_end_date": ban_end_date}
        
        await file.seek(0)
        await file.write(json.dumps(data, ensure_ascii=False, indent=4))
        await file.truncate()

async def unban_user(user_id):
    async with aiofiles.open("banned_users.json", "r+") as file:
        try:
            data = json.loads(await file.read())
        except json.JSONDecodeError:
            return
        
        user_id = str(user_id)
        if user_id in data:
            del data[user_id]
        
        await file.seek(0)
        await file.write(json.dumps(data, ensure_ascii=False, indent=4))
        await file.truncate()

async def check_ban_status(user_id):
    async with aiofiles.open("banned_users.json", "r+") as file:
        try:
            data = json.loads(await file.read())
        except json.JSONDecodeError:
            return False
        
        user_id = str(user_id)
        if user_id in data:
            ban_end_date = data[user_id]['ban_end_date']
            if ban_end_date == "forever":
                return False
            ban_end_date = datetime.strptime(ban_end_date, '%Y-%m-%d')
            if datetime.now() >= ban_end_date:
                del data[user_id]
                await file.seek(0)
                await file.write(json.dumps(data, ensure_ascii=False, indent=4))
                await file.truncate()
                return True
            else:
                return False
        else:
            return False
