import logging
import os

from telegram.helpers import escape_markdown
from telegram.constants import ParseMode
from telegram import Bot

from common.env_vars_parser import EnvParser


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def forward_personal_game_handler(body: dict, bot: Bot) -> None:
    env_cfg = EnvParser()
    env_cfg.parse()
    message_template = body.get("message_template", "")
    format_params = body.get("format_params", {})

    message_to_send = message_template.format(
        from_user=format_params["from_user"],
        text=escape_markdown(format_params["text"], version=2)
    )

    await bot.send_message(
        chat_id=env_cfg.chat_id,
        message_thread_id=env_cfg.message_thread_id,
        text=message_to_send,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    if photos := body.get("photos"):
        for photo in photos:
            await bot.send_photo(
                chat_id=env_cfg.chat_id,
                photo=photo,
                message_thread_id=env_cfg.message_thread_id,
            )
