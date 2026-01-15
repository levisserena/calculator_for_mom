from decimal import Decimal
from enum import Enum
from typing import Protocol


type CategoryType = Enum


class RepositoryProtocol(Protocol):
    """Протокол репозитория"""

    def get_all(self) -> list:
        """Вернет все записи из таблицы базы данных."""

    def create(
        self,
        name: str,
        price: str,
        dimension: str,
        description: str = '',
    ) -> None:
        """Создаст запись в таблице базы данных."""

    def update(
        self,
        id: int,
        name: str,
        price: str,
        dimension: str,
        description: str,
    ) -> None:
        """Обновит запись в таблице базы данных."""

    def delete(self, id: int) -> None:
        """Удалит запись из таблице по id."""


class DimensionConverterProtocol(Protocol):

    @classmethod
    def get_base(cls, dimension: str, value: Decimal) -> tuple[str, str]:
        """Вернет базовую размерность и множитель."""

    @classmethod
    def get_dimensions_by_category(cls, category: CategoryType) -> list[str]:
        """Вернет все размерности для данной категории."""

    @classmethod
    def get_category_by_dimension(cls, dimension: str) -> CategoryType | None:
        """Вернет категорию для данной размерности."""

    @classmethod
    def get_all(cls) -> list[str]:
        """Вернет все размерности."""


class RowViewProtocol(Protocol):
    """Протокол строк отображаемых таблиц."""

    headers: list[str]

    def __getitem__(self, index: int):
        ...

    def __len__(self):
        ...


class LogicMainWindowProtocol(Protocol):
    """Протокол логики работы главного окна."""

    def get_all(self) -> list[RowViewProtocol]:
        """Вернет список объектов-строк обрабатываемых в логике."""

    def get(self, index: int) -> RowViewProtocol:
        """Вернет строку по индексу."""

    def add(self, item: RowViewProtocol) -> None:
        """Добавит для обработки в логике объект-строку."""

    def delete(self, index: int) -> None:
        """Удалит из обработки в логике объект-строку."""

    def update(self, index: int, new: RowViewProtocol) -> None:
        """Заменит объект-строку в логике."""

    def clear(self) -> None:
        """Очистит логику от объектов-строк."""

    def calculation(self) -> str:
        """Вернет строку для поля "Итого"."""


class LogicDBWindowProtocol(Protocol):
    """Протокол логики работы окна "База данных"."""

    def get(self) -> list[RowViewProtocol]:
        """Вернет список объектов-строк."""

    def add(
        self,
        name: str,
        quantity: int,
        price: float,
        dimension: str,
        description: str,
    ) -> None:
        """Подсчитает цену за размерность и добавит запись в базу данных."""

    def delete(self, id: int) -> None:
        """Удалит запись из базы данных."""

    def update(
        self,
        id_item: int,
        name: str,
        quantity: int,
        price: float,
        dimension: str,
        description: str,
    ) -> None:
        """Изменит запись из базы данных."""

    def calculation(
        self, price: float, quantity: int, dimension: str
    ) -> str:
        """
        Вернет стоимость, исходя из цены за единицу измерения (например, м),
        количеств в единцах измерения (например, см).
        """
