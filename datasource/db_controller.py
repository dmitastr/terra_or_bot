from typing import Any
import ydb # type: ignore
import ydb.iam # type: ignore
import os
import asyncio
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

INSERT_QUERY_TEMPLATE = 'UPSERT INTO {table_name} ({columns_clause}) VALUES ({values_clause})'
FILTER_QUERY_TEMPLATE = 'SELECT * FROM {table_name}  {order_by_clause} {limit_clause}'
DELETE_QUERY_TEMPLATE = "DELETE FROM {table_name} {where_clause}"
WHERE_CLAUSE_TEMPLATE = '{field} IN ({field_values_query})'



class YDataBase:
    def __init__(self, endpoint='YDB_ENDPOINT', database='YDB_DATABASE') -> None:
        self.endpoint = os.getenv(endpoint)
        self.database = os.getenv(database)
        if self.endpoint is None or self.database is None:
            raise AssertionError("Нужно указать обе переменные окружения")

        self.driver = ydb.Driver(
            endpoint=self.endpoint,
            database=self.database,
            credentials=ydb.iam.MetadataUrlCredentials(),
        )
        try:
            self.driver.wait(fail_fast=True, timeout=5)
        except TimeoutError:
            print("Connect failed to YDB")
            print("Last reported errors by discovery:")
            print(self.driver.discovery_debug_details())
            exit(1)


    def get_fields_equal(
        self, 
        table_name: str, 
        field_filter: dict[str, Any]={},
        order_by: list[list[Any]]=[],
        limit: int=0
    ) -> list[dict]:

        query = self.create_select_query(
            table_name=table_name, 
            field_filter=field_filter,
            order_by=order_by,
            limit=limit
        )
        return self.execute_query(query)
    

    def insert_row(self, new_row: dict, table_name: str) -> None:
        columns = []
        values = []
        for column, value in new_row.items():
            columns.append(column)
            if type(value) == str:
                values.append(f'"{value}"')
            else:
                values.append(f'{value}')

        columns_clause = ','.join(columns)
        values_clause = ','.join(values)
        query = INSERT_QUERY_TEMPLATE.format(
            table_name=table_name,
            columns_clause=columns_clause,
            values_clause=values_clause
        )
        logger.info(query)
        return self.execute_query(query)


    def insert_rows(self, new_rows: list[dict], table_name: str) -> None:
        for row in new_rows:
            self.insert_row(row, table_name=table_name)


    def update_rows(self, new_rows: list[dict], table_name: str) -> None:
        self.insert_rows(new_rows=new_rows, table_name=table_name)

    
    def delete(
        self, 
        table_name: str, 
        field_filter: dict[str, Any]={},
    ) -> list[dict]:

        where_clause = ""
        if field_filter:
            where_clauses = [
                self.create_where_clause(field, values)
                for field, values in field_filter.items()
            ]
            where_clause = 'WHERE ' + ' AND '.join(where_clauses)
        
        query = DELETE_QUERY_TEMPLATE.format(table_name=table_name, where_clause=where_clause)
        return self.execute_query(query)


    def execute_query(self, query): 
        session = self.driver.table_client.session().create()
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            query,
            commit_tx=True
        )
        result_parsed = []
        try:
            if result_sets:
                result_parsed = [self.parse_row(row) for row in result_sets[0].rows]
        except Exception:
            logger.exception("Error while executing query", exc_info=True)
        return result_parsed


    async def execute_query_async(self, query): 
        with ydb.Driver(endpoint=self.endpoint, database=self.database) as driver:
            await asyncio.wait_for(
                asyncio.wrap_future(driver.async_wait(fail_fast=True)), timeout=5
            )

            session_pool = ydb.SessionPool(driver)
            await ydb.aio.retry_operation(self._execute_query, query, session_pool)

    async def _execute_query(self, session, query):
        await session.execute_scheme(query)


    def parse_row(self, row):
        res_parsed = {}
        for k, v in dict(row).items():
            try: 
                value = v.decode()
            except (UnicodeDecodeError, AttributeError):
                value = v
            res_parsed[k] = value
        return res_parsed
    

    def create_select_query(
        self, 
        table_name: str, 
        field_filter: dict[str, Any]={},
        order_by: list[list[Any]]=[],
        limit: int=0
    ) -> str:

        where_clauses = [
            self.create_where_clause(field, values)
            for field, values in field_filter.items()
        ]
        where_clause = 'WHERE ' + ' AND '.join(where_clauses) if field_filter else ''

        order_by_clause = 'ORDER BY {}'.format(
            ' , '.join([
                self.create_order_by_clause(field, order) 
                for field, order in order_by
            ])
        ) if order_by else ''

        limit_clause = f'LIMIT {limit}' if limit else ''
        
        query = FILTER_QUERY_TEMPLATE.format(
            table_name=table_name,
            where_clause=where_clause,
            order_by_clause=order_by_clause,
            limit_clause=limit_clause
        )

        logger.info(query)
        return query


    def create_where_clause(self, field: str, field_values: list[Any]) -> str:
        if type(field_values[0]) == str:
            field_values_query = ','.join([f'"{value}"' for value in field_values])
        else:
            field_values_query = ','.join([str(value) for value in field_values])
        
        query = WHERE_CLAUSE_TEMPLATE.format(
            field=field,
            field_values_query=field_values_query
        )
        return query


    def create_order_by_clause(self, field: str, order: int) -> str:
        return field + ' ASC' if order else ' DESC' 

