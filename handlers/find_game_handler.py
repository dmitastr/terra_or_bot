import logging
from telegram.ext import (
    CallbackContext,
    MessageHandler,
    filters
)
from telegram import (
    Update,
)
from telegram.constants import ParseMode
import requests
from datasource.db_controller import YDataBase

from common.config import APPSCRIPT_URL, TECH_SHEETS, SHEET_NAMES
from common.beutify_message import beutify_message


class MessageLengthFilter(filters.MessageFilter):
    def __init__(self, length: int, name=None, data_filter=False):
        self.max_length = length
        super().__init__(name, data_filter)

    def filter(self, message):
        return len(message.text) <= self.max_length


# Remember to initialize the class.
length: int = 20
msg_length_filter = MessageLengthFilter(length)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def find_game(update: Update, context: CallbackContext) -> None:
    if update.effective_user and update.effective_message:
        user_id = update.effective_user.id
        db = YDataBase(endpoint='REPORTS_ENDPOINT',
                       database='REPORTS_DATABASE')
        user_exist = db.get_fields_equal(

            table_name='gamemasters',
            field_filter={'user_id': [int(user_id)]}
        )
        if user_exist:
            game_to_find = update.effective_message.text
            params = {"search_string": game_to_find}

            response = requests.get(APPSCRIPT_URL, params=params)

            games = [
                game for game in response.json()
                if game["lockerName"] in SHEET_NAMES
            ]
            game_exist = bool(response.json())

            message = beutify_message(games)
            if message:
                message = "Найдены игры:\n\n" + message
            elif game_exist:
                message = "Игра есть в коллекции, место неизвестно"
            else:
                message = "Подходящих игр не найдено"

            await update.effective_message.reply_text(
                message,
                parse_mode=ParseMode.HTML
            )


find_game_handler = MessageHandler(
    filters=filters.ChatType.PRIVATE & filters.TEXT & msg_length_filter,
    callback=find_game,
)
