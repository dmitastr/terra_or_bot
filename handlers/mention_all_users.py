import logging
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    filters
)
from telegram import (
    Update,
)
from telegram.constants import ParseMode
from common.config import DEV_USER_ID, GAMEMASTERS_CHAT_IDS
from datasource.db_controller import YDataBase
from common.beutify_message import mention_wrapper


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def mention_all_users(update: Update, context: CallbackContext) -> None:
    if not update.effective_user or not update.effective_message or not update.effective_chat:
        return

    requester_id = update.effective_user.id
    original_message_id = None
    if update.effective_message.reply_to_message:
        original_message_id = update.effective_message.reply_to_message.message_id
    db = YDataBase(endpoint='REPORTS_ENDPOINT', database='REPORTS_DATABASE')
    users_to_mention = db.get_fields_equal(
        table_name='gamemasters'
    )
    message = " ".join([
        mention_wrapper(user["username"])
        for user in users_to_mention
        if user["user_id"] != requester_id
    ])
    logger.info(message)

    await update.effective_chat.send_message(
        message,
        parse_mode=ParseMode.HTML,
        reply_to_message_id=original_message_id
    )


mention_all_users_handler = CommandHandler(
    command=['all'],
    callback=mention_all_users,
    filters=filters.Chat(GAMEMASTERS_CHAT_IDS)
)
