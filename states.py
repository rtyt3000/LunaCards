import time

user_button = {}
last_request_time = {}


async def last_time_usage(user_id):
    current_time = time.time()
    if user_id in last_request_time and (current_time - last_request_time[user_id]) < 2:
        return False
    last_request_time[user_id] = current_time
    return True


async def get_titul(card_count, user_id):
    if user_id in [1130692453, 1268026433, 6184515646]:
        return "Создатель"
    if user_id in [1497833411, 6679727618, 5872877426]:
        return "Лох"
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
