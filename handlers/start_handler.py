import logging
from telegram.ext import (
    CallbackContext, 
    CommandHandler,
)
from telegram import (
    Update,
)
from telegram.constants import ParseMode


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HELP_MESSAGE = ('Привет! Это бот игроведов Терры, который помогает искать игры. Просто напиши название игры и бот найдёт, где она должна лежать')


async def show_help_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    await update.effective_chat.send_message(
        HELP_MESSAGE.format(user_id=user_id),
        parse_mode=ParseMode.HTML
    )
            

start_handler = CommandHandler(
    ['start', 'help'],
    show_help_message,
)