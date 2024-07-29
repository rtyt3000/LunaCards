import json
import aiofiles
import logging

async def collect_season_data():
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

        print("Данные сезона успешно собраны и обновлены.")
    except Exception as e:
        logging.error(f"Ошибка при сборе данных сезона: {e}")
        print(f"Произошла ошибка при сборе данных сезона: {e}")

import asyncio
asyncio.run(collect_season_data())
