
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from app.logic.adapter import LogicMainWindow, logic_db_window
from app.models import (
    RowViewOnDBTable,
    RowViewOnMainTable,
    ViewOnDBTableModels,
    ViewOnMainTableModels,
)

from .add_or_update import AddRowWindow, UpdateRowWindow
from .db import DBWindow


class MainWindow(QMainWindow):
    """Главное окно программы."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.logic_for_main = LogicMainWindow()
        self.logic_for_db = logic_db_window
        self.model_for_main = ViewOnMainTableModels
        self.model_for_db = ViewOnDBTableModels
        self.row_for_main = RowViewOnMainTable
        self.row_for_db = RowViewOnDBTable

        self.initUI()
        self.load_data()

    def initUI(self):
        """Инициация пользовательского интерфейса."""
        self.setWindowTitle('Калькулятор для Мамы')
        self.setGeometry(300, 400, 700, 500)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        bot_layout = QHBoxLayout()

        layout_left_top = QFormLayout()

        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.table_view.setSelectionMode(
            QTableView.SelectionMode.SingleSelection
        )
        self.table_view.setAlternatingRowColors(True)
        header = self.table_view.horizontalHeader()
        header.setFixedHeight(40)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout_left_top.addRow('', self.table_view)

        layout_right_top = QFormLayout()
        buttons = [
            ('Добавить', self.add_item),
            ('Изменить', self.update_item),
            ('Удалить', self.delete_item),
            ('Очистить', self.remove_items),
        ]

        for name, func in buttons:
            button = QPushButton(name)
            button.clicked.connect(func)
            layout_right_top.addRow('', button)

        self.label = QLabel()
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        layout_left_top.addRow('', self.label)

        top_layout.addLayout(layout_left_top)
        top_layout.addLayout(layout_right_top)

        button_db = QPushButton('База данных')
        button_db.clicked.connect(self.open_window_db)
        bot_layout.addWidget(button_db, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bot_layout)

        central_widget.setLayout(main_layout)

        self.show()

    def load_data(self):
        """Обновление данных в таблице окна."""
        data = self.logic_for_main.get_all()
        model = self.model_for_main(data)
        self.table_view.setModel(model)
        self.label.setText(self.logic_for_main.calculation())

    def add_item(self):
        """Откроет окно для добавление строки в таблицу окна."""
        self.window_add_row = AddRowWindow(
            parent=self,
            logic_for_main=self.logic_for_main,
            logic_for_db=self.logic_for_db,
            row_for_main=self.row_for_main,
            model_for_db=self.model_for_db,
        )
        self.load_data()

    def remove_items(self):
        """Удалит из таблицы окна все строки."""
        self.logic_for_main.clear()
        self.load_data()

    def update_item(self):
        """Откроет окно для изменения строки в таблице окна."""
        index_row = self.get_index_selected_row()

        if index_row is None:
            return

        self.db_add_window = UpdateRowWindow(
            parent=self,
            logic_for_db=self.logic_for_db,
            logic_for_main=self.logic_for_main,
            row_for_main=self.row_for_main,
            index_row=index_row,
        )
        self.load_data()

    def delete_item(self):
        """Удалит элемент из таблицы окна."""
        index = self.get_index_selected_row()

        if index is None:
            return

        self.logic_for_main.delete(index)
        self.load_data()

    def get_index_selected_row(self) -> int | None:
        """Вернет индекс выделенной строки таблицы окна."""
        selected = self.table_view.selectionModel().selectedRows()
        if selected:
            return selected[0].row()
        return None

    def open_window_db(self):
        """Откроет окно управления базой данных."""
        self.window_db = DBWindow(
            parent=self,
            logic_for_db=self.logic_for_db,
            model_for_db=self.model_for_db,
        )
