import logging
from telegram.ext import (
    CallbackContext, 
    ChatMemberHandler,
    filters
)
from telegram import (
    Update,
)
from telegram.constants import ChatMemberStatus
from common.config import GAMEMASTERS_CHAT_IDS
from datasource.db_controller import YDataBase


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def change_gamemasters_list(update: Update, context: CallbackContext) -> None:
    db = YDataBase(endpoint="REPORTS_ENDPOINT", database="REPORTS_DATABASE") 
    if update.chat_member:
        username = update.chat_member.new_chat_member.user.username
        user_id = update.chat_member.new_chat_member.user.id
        status = update.chat_member.new_chat_member.status
    
        if status == ChatMemberStatus.MEMBER:
            new_user = {"user_id": user_id, "role": "user", "username": username}
            db.insert_row(new_user, table_name="gamemasters")   

        elif status == ChatMemberStatus.LEFT or status == ChatMemberStatus.BANNED:
            db.delete(table_name="gamemasters", field_filter={"user_id": [user_id]})   
            


change_gamemasters_list_handler = ChatMemberHandler(
    change_gamemasters_list,
    chat_member_types=ChatMemberHandler.ANY_CHAT_MEMBER
)