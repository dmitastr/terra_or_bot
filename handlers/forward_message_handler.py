import os
import logging
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    filters
)
from telegram import (
    Update,
)

from telegram.helpers import escape_markdown
from telegram.constants import ParseMode

from common.config import DEV_USER_ID
from common.env_vars_parser import EnvParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def forward_message(update: Update, context: CallbackContext) -> None:
    env_cfg = EnvParser()
    env_cfg.parse()
    chat_id = env_cfg.chat_id
    message_thread_id = env_cfg.message_thread_id
    if msg := update.effective_message.reply_to_message:
        message_thread_id = None
        if context.args:
            message_thread_id = int(context.args[0])

        await msg.forward(
            chat_id=chat_id,
            message_thread_id=message_thread_id
        )


forward_message_handler = CommandHandler(
    command=['fwd_msg'],
    filters=filters.Chat(DEV_USER_ID),
    callback=forward_message
)
