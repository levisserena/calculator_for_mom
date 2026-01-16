from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from app.db.repository import repository
from app.logic.dimension import DimensionConverter
from app.models import RowViewOnDBTable

if TYPE_CHECKING:
    from app.db.repository import RepositoryDB
    from app.models import RowViewOnMainTable


class LogicMainWindow:
    """Логика работы главного окна."""

    def __init__(self):
        self.data = []

    def get_all(self) -> list['RowViewOnMainTable']:
        """Вернет список объектов-строк обрабатываемых в логике."""
        return self.data

    def get(self, index: int) -> 'RowViewOnMainTable':
        """Вернет строку по индексу."""
        return self.data[index]

    def add(self, item: 'RowViewOnMainTable') -> None:
        """Добавит для обработки в логике объект-строку."""
        self.data.append(item)

    def delete(self, index: int) -> None:
        """Удалит из обработки в логике объект-строку."""
        del self.data[index]

    def update(self, index: int, new: 'RowViewOnMainTable') -> None:
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


class LogicDBWindow:
    """Логика работы окна "База данных"."""

    def __init__(
        self,
        repository: 'RepositoryDB',
        dimension: type[DimensionConverter],
        row_view: type[RowViewOnDBTable],
    ) -> None:
        self.repository = repository
        self.dimension = dimension
        self.row_view = row_view

    def get_all(self) -> list[RowViewOnDBTable]:
        """Вернет список объектов-строк."""
        return [
            self.row_view(id, name, description, dimension, price)
            for id, name, description, dimension, price
            in self.repository.get_all()
        ]

    def get(self, id: int) -> RowViewOnDBTable | None:
        """Вернет строку по переданному id."""
        item = self.repository.get(id)
        if item is None:
            return None
        return self.row_view(*item)

    def add(
        self,
        name: str,
        quantity: int,
        price: float,
        dimension: str,
        description: str,
    ) -> None:
        """Подсчитает цену за размерность и добавит запись в базу данных."""
        quoted_price = self._calculation(price, quantity)

        self.repository.create(
            name=name,
            price=quoted_price,
            dimension=dimension,
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
        quoted_price = self._calculation(price, quantity)

        self.repository.update(
            id_item,
            name=name,
            price=quoted_price,
            dimension=dimension,
            description=description,
        )

    def _calculation(self, price: float, quantity: int) -> str:
        """Вычислит стоимость одной единицы."""
        result_price = Decimal(price) / Decimal(quantity)
        rounded_result = result_price.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        return str(rounded_result)

    def calculation(
        self,
        price: int | float | str,
        quantity: int | float | str,
        current_dimension: str,
        db_dimension: str,
    ) -> float:
        """
        Вернет стоимость, исходя из цены за единицу измерения (например, м),
        количеств в единцах измерения (например, см).
        """
        ratio = self.dimension.get_ratio(current_dimension, db_dimension)
        result_price = Decimal(Decimal(price)) * Decimal(quantity) * ratio
        rounded_result = result_price.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        return float(rounded_result)


logic_db_window = LogicDBWindow(
    repository, DimensionConverter, RowViewOnDBTable
)
