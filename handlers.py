import logging
import random
import time
from aiogram import types, F, Router
from aiogram.types import Message, InputMediaPhoto
from aiogram.filters import Command
from text import WELCOME_MESSAGE_PRIVATE, WELCOME_MESSAGE, HELP_MESSAGE, responses, PRIVACY_MESSAGE, forbidden_symbols
from kb import start_kb, help_kb, profile_kb, cards_kb, get_card_navigation_keyboard, top_kb, subcribe_keyboard
from premium import check_and_update_premium_status, activate_premium
from db import save_data, load_data_cards, register_user_and_group_async, config_func, read_promo_data, write_promo_data
from states import get_titul, user_button, last_time_usage, get_dev_titul
from premium import send_payment_method_selection
import emoji
import re
from aiogram import html

router = Router()


async def setup_router(dp, bot):
    @router.message(Command("start"))
    async def start_handler(msg: Message):
        if not await last_time_usage(msg.from_user.id):
            return
        await register_user_and_group_async(msg)
        if msg.chat.type == "private":
            markup = await start_kb(msg)
            await msg.answer(WELCOME_MESSAGE_PRIVATE, reply_markup=markup, parse_mode='HTML')
        else:
            await msg.answer(WELCOME_MESSAGE, parse_mode='HTML')

    @router.message(Command("help"))
    async def help_handler(msg: Message):
        if not await last_time_usage(msg.from_user.id):
            return
        markup = await help_kb(msg)
        await msg.answer(HELP_MESSAGE, reply_markup=markup, parse_mode='HTML')

    @router.message(Command("privacy"))
    async def privacy_handler(msg: Message):
        if not await last_time_usage(msg.from_user.id):
            return
        markup = await help_kb(msg)
        await msg.answer(PRIVACY_MESSAGE, reply_markup=markup)

    @router.message(F.text.casefold().in_(["комару".casefold(), "карту, сэр".casefold(), "карту сэр".casefold(), "карту, сэр.".casefold(), "камар".casefold(), "камару".casefold(), "получить карту".casefold()]))
    async def komaru_cards_function(msg: Message):
        if not await last_time_usage(msg.from_user.id):
            return
        user_id = str(msg.from_user.id)
        user_nickname = msg.from_user.first_name
        await register_user_and_group_async(msg)
        config_data = await config_func()
        cats = config_data['cats']

        data = await load_data_cards()
        user_data = data.get(user_id,
                             {'cats': [], 'last_usage': 0, 'points': 0, 'nickname': user_nickname, 'card_count': 0,
                              'all_points': 0})

        if 'card_count' not in user_data:
            user_data['card_count'] = 0

        if 'all_points' not in user_data:
            user_data['all_points'] = 0

        user_data['points'] = int(user_data['points'])
        time_since_last_usage = time.time() - user_data['last_usage']

        premium_status, _ = await check_and_update_premium_status(user_id)
        wait_time = 14400 if not premium_status else 10800

        if time_since_last_usage < wait_time:
            remaining_time = wait_time - time_since_last_usage
            remaining_hours = int(remaining_time // 3600)
            remaining_minutes = int((remaining_time % 3600) // 60)
            remaining_seconds = int(remaining_time % 60)
        
            time_parts = []
            if remaining_hours > 0:
                time_parts.append(f"{remaining_hours} часов")
            if remaining_minutes > 0:
                time_parts.append(f"{remaining_minutes} минут")
            if remaining_seconds > 0:
                time_parts.append(f"{remaining_seconds} секунд")
        
            time_string = " ".join(time_parts)
            if not time_string:
                time_string = "меньше минуты"
        
            await msg.reply(
                f"{msg.from_user.first_name}, вы осмотрелись, но не увидели рядом Комару. Попробуйте еще раз через {time_string}.")
            return

        random_number = random.randint(1, 95)
        if premium_status:
            if 0 <= random_number <= 19:
                eligible_cats = [cat for cat in cats if cat["rarity"] == "Легендарная"]
            elif 20 <= random_number <= 34:
                eligible_cats = [cat for cat in cats if cat["rarity"] == "Мифическая"]
        else:
            if 0 <= random_number <= 14:
                eligible_cats = [cat for cat in cats if cat["rarity"] == "Легендарная"]
            elif 15 <= random_number <= 29:
                eligible_cats = [cat for cat in cats если cat["rarity"] == "Мифическая"]

        if 30 <= random_number <= 49:
            eligible_cats = [cat for cat in cats if cat["rarity"] == "Сверхредкая"]
        elif 50 <= random_number <= 95:
            eligible_cats = [cat for cat in cats if cat["rarity"] == "Редкая"]

        if eligible_cats:
            chosen_cat = random.choice(eligible_cats)
            photo_data = chosen_cat['photo']
            if chosen_cat['name'] in user_data['cats']:
                await bot.send_photo(
                    msg.chat.id,
                    photo=photo_data,
                    caption=f"✨{msg.from_user.first_name}, вы осмотрелись вокруг и снова увидели {chosen_cat['name']}! ✨\nБудут начислены только очки.\n\n🎲 Редкость: {chosen_cat['rarity']}\n💯 +{chosen_cat['points']} очков.\n🌟 Всего поинтов: {user_data['points'] + int(chosen_cat['points'])}",
                    reply_to_message_id=msg.message_id
                )
                user_data['points'] += int(chosen_cat['points'])
                user_data['all_points'] += int(chosen_cat['points'])
            else:
                await bot.send_photo(
                    msg.chat.id,
                    photo=photo_data,
                    caption=f"✨{msg.from_user.first_name}, вы осмотрелись вокруг и увидели.. {chosen_cat['name']}! ✨\n\n🎲 Редкость: {chosen_cat['rarity']}\n💯 Очки: {chosen_cat['points']}\n🌟 Всего поинтов: {user_data['points'] + int(chosen_cat['points'])}",
                    reply_to_message_id=msg.message_id
                )
                user_data['cats'].append(chosen_cat['name'])
                user_data['points'] += int(chosen_cat['points'])
                user_data['all_points'] += int(chosen_cat['points'])
                user_data['card_count'] += 1
            user_data['last_usage'] = time.time()
            data[user_id] = user_data

            await write_event.wait()
            write_event.clear()
            await save_data(data)

    @router.message(F.text.casefold().in_(["кпрофиль".casefold(), "профиль".casefold(), "комару профиль".casefold(), "камара профиль".casefold()]) | F.command("profile"))
    async def user_profile(msg: Message):
        if not await last_time_usage(msg.from_user.id):
            return
        await register_user_and_group_async(msg)
        user_id = msg.from_user.id
        first_name = msg.from_user.first_name
        last_name = msg.from_user.last_name or ""
        data = await load_data_cards()
        user_data = data.get(str(user_id),
                             {'cats': [], 'last_usage': 0, 'points': 0, 'nickname': first_name, 'card_count': 0})
        card_count = user_data.get('card_count', 0)
        favorite_card = user_data.get('love_card', 'Не выбрана')
        titul = await get_titul(card_count)
        await register_user_and_group_async(msg)
        config_data = await config_func()
        cats = config_data['cats']
        collected_cards = len(user_data['cats'])
        total_cards = len(cats)
    
        premium_status, premium_expiration = await check_and_update_premium_status(user_id)
        premium_message = f"Премиум: активен до {premium_expiration}" if premium_status else "Премиум: не активен"
    
        if user_id in [6184515646, 1268026433, 5493956779, 1022923020]:
            dev_titul = await get_dev_titul(user_id)
            dev_titul_message = f"🪬 Dev Титул: {dev_titul}"
        else:
            dev_titul_message = ""
    
        try:
            user_profile_photos = await bot.get_user_profile_photos(user_id, limit=1)
            if user_profile_photos.photos:
                photo = user_profile_photos.photos[0][-1]
                file_id = photo.file_id
    
                photo_cache = file_id
            else:
                photo_cache = 'https://tinypic.host/images/2024/07/08/avatar.jpg'
    
            caption = (
                f"Привет {html.bold(html.quote(user_data['nickname']))}!\n\n"
                f"🏡 Твой профиль:\n"
                f"🃏 Собрано {collected_cards} из {total_cards} карточек\n"
                f"💰 Очки: {user_data['points']}\n"
                f"🎖️ Титул: {titul}\n"
                f"💖 Любимая карточка: {favorite_card}\n"
                f"🌟 {premium_message}\n"
                f"<blockquote> {dev_titul_message} </blockquote>\n"
            )
            markup = await profile_kb(msg)
    
            await bot.send_photo(msg.chat.id, photo=photo_cache, caption=caption, reply_markup=markup, parse_mode="HTML")
        except Exception as e:
            if "bot was blocked by the user" in str(e):
                await msg.answer("Пожалуйста, разблокируйте бота для доступа к вашему профилю.")
            else:
                print(e)
                await msg.answer(
                    "Произошла ошибка при доступе к вашему профилю. Попробуйте позже.")

    @router.message(F.text.casefold().startswith("сменить ник".casefold()))
    async def change_nickname(message: types.Message):
        if not await last_time_usage(message.from_user.id):
            return
        user_id = message.from_user.id
        data = await load_data_cards()
        first_name = message.from_user.first_name
        premium_status, _ = await check_and_update_premium_status(str(user_id))
        user_data = data.get(str(user_id),
                             {'cats': [], 'last_usage': 0, 'points': 0, 'nickname': first_name, 'card_count': 0})
        parts = message.text.casefold().split('сменить ник'.casefold(), 1)

        if len(parts) > 1 and parts[1].strip():
            new_nick = parts[1].strip()

            if len(new_nick) > 64:
                await message.reply("Никнейм не может быть длиннее 64 символов.")
                return

            if not premium_status and any(emoji.is_emoji(char) for char in new_nick):
                await message.reply("Вы не можете использовать эмодзи в нике. Приобретите премиум в профиле!")
                return

            if any(entity.type == 'url' for entity in message.entities or []):
                await message.reply("Никнейм не может содержать ссылки.")
                return

            if '@' in new_nick:
                await message.reply("Никнейм не может содержать юзернеймы.")
                return
                
            if not is_nickname_allowed(new_nick):
                await message.reply("Никнейм содержит запрещённые символы или слова.")
                return

            user_data['nickname'] = new_nick
            data[str(user_id)] = user_data
            await save_data(data)
            await message.reply(f"Ваш никнейм был изменен на {new_nick}.")
        else:
            await message.reply("Никнейм не может быть пустым. Укажите значение после команды.")

    @router.message(F.text.casefold().startswith("промо ".casefold()))
    async def promo(message):
        if not await last_time_usage(message.from_user.id):
            return
        try:
            promo_code = message.text[6:]
            promo_data = await read_promo_data("promo.json")

            data = promo_data.get(promo_code)
            if not data:
                return

            user_id = message.from_user.id
            current_time = time.time()
            markup = await subcribe_keyboard()

            if current_time > data['until']:
                await bot.send_message(message.chat.id,
                                       "Срок действия промокода истек. Подпишитесь на канал, чтобы не пропускать новые промо!",
                                       reply_markup=markup)
                return

            if data['activation_limit'] != -1 and data['activation_counts'] >= data['activation_limit']:
                await bot.send_message(message.chat.id,
                                       "Этот промокод уже был активирован максимальное количество раз. Подпишитесь на канал, чтобы не пропускать новые промо!",
                                       reply_markup=markup)
                return

            try:
                chat_member = await bot.get_chat_member('@komaru_updates', user_id)
                if chat_member.status not in ['member', 'administrator', 'creator']:
                    await bot.send_message(message.chat.id,
                                           "Подпишитесь на канал, чтобы получить подарок.",
                                           reply_markup=markup)
                    return
            except Exception as e:
                await bot.send_message(1130692453, f"Произошла ошибка {e}")
                await bot.send_message(1268026433, f"Произошла ошибка {e}")

            if user_id in data['users']:
                await bot.send_message(message.chat.id,
                                       "Вы уже активировали этот промокод. Подпишитесь на канал, чтобы не пропускать новые промо!",
                                       reply_markup=markup)
                return

            action = data['action'].split()
            if action[0] == 'give_prem':
                await activate_premium(user_id, int(action[1]))
                data['users'].append(user_id)
                data["activation_counts"] += 1

                await write_promo_data("promo.json", promo_data)

                await bot.send_message(message.chat.id,
                                       f"Промокод успешно активирован!\n\nВы получили премиум на {int(action[1])} дней!")
            elif action[0] == "kd":
                data_komaru = await load_data_cards()
                if str(user_id) in data_komaru:
                    user_data = data_komaru[str(user_id)]
                    current_time = time.time()
                    premium_status, _ = await check_and_update_premium_status(user_id)
                    wait_time = 10800 if premium_status else 14400

                    time_since_last_usage = current_time - user_data['last_usage']
                    if time_since_last_usage < wait_time:
                        user_data['last_usage'] = 0
                        data_komaru[str(user_id)] = user_data
                        await save_data(data_komaru)
                        logging.info(f"Waiting time for user {user_id} has been reset.")
                        data['users'].append(user_id)
                        data["activation_counts"] += 1

                        await write_promo_data("promo.json", promo_data)

                        await bot.send_message(message.chat.id,
                                               "Промокод успешно активирован!\n\nВы полуили обнуление кд на карточку!")
                    else:
                        await bot.send_message(message.chat.id,
                                               "Пожалуйста откройте сначала карточку, а потом заново активируйте промокод.")
                else:
                    logging.warning(f"User {user_id} not found in the data.")
                    await bot.send_message(message.chat.id,
                                           "Пожалуйста откройте сначала карточку, а потом заново активируйте промокод.")

        except Exception as e:
            logging.error(f"Error processing promo code: {e}")
            await bot.send_message(1130692453, f"Произошла ошибка {e}")
            await bot.send_message(1268026433, f"Произошла ошибка {e}")

    dp.include_router(router)


def is_nickname_allowed(nickname):
    for symbol in forbidden_symbols:
        if re.search(re.escape(symbol), nickname, re.IGNORECASE):
            return False
    return True


"""                                                 КолБэки                                                      """

"""                                                  Карты                                                     """


async def setup_router_2(dp, bot):
    @router.callback_query(F.data.startswith("show_cards"))
    async def show_cards_second(callback: types.CallbackQuery):
        unique_id = str(callback.data.split('_')[-1])
        if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
            await callback.answer(text=random.choice(responses), show_alert=True)
            return

        user_id = str(callback.from_user.id)
        config_data = await config_func()
        cats = config_data['cats']
        user_nickname = callback.from_user.first_name
        data = await load_data_cards()
        user_data = data.get(user_id,
                             {'cats': [], 'last_usage': 0, 'points': 0, 'nickname': user_nickname, 'card_count': 0})
        collected_cards = len(user_data['cats'])
        total_cards = len(cats)

        if user_data['cats']:
            cats_owned_by_user = {cat['name'] for cat in cats if cat['name'] in user_data['cats']}
            rarities = {cat['rarity'] for cat in cats if cat['name'] in cats_owned_by_user}
            markup = await cards_kb(rarities)
            try:
                await bot.send_message(user_id,
                                       f"У вас собрано {collected_cards} из {total_cards} возможных\nВыберите редкость:",
                                       reply_markup=markup)
                if callback.message.chat.type in ["supergroup", "group"]:
                    print(callback.message.chat.type)
                    await bot.send_message(chat_id=callback.message.chat.id,
                                           text=f"{user_nickname}, карточки отправлены вам в личные сообщения!")
                else:
                    pass
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение: {str(e)}")
                await callback.answer("Напишите боту что-то в личные сообщения, чтобы отправить вам карточки!",
                                      show_alert=True)
        else:
            await callback.answer("Вы пока что не наблюдали за птичками.", show_alert=True)

    @router.callback_query(F.data.startswith("show_"))
    async def show_cards(callback: types.CallbackQuery):
        try:
            config_data = await config_func()
            cats = config_data['cats']
            rarity = callback.data[len('show_'):]
            user_id = str(callback.from_user.id)
            user_nickname = callback.from_user.first_name
            data = await load_data_cards()
            user_data = data.get(user_id,
                                 {'cats': [], 'last_usage': 0, 'points': 0, 'nickname': user_nickname, 'card_count': 0})
            rarity_cards = [cat for cat in cats if
                            cat['name'] in user_data['cats'] and cat['rarity'].startswith(rarity)]

            if rarity_cards:
                first_card_index = 0
                await send_initial_card_with_navigation(callback.message.chat.id, user_id, rarity, rarity_cards,
                                                        first_card_index)
            else:
                await callback.message.answer(f"У вас нет карточек редкости {rarity}")
        except Exception as e:
            logging.error(f"Error in show_cards: {e}")
            await callback.message.answer("Произошла ошибка при отображении карточек.")

    async def send_initial_card_with_navigation(chat_id, user_id, rarity, rarity_cards, card_index):
        if card_index < len(rarity_cards):
            card = rarity_cards[card_index]
            photo_data = card['photo']
            caption = f"{card['name']}\nРедкость: {card['rarity']}"
            if 'points' in card:
                caption += f"\nОчки: {card['points']}"

            markup = await get_card_navigation_keyboard(user_id, card_index, rarity, rarity_cards, card["id"])

            await bot.send_photo(chat_id, photo=photo_data, caption=caption, reply_markup=markup)
        else:
            logging.error(f"Card index {card_index} out of range for rarity cards")

    async def send_card_with_navigation(chat_id, message_id, user_id, rarity, rarity_cards, card_index):
        if card_index < len(rarity_cards):
            card = rarity_cards[card_index]
            photo_data = card['photo']
            caption = f"{card['name']}\nРедкость: {card['rarity']}"
            if 'points' in card:
                caption += f"\nОчки: {card['points']}"

            markup = await get_card_navigation_keyboard(user_id, card_index, rarity, rarity_cards, card["id"])

            print("1")
            media = InputMediaPhoto(media=photo_data)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id)
            await bot.edit_message_caption(caption=caption, chat_id=chat_id, message_id=message_id, reply_markup=markup)
            print("3")
        else:
            logging.error(f"Card index {card_index} out of range for rarity cards")

    @router.callback_query(F.data.startswith("love_"))
    async def handle_love_card(callback: types.CallbackQuery):
        parts = callback.data.split('_')
        config_data = await config_func()
        cats = config_data['cats']
        user_id, card_id = parts[1], parts[2]
        data = await load_data_cards()
        user_data = data.get(user_id, {'cats': [], 'last_usage': 0, 'points': 0, 'nickname': '', 'love_card': ''})
        card_name = next((card['name'] for card in cats if card['id'] == card_id), None)
        if card_name:
            user_data['love_card'] = card_name
            data[user_id] = user_data
            await save_data(data)
            await bot.answer_callback_query(callback.id, f"Карточка '{card_name}' теперь ваша любимая!")
        else:
            await bot.answer_callback_query(callback.id, "Не найдено карточек с таким ID.")

    @router.callback_query(F.data.startswith("navigate_"))
    async def navigate_cards(callback: types.CallbackQuery):
        try:
            config_data = await config_func()
            cats = config_data['cats']
            parts = callback.data.split('_')
            user_id = parts[1]
            direction = parts[2]
            new_index = int(parts[3])
            rarity = parts[4]

            logging.debug(f"User ID: {user_id}, Direction: {direction}, New Index: {new_index}, Rarity: {rarity}")

            data = await load_data_cards()
            user_data = data.get(user_id, {'cats': [], 'last_usage': 0, 'points': 0, 'nickname': ''})
            rarity_cards = [cat for cat in cats if
                            cat['name'] in user_data['cats'] and cat['rarity'].startswith(rarity)]

            logging.info(f"Navigating to card {new_index} of {len(rarity_cards) - 1}")

            if 0 <= new_index < len(rarity_cards):
                await send_card_with_navigation(callback.message.chat.id, callback.message.message_id, user_id, rarity,
                                                rarity_cards, new_index)
            else:
                await callback.message.answer("Индекс карточки вне диапазона.")
        except Exception as e:
            logging.error(f"Error in navigate_cards: {str(e)}")
            await callback.message.answer("Произошла ошибка при навигации по карточкам.")


"""                                               Топ карточек                                                   """


async def setup_router_3(dp, bot):
    @router.callback_query(F.data.startswith("top_komaru"))
    async def top_komaru(callback: types.CallbackQuery):
        unique_id = str(callback.data.split('_')[-1])
        if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
            await callback.answer(random.choice(responses), show_alert=True)
            return
        markup = await top_kb(callback, "all_top")
        await callback.message.answer(
            text="Топ 10 пользователей по карточкам. Выберите кнопку:",
            reply_markup=markup)

    @router.callback_query(F.data.startswith("top_cards_"))
    async def cards_top_callback(callback: types.CallbackQuery):
        parts = callback.data.split('_')
        choice = parts[2]
        unique_id = str(parts[-1])

        if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
            await callback.answer(random.choice(responses), show_alert=True)
            return

        data = await load_data_cards()
        user_id = str(callback.from_user.id)
        user_data = data.get(user_id, {'cats': [], 'points': 0, 'all_points': 0})
        message_text = ""

        if choice == "cards":
            sorted_data = sorted(data.items(), key=lambda x: len(x[1].get('cats', [])), reverse=True)
            user_rank = next((i for i, item in enumerate(sorted_data, 1) if item[0] == user_id), None)
            top_10 = sorted_data[:10]

            message_text = "🏆 Топ-10 пользователей по количеству собранных карточек:\n\n"
            for i, (uid, u_data) in enumerate(top_10, 1):
                nickname = u_data.get('nickname', 'Unknown')
                num_cards = len(u_data.get('cats', []))
                premium_status, _ = await check_and_update_premium_status(uid)
                premium_icon = "💎" if premium_status else ""
                message_text += f"{i}. {premium_icon} {nickname}: {num_cards} карточек\n"

            if user_rank and user_rank > 10:
                message_text += f"\nВаше место: {user_rank} ({data[user_id]['nickname']}: {len(user_data['cats'])} карточек)"

            markup = await top_kb(callback, "cards")

        elif choice == "point":
            sorted_data_points = sorted(data.items(), key=lambda x: x[1].get('points', 0), reverse=True)
            user_rank_points = next((j for j, item in enumerate(sorted_data_points, 1) if item[0] == user_id), None)
            top_10 = sorted_data_points[:10]

            message_text = "🏆 Топ-10 пользователей по количеству набранных очков:\n\n"
            for j, (uid, u_data) in enumerate(top_10, 1):
                nickname_2 = u_data.get('nickname', 'Unknown')
                points = u_data.get('points', 0)
                premium_status, _ = await check_and_update_premium_status(uid)
                premium_icon = "💎" if premium_status else ""
                message_text += f"{j}. {premium_icon} {nickname_2}: {points} очков\n"

            if user_rank_points and user_rank_points > 10:
                message_text += f"\nВаше место: {user_rank_points} ({data[user_id]['nickname']}: {user_data['points']} очков)"

            markup = await top_kb(callback, "point")

        elif choice == "all":
            sorted_data = sorted(data.items(), key=lambda x: x[1].get('all_points', 0), reverse=True)
            user_rank_all = next((index for index, item in enumerate(sorted_data, 1) if item[0] == user_id), None)
            top_10 = sorted_data[:10]

            message_text = "🏆 Топ-10 пользователей по всем временам (очки):\n\n"
            for index, (uid, u_data) in enumerate(top_10, 1):
                nickname = u_data.get('nickname', 'Unknown')
                premium_status, _ = await check_and_update_premium_status(uid)
                premium_icon = "💎" if premium_status else ""
                total_points = u_data.get('all_points', 0)
                message_text += f"{index}. {premium_icon} {nickname}: {total_points} очков\n"

            if user_rank_all and user_rank_all > 10:
                message_text += f"\nВаше место: {user_rank_all} ({data[user_id]['nickname']}: {user_data['all_points']} очков)"

            markup = await top_kb(callback, "all")

        if not message_text:
            message_text = "Не удалось получить данные. Попробуйте позже."

        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text=message_text,
                                    reply_markup=markup)


"""                                                  Премиум                                                   """


@router.callback_query(F.data.startswith("premium_callback"))
async def handler_premium(callback: types.CallbackQuery):
    unique_id = callback.data.split('_')[-1]
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(random.choice(responses), show_alert=True)
        return

    try:
        await send_payment_method_selection(callback, callback.from_user.id, unique_id)
        if callback.message.chat.type != "private":
            await callback.message.answer(
                f"{str(callback.from_user.first_name)}, информация о способах оплаты отправлена вам в личные сообщения.")
    except Exception as e:
        print(e)
        await callback.answer("Пожалуйста, напишите боту что-то в личные сообщения, чтобы я смог отправить информацию.",
                              show_alert=True)
