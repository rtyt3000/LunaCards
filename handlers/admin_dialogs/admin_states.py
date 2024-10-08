from aiogram.fsm.state import State, StatesGroup


class AdminSG(StatesGroup):
    menu = State()
    mailing = State()
    ban = State()
    unban = State()
    reset_season = State()


class PremiumSG(StatesGroup):
    premium_get_id = State()
    premium_get_date = State()
    premium_accept = State()
    error = State()
    all_good = State()


class BanSG(StatesGroup):
    get_id = State()
    error = State()
    user_is_banned = State()
    accept = State()
    all_ok = State()


class UnBanSG(StatesGroup):
    get_id = State()
    error = State()
    user_not_banned = State()
    accept = State()
    all_ok = State()


class DelSeasonSG(StatesGroup):
    accept_del = State()
    accept_2 = State()
    accept_3 = State()
    season_del = State()
    error = State()


class ChangeUsernameSG(StatesGroup):
    get_id = State()
    get_new_username = State()
    accept = State()
    changed = State()
    error = State()


class MailingSG(StatesGroup):
    choose_type = State()
    get_message = State()
    get_media = State()
    send_message = State()
    error = State()
