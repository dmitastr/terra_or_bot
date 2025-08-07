import os

from common.config import GM_CHAT_ID_TEST


class EnvParser:
    def __init__(self) -> None:
        self.chat_id: int | None = None
        self.message_thread_id: int | None = None

    def parse(self) -> None:
        chat_cfg = os.environ.get('GM_CHAT_ID', GM_CHAT_ID_TEST)

        chat_ids = [int(id) for id in chat_cfg.split(":")]
        self.chat_id = chat_ids[0]
        if len(chat_ids) == 2:
            self.message_thread_id = chat_ids[1]
