import logging
from typing import Any, List, Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram._utils.defaultvalue import DEFAULT_TRUE
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters, BaseHandler

from service.service import Service
from common.config import SLOTS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

day_names = {
    "1": ("Пн", 0),
    "2": ("Вт", 0),
    "3": ("Ср", 1),
    "4": ("Чт", 1),
    "5": ("Пт", 2),
    "6": ("Сб", 3),
    "7": ("Вс", 4),
}

period_names = {
    "1": ("утро", 0),
    "3": ("вечер", 1),
    "5": ("ночь", 2),
}

other_names = {
    'submit': ('Отправить', 6, 0),
    'comment': ('Комментарий', 5, 1),
    'all': ('Выбрать все', 5, 0)
}


class Button:
    def __init__(self, id: str) -> None:
        if name := other_names.get(id):
            self.name = name[0]
            self.position = (name[1], name[2])
        else:
            day = id[0]
            period = id[1]
            self.name = f"{day_names[day][0]} {period_names[period][0]}"
            self.position = self.calculate_position(day, period)
        self.callback_data = id

    def to_keyboard_button(self, check_type: int = 0) -> InlineKeyboardButton:
        suffix = ''
        match check_type:
            case 0:
                suffix = ' 🟢'
            case 1:
                suffix = ' 🟡'

        name = self.name + suffix
        return InlineKeyboardButton(name, callback_data=self.callback_data)

    def calculate_position(self, day: str, period: str) -> Tuple[int, int]:
        return (day_names[day][1], period_names[period][1])


buttons: List[Button] = [Button(slot) for slot in SLOTS]
buttons += [Button('submit'), Button('comment'), Button('all'),]

CHECK_CAN: int = 0
CHECK_WANT: int = 1
UNCHECK: int = 2

CHOICE, COMMENT = range(2)


class Keyboard:
    def __init__(self, buttons: List[Button]) -> None:
        self.buttons = buttons

    def create_keyboard(self, selected: dict[str, List[str]] = {}) -> List[List[InlineKeyboardButton]]:
        buttons = sorted(self.buttons, key=lambda x: 10 *
                         x.position[0]+x.position[1])
        keyboard = [[] for _ in range(buttons[-1].position[0]+1)]
        for btn in buttons:
            row = btn.position[0]

            check_type = 2
            if btn.callback_data in selected.get('wants', []):
                check_type = 0
            elif btn.callback_data in selected.get('cans', []):
                check_type = 1

            keyboard[row].append(btn.to_keyboard_button(check_type))

        return keyboard


def get_keyboard(selected: dict[str, List[str]] = {}):
    keyboard = Keyboard(buttons).create_keyboard(selected)

    return InlineKeyboardMarkup(keyboard)


def names_generate(shifts: List[str]) -> str:
    txt: List[str] = []
    for shift in shifts:
        btn = Button(shift)
        txt.append(btn.name)
    return ', '.join(txt)


def choices_update(choices: dict[str, List[str]], new_choice: str) -> dict[str, List[str]]:
    if not choices.get('wants'):
        choices['wants'] = []
    if not choices.get('cans'):
        choices['cans'] = []

    if new_choice == 'all':
        if len(choices['wants']) == len(SLOTS):
            choices['wants'] = []
        else:
            choices['wants'] = SLOTS

        choices['cans'] = []
        return choices

    if new_choice in choices['cans']:
        choices['cans'].remove(new_choice)
    elif new_choice in choices['wants']:
        choices['wants'].remove(new_choice)
        choices['cans'].append(new_choice)
    else:
        choices['wants'].append(new_choice)

    return choices


# handler funcs
async def send_shift_choices(update: Update, context: CallbackContext) -> int:
    if isinstance(context.user_data, dict):
        context.user_data['selected_options'] = {
            'cans': [], 'wants': [], 'comment': ''}
        if message := update.effective_message:
            await message.reply_text('Отметь подходящие варианты', reply_markup=get_keyboard(context.user_data.get('selected_options', {})))
        return CHOICE
    return ConversationHandler.END


async def button_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()
    if isinstance(context.user_data, dict):
        selected_options = context.user_data.get('selected_options', {})
        if choice := query.data:
            if choice == 'submit':
                context.user_data['save_shifts'] = True
                if update.effective_user:
                    user_id = update.effective_user.id
                    username = str(user_id)
                    if update.effective_user.username:
                        username = update.effective_user.username.lower()

                    context.user_data['username'] = username
                    context.user_data['user_id'] = update.effective_user.id

                text = 'Твои пожелания на следующую неделю:\n'
                if selected_options:
                    if wants := selected_options.get('wants'):
                        text += f'Хочу: {names_generate(wants)}\n'

                    if cans := selected_options.get('cans'):
                        text += f'Могу: {names_generate(cans)}\n'

                else:
                    text = "Ты не выбрал ничего"

                if comment := selected_options['comment']:
                    text += f'\nКомментарий: {comment}'

                await query.edit_message_text(text)

                logger.info(context.user_data)
                # context.user_data.clear()
                return ConversationHandler.END

            if choice == 'comment':
                if update.effective_chat:
                    await query.edit_message_text('Напиши комментарий')
                return COMMENT

            selected_options = choices_update(selected_options, query.data)

            context.user_data['selected_options'] = selected_options
            markup = get_keyboard(selected_options)
            await query.edit_message_reply_markup(reply_markup=markup)
            return CHOICE
    return ConversationHandler.END


async def add_comment(update: Update, context: CallbackContext) -> int:
    logger.info("add comment to shifts")
    if update.effective_message and isinstance(context.user_data, dict):
        context.user_data['selected_options']['comment'] = update.effective_message.text
        logger.info(f"comment: {update.effective_message.text}")

        markup = get_keyboard(context.user_data['selected_options'])
        await update.effective_message.reply_text('Отметь подходящие варианты', reply_markup=markup)

        return CHOICE

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    if update.message:
        if user := update.message.from_user:
            logger.info("User %s canceled the conversation.", user.id)
        await update.message.reply_text("Отмена", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


shift_button_handler = CallbackQueryHandler(button_callback)
shift_choices_handler = CommandHandler(
    command='send_shifts',
    callback=send_shift_choices,
    filters=filters.ChatType.PRIVATE

)

shift_choose_conversation_handler = ConversationHandler(
    entry_points=[shift_choices_handler],
    states={
        CHOICE: [shift_button_handler],
        COMMENT: [MessageHandler(filters.TEXT, add_comment)]
    },
    persistent=True,
    fallbacks=[CommandHandler("cancel", cancel)],
    name="sendShifts"
)


class SendShiftsHandler(BaseHandler):
    def __init__(self, service: Service):
        self.service = service
        self.handler = shift_choose_conversation_handler
        self.block = True

    def save_shifts(self, user_data: dict[str, Any]) -> None:
        return self.service.save_shifts(user_data)

    def check_update(self, update: object) -> Any:
        check_result = self.handler.check_update(update)
        return check_result

    async def handle_update(self, update: Any, application: Application[Any, Any, Any, Any, Any, Any], check_result: Any, context: Any) -> None:
        await self.handler.handle_update(
            update=update, application=application, check_result=check_result, context=context)

        if context.user_data.get('save_shifts'):
            self.save_shifts(context.user_data)
