import html
import io
import json
import logging
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    BaseHandler,
    Application,
    filters
)
from telegram import (
    Update,

)
from telegram.constants import ParseMode
from service.service import Service
from gm_schedule_generator.gm_schedule_generator import GmScheduleGenerator
from common.config import DEV_USER_ID


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def schedule_create(update: Update, context: CallbackContext, message: str, file_content: str | None) -> None:
    if not update.effective_chat or not update.effective_user:
        return

    if not file_content:
        await update.effective_chat.send_message(
            text=message
        )

    file = io.StringIO(file_content)
    await update.effective_chat.send_document(
        caption=message,
        document=file,
        filename="gms_schedule.html"
    )


schedule_create_handler = CommandHandler(
    ['schedule_create'],
    lambda upd, ctx: 1,
)


class ScheduleCreateHandler(BaseHandler):
    def __init__(self, service: Service):
        self.block = True
        self.service = service
        self.handler = schedule_create_handler
        self.gm_generator = GmScheduleGenerator(service)

    def check_update(self, update: Update) -> bool | None:
        return self.handler.check_update(update)

    async def handle_update(self, update: Update, application: Application, check_result: bool | None, context: CallbackContext) -> None:
        message = "Извини, но ты не админ (пока)"
        html: str | None = None

        if update.effective_user.id == DEV_USER_ID:
            dates, table = self.service.schedule_create()
            html = self.gm_generator.render_html_page(dates, table)
            message = 'Драфт расписания'

        await schedule_create(update, context, message, html)
