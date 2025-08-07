import logging
import html
import json
import traceback
from telegram.ext import (
    CallbackContext,
)
from telegram import (
    Update,
)
from telegram.constants import ParseMode

from common.config import DEV_USER_ID

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def error_handler(update: object, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:",
                 exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    await context.bot.send_message(
        chat_id=DEV_USER_ID,
        text=message,
        parse_mode=ParseMode.HTML
    )
