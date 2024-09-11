import clickhouse_connect
from core.config import main_config
from crud.ch_table_creation import create_tables_queries


class ClickHouseDB:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.create_tables()

    def create_tables(self):
        client = self.get_client()
        for query in create_tables_queries:
            client.command(query)

    def get_client(self):
        client = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
        )
        return client


client = ClickHouseDB(
    host=main_config.database.clickhouse_host,
    port=main_config.database.clickhouse_port,
    username=main_config.database.clickhouse_user,
    password=main_config.database.clickhouse_password,
)


def get_db_client():
    yield client.get_client()
