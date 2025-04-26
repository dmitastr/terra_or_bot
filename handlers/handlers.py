from handlers.find_game_handler import find_game_handler
from handlers.start_handler import start_handler
from handlers.register_user import register_user_handler
from handlers.add_user import add_user_handler
from handlers.change_gamemasters_list import change_gamemasters_list_handler
from handlers.mention_all_users import mention_all_users_handler
from handlers.captcha_solve import captcha_send_handler, captcha_solve_handler


handlers = [
    captcha_send_handler,
    captcha_solve_handler,
    find_game_handler,
    start_handler,
    register_user_handler,
    add_user_handler,
    change_gamemasters_list_handler,
    mention_all_users_handler,
]
