import logging
import time
import emoji
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ChatMemberHandler,
    filters,
    ContextTypes
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
)

from telegram.constants import ChatMemberStatus
from common.config import GAMEMASTERS_CHAT_IDS
from datasource.db_controller import YDataBase


import random
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


choices_num = 5
NEW_USER_RESTRICTED = ChatPermissions.no_permissions()
NEW_USER_ALLOWED = ChatPermissions.all_permissions()
salt = "terra_group"
captcha_message_thread_id = 742
restricted_users = "users_restricted"


def generate_emoji_choices(choices_num: int) -> list[str]:
    return random.sample(list(emoji.EMOJI_DATA.keys()), choices_num)


def calculate_target_num(user_id: int, choices_num: int, salt: str) -> int:
    return hash(str(user_id) + salt) % choices_num


async def send_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.chat_member and update.chat_member.new_chat_member:
        new_user = update.chat_member.new_chat_member
        status = new_user.status
        user = new_user.user
        logger.info(f"New chat member with status '{new_user.status}'")
        if status == ChatMemberStatus.MEMBER:
            update.effective_chat.restrict_member(
                user_id=user.id,
                permissions=NEW_USER_RESTRICTED
            )

            # create_message
            emoji_selected = generate_emoji_choices(choices_num)
            target_idx = calculate_target_num(
                user_id=user.id,
                choices_num=choices_num,
                salt=salt,
            )
            target_emoji = emoji_selected[target_idx]
            keyboard = [[
                InlineKeyboardButton(emoji_item, callback_data=str(i))
                for i, emoji_item in enumerate(emoji_selected)
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # send_message
            message = await update.message.reply_text(
                text=f"Нажми на {target_emoji} чтобы подтвердить что ты человек",
                message_thread_id=captcha_message_thread_id,
                reply_markup=reply_markup
            )

            # insert into db
            entry = {
                "user_id": user.id,
                "is_valid": False,
                "is_deleted": False,
                "dttm_added": update.chat_member.date,
                "message_id": message.id,
                "chat_id": update.effective_chat.id,
            }
            # db = YDataBase(endpoint="REPORTS_ENDPOINT", database="REPORTS_DATABASE")
            # db.insert_row(
            #     table_name=restricted_users,
            #     new_row=entry,
            # )


async def solve_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    query = update.callback_query
    target_idx = calculate_target_num(
        user_id=user.id,
        choices_num=choices_num,
        salt=salt,
    )
    await query.answer()

    try:
        selected_idx = int(query.data)
    except ValueError:
        logger.exception(f"Error while parsing callback data '{query.data}'")
        return

    # fetch original message_id
    # db = YDataBase(endpoint="REPORTS_ENDPOINT", database="REPORTS_DATABASE")
    # db_filter = {
    #     "user_id": [user.id],
    # }
    # target_messages = db.get_fields_equal(
    #     table_name=restricted_users,
    #     field_filter=db_filter,
    # )

    # dummy data
    target_messages = [1]

    if (
        target_messages
        # and target_messages[0].get("message_id") == query.message.id
        and target_idx == selected_idx
    ):
        update.effective_chat.restrict_member(
            user_id=user.id,
            permissions=NEW_USER_ALLOWED,
        )

        entry = {
            "user_id": user.id,
            "is_valid": True,
        }
        # for _ in range(5):
        #     try:
        #
        #         db.insert_row(
        #             table_name="users_restricted",
        #             new_row=entry,
        #         )
        #     except:
        #         logger.exception("Error while writing to db")
        #         time.sleep(30)
        #     else:
        #         break

    await query.edit_message_text(
        text=f"Ты выбрал номер: {query.data}\nТребовалось выбрать номер: {target_idx}",
    )


captcha_solve_handler = CallbackQueryHandler(
    callback=solve_captcha
)


captcha_send_handler = ChatMemberHandler(
    callback=send_captcha,
    chat_member_types=ChatMemberHandler.ANY_CHAT_MEMBER,
)
