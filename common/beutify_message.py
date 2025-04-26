import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def beutify_message(games: list[dict]) -> str:
    games_uniq = {}
    
    for game in games:
        name = game["name"]
        locker = game["lockerName"]
        place = game["gamePlace"]
        if name in games_uniq:
            games_uniq[name].append(f"- {locker} {place}")
        else:
            games_uniq[name] = [f"- {locker} {place}"]

    message = ""
    for name, places in games_uniq.items():
        message += f"<b>{name}</b>\n"
        message += "\n".join(places)
        message += "\n"

    message = message.strip()
    return message


def mention_wrapper(username: str) -> str:
    return f"@{username}"

