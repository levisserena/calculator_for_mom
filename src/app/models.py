from decimal import Decimal

from PyQt6.QtCore import Qt, QAbstractTableModel

from app.protocol import RowViewProtocol


class RowViewOnMainTable(RowViewProtocol):

    headers = ['Название', 'Количество', 'Размерность', 'Стоимость']

    def __init__(
        self,
        name: str = '',
        quantity: int | float = 0,
        dimension: str = '',
        price: int | float = 0,
    ):
        self.name = name
        self.quantity = quantity
        self.dimension = dimension
        self.price = price

    def __getitem__(self, index):
        return [self.name, self.quantity, self.dimension, self.price][index]

    def __len__(self):
        return len(self.headers)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Decimal(self.price) + Decimal(other.price)
        elif isinstance(other, (int, float, Decimal)):
            return Decimal(self.price) + Decimal(other)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'{self.name, self.quantity, self.dimension, self.price}'
        )


class RowViewOnDBTable(RowViewProtocol):

    headers = ['ID', 'Название', 'Описание', 'Размерность', 'Стоимость']

    def __init__(
        self,
        id: int = 0,
        name: str = '',
        description: str | None = None,
        dimension: str = '',
        price: str = '',
    ):
        self.id = id
        self.name = name
        self.description = description
        self.dimension = dimension
        self.price = price

    def __getitem__(self, index):
        return [
            self.id, self.name, self.description, self.dimension, self.price
        ][index]

    def __len__(self):
        return len(self.headers)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'{self.name, self.description, self.dimension, self.price}'
        )


class ViewOnMainTableModels(QAbstractTableModel):

    def __init__(self, data=None):
        super().__init__()
        self.row = RowViewOnMainTable
        self._data = data or []

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self.row.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.row.headers[section]
        return None

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()])

        if role == Qt.ItemDataRole.BackgroundRole:
            if index.row() % 2 == 0:
                return Qt.GlobalColor.lightGray
        return None


class ViewOnDBTableModels(QAbstractTableModel):

    def __init__(self, data=None):
        super().__init__()
        self.row = RowViewOnDBTable
        self._data = data or []

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self.row.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.row.headers[section]
        return None

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()])

        if role == Qt.ItemDataRole.BackgroundRole:
            if index.row() % 2 == 0:
                return Qt.GlobalColor.lightGray
        return None

    def get_row(self, index_row) -> RowViewOnDBTable | None:
        if 0 <= index_row < len(self._data):
            return self._data[index_row]
        return None

    # def get_row_id(self, index_row) -> int | None:
    #     """Получить ID строки."""
    #     row = self.get_row(index_row)
    #     return None if row is None else row.id
