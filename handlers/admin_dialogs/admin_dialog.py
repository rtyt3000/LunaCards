from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const

from .admin_states import AdminSG, PremiumSG, BanSG, UnBanSG, DelSeasonSG, ChangeUsernameSG, MailingSG
from middlewares import AdminMiddleware


async def message_to_mailing_handler(
        message: Message,
        message_input: Message,
        manager: DialogManager,
): await manager.switch_to(AdminSG)


admin_dialog = Dialog(
    Window(
        Const("Привет админ!"),
        Start(Const("Рассылка"), id="mailing", state=MailingSG.choose_type),
        Row(
            Start(Const("Премиум"), id="premium", state=PremiumSG.premium_get_id),
            Start(Const("Сменить ник"), id="__change_username__", state=ChangeUsernameSG.get_id),
        ),
        Row(
            Start(Const("Бан"), id="ban", state=BanSG.get_id),
            Start(Const("Разбан"), id="unban", state=UnBanSG.get_id),
        ),
        Start(Const("Сбросить сезон"), id="reset_season", state=DelSeasonSG.accept_del),
        state=AdminSG.menu,
    ),
    Window(
        Const("Отправьте сообщение для рассылки, оно может содержать фото, видео и гифки"),
        MessageInput(message_to_mailing_handler,
                     content_types=[ContentType.PHOTO, ContentType.VIDEO, ContentType.ANIMATION]),
        Back(Const('В меню')),
        state=AdminSG.mailing
    ),
)


