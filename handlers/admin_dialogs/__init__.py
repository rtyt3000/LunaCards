from aiogram import Router

from middlewares import AdminMiddleware
from .admin_dialog import admin_dialog, AdminSG
from .premium_dialog import premium_dialog
from .ban_dialog import ban_dialog
from .unban_dialog import unban_dialog
from .season_delete_dialog import season_delete_dialog
from .change_nickname_dialog import change_nickname_dialog
from .mailing_dialog import mailing_dialog

dialogs_router = Router()

dialogs_router.include_routers(admin_dialog, premium_dialog, ban_dialog, unban_dialog, season_delete_dialog,
                               change_nickname_dialog, mailing_dialog)
dialogs_router.message.middleware(AdminMiddleware())
dialogs_router.callback_query.middleware(AdminMiddleware())
