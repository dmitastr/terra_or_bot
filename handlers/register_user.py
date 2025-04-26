import logging
from telegram.ext import (
    CallbackContext, 
    CommandHandler,
)
from telegram import (
    Update,
)
from telegram.constants import ParseMode
from common.config import DEV_USER_ID


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ADMIN_TEXT = '{full_name}\n\n<code>/add_user {id}</code>'
USER_TEXT = 'Ваш запрос отправлен админу'

async def register_user(update: Update, context: CallbackContext) -> None:
    await update.effective_chat.send_message(
        USER_TEXT,
        parse_mode=ParseMode.HTML
    )

    await context.bot.send_message(
        chat_id=DEV_USER_ID, 
        text=ADMIN_TEXT.format(id=update.effective_user.id, full_name=update.effective_user.full_name), 
        parse_mode=ParseMode.HTML
    )
            

register_user_handler = CommandHandler(
    ['add_me'],
    register_user,
)