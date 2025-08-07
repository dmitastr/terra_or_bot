import logging
from telegram.ext import (
    CallbackContext,
    CommandHandler,
)
from telegram import (
    Update,
)
from telegram.constants import ParseMode
from datasource.db_controller import YDataBase
from common.config import DEV_USER_ID


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

USER_TEXT = 'Регистрация прошла успешно!'


async def add_user(update: Update, context: CallbackContext) -> None:
    if update.effective_user == None:
        return

    if update.effective_user.id == DEV_USER_ID:
        db = YDataBase(endpoint='REPORTS_ENDPOINT',
                       database='REPORTS_DATABASE')

        if context.args == None:
            logger.error("no user_id was passed")
            return

        user_id = int(context.args[0])
        new_user = {'user_id': user_id, 'role': 'user'}
        db.insert_row(new_user, table_name='gamemasters')

        await context.bot.send_message(
            chat_id=user_id,
            text=USER_TEXT,
            parse_mode=ParseMode.HTML
        )


add_user_handler = CommandHandler(
    ['add_user'],
    add_user,
)
