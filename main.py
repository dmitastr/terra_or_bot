from datasource.db_controller import YDataBase
from service.service import Service
from persistence.ydb_persistence import YdbPersistence
import json
import logging
import os

from telegram.ext import Application
from telegram import Update

import handlers
from handlers.error_handler import error_handler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    force=True
)
logger = logging.getLogger(__name__)


async def handler(event, context) -> dict:
    TG_TOKEN: str | None = os.environ.get("BOT_TOKEN")
    db = YDataBase(endpoint='REPORTS_ENDPOINT', database='REPORTS_DATABASE')
    service = Service(db=db, api_key=context.token['access_token'])

    handlers_list = [
        handlers.start_handler,

        handlers.register_user_handler,
        handlers.add_user_handler,
        handlers.change_gamemasters_list_handler,

        handlers.mention_all_users_handler,

        handlers.SendShiftsHandler(service=service),
        handlers.ScheduleCreateHandler(service=service),

        handlers.forward_message_handler,

        handlers.find_game_handler,
    ]
    if TG_TOKEN == None:
        return {'statusCode': 500, 'body': 'could not find telegram token'}

    persistance = YdbPersistence(db, table_name='persistent_user_data')
    application = (Application
                   .builder()
                   .token(TG_TOKEN)
                   .pool_timeout(100)
                   .connect_timeout(100)
                   .connection_pool_size(1000)
                   .persistence(persistance)
                   .build())

    application.add_handlers(handlers=handlers_list)
    application.add_error_handler(error_handler)
    await application.initialize()

    logger.info("Application fetched user data")
    logger.info(application.user_data)

    if update_raw := event.get("body"):
        update_parsed = json.loads(update_raw)
        logger.info(update_parsed)
        if event_type := update_parsed.get("event_type"):
            if event_type == "forward_personal_game":
                await handlers.forward_personal_game_handler(body=update_parsed["data"], bot=application.bot)
        else:
            upd = Update.de_json(update_parsed, application.bot)
            if upd:
                await application.process_update(upd)

    else:
        logger.error(event)
        return {'statusCode': 400, 'body': 'Something is wrong'}

    await application.shutdown()

    return {'statusCode': 200, 'body': 'Hello World!'}
