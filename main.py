import json
import logging
import os

from telegram.ext import Application
from telegram import Update

from handlers.handlers import handlers
from handlers.error_handler import error_handler
from handlers.forward_personal_game import forward_personal_game_handler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    force=True
)
logger = logging.getLogger(__name__)
TG_TOKEN = os.environ.get("BOT_TOKEN")


async def handler(event, context) -> dict:
    application = (Application
                   .builder()
                   .token(TG_TOKEN)
                   .pool_timeout(100)
                   .connect_timeout(100)
                   .connection_pool_size(1000)
                   .build())

    application.add_handlers(handlers=handlers)
    application.add_error_handler(error_handler)
    await application.initialize()

    logger.info("Application fetched user data")
    logger.info(application.user_data)

    if update_raw := event.get("body"):
        update_parsed = json.loads(update_raw)
        logger.info(update_parsed)
        if event_type := update_parsed.get("event_type"):
            if event_type == "forward_personal_game":
                await forward_personal_game_handler(body=update_parsed["data"], bot=application.bot)
        else:
            upd = Update.de_json(update_parsed, application.bot)
            try:
                logger.info(f"New chat member = {upd.chat_member}")
            except:
                logger.info("No new chat member")

            await application.process_update(upd)

    else:
        logger.error(event)
        return {'statusCode': 400, 'body': 'Something is wrong'}

    await application.shutdown()

    return {'statusCode': 200, 'body': 'Hello World!'}
