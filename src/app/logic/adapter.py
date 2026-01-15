from decimal import Decimal

from app.db.repository import repository
from app.logic.dimension import DimensionConverter
from app.models import RowViewOnDBTable
from app.protocol import (
    DimensionConverterProtocol,
    LogicDBWindowProtocol,
    LogicMainWindowProtocol,
    RepositoryProtocol,
    RowViewProtocol,
)


class LogicMainWindow(LogicMainWindowProtocol):
    """Логика работы главного окна."""

    def __init__(self):
        self.data = []

    def get_all(self) -> list[RowViewProtocol]:
        """Вернет список объектов-строк обрабатываемых в логике."""
        return self.data

    def get(self, index: int) -> RowViewProtocol:
        """Вернет строку по индексу."""
        return self.data[index]

    def add(self, item: RowViewProtocol) -> None:
        """Добавит для обработки в логике объект-строку."""
        self.data.append(item)

    def delete(self, index: int) -> None:
        """Удалит из обработки в логике объект-строку."""
        del self.data[index]

    def update(self, index: int, new: RowViewProtocol) -> None:
        """Заменит объект-строку в логике."""
        self.data[index] = new

    def clear(self) -> None:
        """Очистит логику от объектов-строк."""
        self.data = []

    def calculation(self) -> str:
        """Вернет строку для поля "Итого"."""
        sum_data = round(sum(self.data), 2)
        rubles = int(sum_data // 1)
        kopecks = int(sum_data * 100 % 100)
        return f'Итого: {rubles} руб. {kopecks} коп.'


class LogicDBWindow(LogicDBWindowProtocol):
    """Логика работы окна "База данных"."""

    def __init__(
        self,
        repository: RepositoryProtocol,
        dimension: type[DimensionConverterProtocol],
    ) -> None:
        self.repository = repository
        self.dimension = dimension

    def get(self) -> list[RowViewProtocol]:
        """Вернет список объектов-строк."""
        return [
            RowViewOnDBTable(id, name, description, dimension, price)
            for id, name, description, dimension, price
            in self.repository.get_all()
        ]

    def add(
        self,
        name: str,
        quantity: int,
        price: float,
        dimension: str,
        description: str,
    ) -> None:
        """Подсчитает цену за размерность и добавит запись в базу данных."""
        quoted_dimension, quoted_price = self._calculation_to_base_quantity(
            price, quantity, dimension
        )

        self.repository.create(
            name=name,
            price=quoted_price,
            dimension=quoted_dimension,
            description=description,
        )

    def delete(self, id: int) -> None:
        """Удалит запись из базы данных."""
        self.repository.delete(id)

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
        quoted_dimension, quoted_price = self._calculation_to_base_quantity(
            price, quantity, dimension
        )

        self.repository.update(
            id_item,
            name=name,
            price=quoted_price,
            dimension=quoted_dimension,
            description=description,
        )

    def _calculation_to_base_quantity(
        self, price: float, quantity: int, dimension: str
    ) -> tuple[str, str]:
        result_price = Decimal(price) / Decimal(quantity)
        return self.dimension.get_base(dimension, result_price)

    def calculation(self, price: float, quantity: int, dimension: str) -> str:
        """
        Вернет стоимость, исходя из цены за единицу измерения (например, м),
        количеств в единцах измерения (например, см).
        """
        _, price_per_dimension = self.dimension.get_base(
            dimension, Decimal(price)
        )
        result_price = Decimal(price_per_dimension) * Decimal(quantity)
        return str(result_price)


logic_db_window = LogicDBWindow(repository, DimensionConverter)
