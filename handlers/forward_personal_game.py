import logging

from telegram import Bot
from telegram.helpers import escape_markdown
from telegram.constants import ParseMode


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
chat_id = -1001359050637 #test chat
# chat_id = -950503307 #prod chat


async def forward_personal_game_handler(body: dict, bot: Bot) -> None:
    message_template = body.get("message_template")
    format_params = body.get("format_params")

    message_to_send = message_template.format(
        from_user=format_params["from_user"], 
        text=escape_markdown(format_params["text"], version=2)
    )
    
    await bot.send_message(
        chat_id=chat_id,
        text=message_to_send,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    if photos := body.get("photos"):
        for photo in photos:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
            )