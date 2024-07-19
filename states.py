import time

user_button = {}
last_request_time = {}


async def last_time_usage(user_id):
    current_time = time.time()
    if user_id in last_request_time and (current_time - last_request_time[user_id]) < 2:
        return False
    last_request_time[user_id] = current_time
    return True


async def get_dev_titul(user_id: int) -> str:
    if user_id == 5493956779:
        return "люпими квт рофл"
    elif user_id in [1268026433, 6184515646]:
        return "Создатель"
    else:
        return "как ты вообще сюда попал?"


async def get_titul(card_count):
    if card_count > 500:
        return "Мастер карточек"
    elif card_count > 250:
        return "Коллекционер"
    elif card_count > 150:
        return 'Эксперт карточек'
    elif card_count > 100:
        return 'Продвинутый коллекционер'
    elif card_count > 50:
        return 'Любитель Комару'
    elif card_count > 20:
        return 'Начинающий коллекционер'
    else:
        return 'Новичок'
