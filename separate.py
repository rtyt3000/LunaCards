import json
import os
import aiofiles

async def separate_users_data():
    try:
        os.makedirs('users', exist_ok=True)
        async with aiofiles.open('komaru_user_cards.json', mode='r', encoding='utf-8') as file:
            data = json.loads(await file.read())
            for user_id, user_data in data.items():
                user_filename = f'users/{user_id}_cards.json'
                async with aiofiles.open(user_filename, mode='w', encoding='utf-8') as user_file:
                    await user_file.write(json.dumps(user_data, ensure_ascii=False, indent=4))
        print("Data has been separated successfully.")
    except Exception as e:
        print(f"An error occurred while separating data: {e}")

import asyncio
asyncio.run(separate_users_data())