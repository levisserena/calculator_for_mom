from app.protocol import RepositoryProtocol

from .manager import Connector, connector

NAME_TABLE = 'ingredient'
NAME = 'name'
DESCRIPTION = 'description'
PRICE = 'price'
DIMENSION = 'dimension'


class RepositoryBase:

    def __init__(self, connector: Connector):
        self.connector = connector
        self.name_table = NAME_TABLE
        self.field_name = NAME
        self.field_description = DESCRIPTION
        self.field_price = PRICE
        self.field_dimension = DIMENSION


class RepositoryStart(RepositoryBase):

    def create_table(self):
        """Создаст таблицу в БД для хранения настроек приложения."""
        with self.connector as cursor:
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.name_table} (
            id INTEGER PRIMARY KEY,
            {self.field_name} TEXT NOT NULL,
            {self.field_description} TEXT,
            {self.field_price} TEXT NOT NULL,
            {self.field_dimension} TEXT NOT NULL
            )
            """)


class RepositoryDB(RepositoryBase, RepositoryProtocol):
    """Репозиторий для CRUD-операций с базой данных."""

    def get_all(self) -> list:
        """Вернет все записи из таблицы базы данных."""
        with self.connector as cursor:
            all_rows = cursor.execute(
                f"""
                SELECT
                    id,
                    {self.field_name},
                    {self.field_description},
                    {self.field_dimension},
                    {self.field_price}
                FROM {self.name_table}
                ORDER BY id
                """,
            ).fetchall()
        return all_rows

    def create(
        self,
        name: str,
        price: str,
        dimension: str,
        description: str = '',
    ) -> None:
        """Создаст запись в таблице базы данных."""
        with self.connector as cursor:
            cursor.execute(
                f"""
                INSERT INTO {self.name_table} (
                    {self.field_name},
                    {self.field_description},
                    {self.field_price},
                    {self.field_dimension}
                )
                VALUES (?, ?, ?, ?)
                """,
                (name, description, price, dimension),
            )

    def update(
        self,
        id: int,
        name: str,
        price: str,
        dimension: str,
        description: str,
    ) -> None:
        with self.connector as cursor:
            cursor.execute(
                f"""
                UPDATE {self.name_table}
                SET
                    {self.field_name} = ?,
                    {self.field_description} = ?,
                    {self.field_price} = ?,
                    {self.field_dimension} = ?
                WHERE id = ?
                """,
                (name, description, price, dimension, id),
            )

    def delete(self, id: int) -> None:
        """Удалит запись из таблице по id."""
        with self.connector as cursor:
            cursor.execute(
                f"""
                DELETE FROM {self.name_table}
                WHERE id = ?
                """,
                (id,),
            )


start = RepositoryStart(connector)
repository = RepositoryDB(connector)
