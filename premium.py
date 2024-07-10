import json
import logging
import random
from datetime import datetime, timedelta
import aiofiles
from aiogram import F, types
from aiogram.types import LabeledPrice, Message

import config
from states import user_button
from kb import premium_keyboard, payment_keyboard, payment_crypto_keyboard
from text import responses, PREMIUM_TEXT
from aiocryptopay import AioCryptoPay, Networks

crypto = AioCryptoPay(token=config.AIO_TOKEN, network=Networks.TEST_NET)


async def check_and_update_premium_status(user_id):
    async with aiofiles.open('premium_users.json', 'r') as file:
        premium_users = json.loads(await file.read())

    if str(user_id) in premium_users:
        expiration_date = datetime.strptime(premium_users[str(user_id)], '%Y-%m-%d')
        if expiration_date > datetime.now():
            return True, expiration_date.strftime('%Y-%m-%d')
        else:
            del premium_users[str(user_id)]
            async with aiofiles.open('premium_users.json', 'w') as file:
                await file.write(json.dumps(premium_users, ensure_ascii=False, indent=4))
            return False, None
    else:
        return False, None


async def activate_premium(user_id, days):
    try:
        premium_duration = timedelta(days=days)
        async with aiofiles.open('premium_users.json', 'r+') as file:
            data = json.loads(await file.read())
            if str(user_id) in data:
                current_expiration = datetime.strptime(data[str(user_id)], '%Y-%m-%d')
                new_expiration_date = current_expiration + premium_duration
            else:
                new_expiration_date = datetime.now() + premium_duration

            data[str(user_id)] = new_expiration_date.strftime('%Y-%m-%d')
            await file.seek(0)
            await file.write(json.dumps(data, ensure_ascii=False, indent=4))
            await file.truncate()
    except Exception as e:
        print(f"Ошибка активации премиум-статуса: {e}")


async def send_payment_method_selection(callback, user_id, unique_id):
    markup = await premium_keyboard(unique_id)
    await callback.bot.send_message(user_id, f"{PREMIUM_TEXT} Выберите способ оплаты премиума:",
                                    reply_markup=markup)


async def start_dp(dp, bot):
    @dp.callback_query(F.data.startswith("pay_stars_"))
    async def pay_with_stars(callback):
        unique_id = callback.data.split('_')[-1]
        if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
            await callback.answer(random.choice(responses), show_alert=True)
            return
        try:
            prices = [LabeledPrice(label="XTR", amount=35)]
            await callback.message.answer_invoice(
                title="🌟 Комару премиум",
                description="Покупка комару премиума",
                prices=prices,
                provider_token="",
                payload="komaru_premium",
                currency="XTR",
                reply_markup=await payment_keyboard(),
            )
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except Exception as e:
            await callback.message.answer(f"Произошла ошибка: {str(e)}")
            logging.error(f"Error in pay_with_stars: {e}")

    async def handle_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    async def handle_successful_payment(message: types.Message):
        await activate_premium(message.from_user.id, 30)
        await message.answer(
            '🌟 Спасибо за покупку Премиума! Наслаждайтесь эксклюзивными преимуществами.')

    @dp.callback_query(F.data.startswith("pay_crypto_"))
    async def create_and_send_invoice(callback):
        try:
            invoice = await crypto.create_invoice(asset='USDT', amount=0.5)
            if not invoice:
                response = "Ошибка при создании инвойса. Попробуйте позже."
                await bot.send_message(callback.from_user.id, response)
                return None

            markup = await payment_crypto_keyboard(invoice.invoice_id, invoice.bot_invoice_url)

            response = (
                f"Премиум активируется после подтверждения оплаты. Реквизиты: {invoice.bot_invoice_url}"
            )
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
            await bot.send_message(callback.from_user.id, response, reply_markup=markup)
            return invoice
        except Exception as e:
            error_message = f"Ошибка при создании инвойса: {e}"
            await bot.send_message(callback.from_user.id, error_message)
            return None

    @dp.callback_query(F.data.startswith("verify_payment"))
    async def verify_payment(call):
        parts = call.data.split('_')
        print(parts)
        if len(parts) < 3:
            await bot.send_message(call.message.chat.id, "Ошибка в данных платежа.")
            return

        action, context, invoice = parts[0], parts[1], parts[2]

        try:
            print("Invoice ID:", invoice)
            payment_status = await get_invoice_status(invoice)
            if payment_status == 'paid':
                await activate_premium(call.from_user.id, 30)
                await bot.send_message(call.from_user.id,
                                       "🌟 Спасибо за покупку Премиума! Наслаждайтесь эксклюзивными преимуществами.")
                await bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                await bot.send_message(call.from_user.id, "Оплата не прошла! Попробуйте еще раз.")
        except Exception as e:
            await bot.send_message(call.from_user.id, f"Произошла ошибка при проверке статуса платежа: {str(e)}")

    async def get_invoice_status(invoice_id):
        try:
            print(invoice_id)
            invoice = await crypto.get_invoices(invoice_ids=int(invoice_id))
            return invoice.status
        except Exception as e:
            print(f"Ошибка при получении данных инвойса: {e}")
            return None

    dp.pre_checkout_query.register(handle_pre_checkout_query)
    dp.message.register(handle_successful_payment, F.successful_payment)
