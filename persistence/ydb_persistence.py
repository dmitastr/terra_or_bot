import json
import logging
from typing import Any, Dict
from telegram.ext import BasePersistence
from telegram.ext._basepersistence import PersistenceInput
from typing import Tuple, List

from datasource.db_controller import YDataBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class YdbPersistence(BasePersistence):
    def __init__(self, db: YDataBase, table_name: str = 'persistent_user_data',
                 conv_table_name: str = 'persistent_conversation',
                 store_data: PersistenceInput | None = None, update_interval: float = 60):
        if not store_data:
            store_data = PersistenceInput(
                bot_data=False, chat_data=False, callback_data=False)

        super().__init__(store_data, update_interval)
        self.db = db
        self.table_name = table_name
        self.conv_table_name = conv_table_name

    async def get_user_data(self) -> dict[int, dict]:
        data = self.db.get_fields_equal(table_name=self.table_name)
        user_data = self.db_to_user_data(data)
        return user_data

    async def update_user_data(self, user_id: int, data: dict) -> None:
        logger.info(data)
        new_row = self.user_data_to_db(user_id, data)
        self.db.insert_row(new_row=new_row, table_name=self.table_name)

    async def refresh_user_data(self, user_id: int, user_data: dict) -> None:
        await self.update_user_data(user_id, user_data)

    async def drop_user_data(self, user_id: int) -> None:
        self.db.delete(table_name=self.table_name,
                       field_filter={'user_id': user_id})

    def db_to_user_data(self, rows: list[dict[str, Any]]) -> dict[int, dict]:
        user_data = {}
        for row in rows:
            uid = row['user_id']
            data_parsed: dict = json.loads(row['data'])
            user_data[uid] = data_parsed
        return user_data

    def user_data_to_db(self, user_id: int, data: dict) -> dict[str, Any]:
        data_json = json.dumps(data)
        return {'user_id': user_id, 'data': data_json}

    async def get_bot_data(self) -> None:
        pass

    async def update_bot_data(self, data: dict) -> None:
        pass

    async def refresh_bot_data(self, bot_data: dict) -> None:
        pass

    async def get_chat_data(self) -> None:
        pass

    async def update_chat_data(self, chat_id: int, data: dict) -> None:
        pass

    async def refresh_chat_data(self, chat_id: int, chat_data: dict) -> None:
        pass

    async def drop_chat_data(self, chat_id: int) -> None:
        pass

    def get_conversation_by_name(self, name: str) -> dict:
        rows = self.db.get_fields_equal(
            table_name=self.conv_table_name,
            field_filter={'name': name}
        )
        if rows:
            conv_data = json.loads(rows[0]['data'])
            return conv_data

        return {}

    async def get_conversations(self, name: str):
        return self.get_conversation_by_name(name)

    async def update_conversation(self, name: str, key: Tuple[int | str, ...], new_state: object | None) -> None:
        conv_data = self.get_conversation_by_name(name)
        if conv_data:
            conv_data[key] = new_state
            new_data = json.dumps(conv_data)
            self.db.insert_row(
                new_row={'name': name, 'data': new_data}, table_name=self.conv_table_name)

    async def get_callback_data(self) -> Tuple[List[Tuple[str, float, Dict[str, Any]]], Dict[str, str]] | None:
        pass

    async def update_callback_data(self, data: Tuple[List[Tuple[str, float, Dict[str, Any]]], Dict[str, str]]) -> None:
        pass

    async def flush(self) -> None:
        pass
