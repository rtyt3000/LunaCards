import json
import logging
import os
import asyncio
import aiofiles
config_lock = asyncio.Lock()
data_lock = asyncio.Lock()
user_group_lock = asyncio.Lock()
promo_lock = asyncio.Lock()
for filename in ["premium_users.json", "komaru_user_cards.json"]:
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)



async def config_func():
    async with config_lock:
        async with aiofiles.open('config.json', 'r', encoding='utf-8') as file:
            data = json.loads(await file.read())
        return data


os.makedirs('users', exist_ok=True)

async def save_user_data(user_id, data):
    try:
        file_path = f'users/{user_id}_cards.json'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
            await file.write(json.dumps(data, ensure_ascii=False, indent=4))
    except Exception as e:
        print(f"Failed to save data for user {user_id}: {e}")

async def load_user_data(user_id):
    try:
        file_path = f'users/{user_id}_cards.json'
        if not os.path.exists(file_path):
            return {} 
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            data = json.loads(await file.read())
        return data
    except Exception as e:
        print(f"Failed to load data for user {user_id}: {e}")
        return {}
        
async def load_all_user_data():
    user_data_directory = "users"  # Укажите путь к директории
    all_user_data = {}
    
    for filename in os.listdir(user_data_directory):
        if filename.endswith("_cards.json"):
            user_id = filename.split('_')[0]
            async with aiofiles.open(os.path.join(user_data_directory, filename), 'r') as file:
                data = await file.read()
                all_user_data[user_id] = json.loads(data)
                
    return all_user_data


async def register_user_and_group_async(message):
    chat_type = message.chat.type
    update_data = {}
    if chat_type == 'private':
        user_info = {
            "user_id": message.from_user.id,
            "username": message.from_user.username or "",
            "first_name": message.from_user.first_name or ""
        }
        user_key = str(message.from_user.id)
        update_data['users'] = {user_key: user_info}
    if chat_type in ['group', 'supergroup']:
        group_info = {
            "group_id": message.chat.id,
            "title": message.chat.title
        }
        group_key = str(message.chat.id)
        update_data['groups'] = {group_key: group_info}
    async with user_group_lock:
        try:
            async with aiofiles.open("user_group_data.json", "r") as file:
                data = await file.read()
                data = json.loads(data)
        except FileNotFoundError:
            data = {"users": {}, "groups": {}}
        updated = False
        for section, items in update_data.items():
            for key, info in items.items():
                if key not in data[section]:
                    data[section][key] = info
                    updated = True
        if updated:
            async with aiofiles.open("user_group_data.json", "w") as file:
                await file.write(json.dumps(data, indent=4))


async def read_promo_data(filename):
    async with promo_lock:
        async with aiofiles.open(filename, 'r') as f:
            data = await f.read()
            return json.loads(data)


async def write_promo_data(filename, data):
    async with promo_lock:
        async with aiofiles.open(filename, 'w') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=4))
