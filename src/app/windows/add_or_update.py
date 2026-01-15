from abc import abstractmethod
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableView,
    QWidget,
)

if TYPE_CHECKING:
    from app.logic.adapter import LogicDBWindow, LogicMainWindow
    from app.models import RowViewOnDBTable, RowViewOnMainTable


class BaseRowWindow(QDialog):
    """Базовое окно для создания и изменения строк."""

    def __init__(
        self,
        parent: QWidget,
        logic_for_main: 'LogicMainWindow',
        logic_for_db: 'LogicDBWindow',
        row_for_main: 'RowViewOnMainTable',
    ) -> None:
        super().__init__(parent)
        self.logic_for_main = logic_for_main
        self.logic_for_db = logic_for_db
        self.row_for_main = row_for_main
        self.cursor_row: 'RowViewOnMainTable' | None = None
        self.initUI()

    @abstractmethod
    def initUI(self):
        pass

    def _initUI(self):
        self.setGeometry(320, 420, 400, 120)

        main_layout = QFormLayout()
        layout_top = QHBoxLayout()

        self.label = QLabel()
        self.button_choice = QPushButton('Выбрать')
        self.button_choice.clicked.connect(self.choice_item)
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 10_000_000)
        self.dimension_input = QComboBox()

        layout_top.addWidget(self.label, stretch=2)
        layout_top.addWidget(self.button_choice, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.perform_action)
        buttons.rejected.connect(self.reject)

        for name, widget in (
            ('Название', layout_top),
            ('Количество', self.quantity_input),
            ('Размерность', self.dimension_input),
            ('', buttons),
        ):
            main_layout.addRow(name, widget)

        self.setLayout(main_layout)

    @abstractmethod
    def perform_action(self):
        pass

    @abstractmethod
    def choice_item(self):
        pass

    def validate_form(self):
        if self.quantity_input.value() == 0:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Количество должно быть больше 0!',
            )
            return False
        return True


class AddRowWindow(BaseRowWindow):
    def __init__(
        self,
        parent,
        logic_for_main,
        logic_for_db,
        row_for_main,
        model_for_db,
    ):
        self.model_for_db = model_for_db
        super().__init__(parent, logic_for_main, logic_for_db, row_for_main)

    def initUI(self):
        self.setWindowTitle('Добавить')
        self._initUI()
        self.exec()

    def perform_action(self):
        self.create_row()

    def create_row(self):
        if not self.validate_form():
            return

        parent = self.parent()
        price = self.logic_for_db.calculation(
            price=self.cursor_row.price,
            quantity=self.quantity_input.value(),
            dimension=self.dimension_input.currentText(),
        )
        item = self.row_for_main(
            name=self.cursor_row.name,
            quantity=self.quantity_input.value(),
            dimension=self.dimension_input.currentText(),
            price=price,
        )
        self.logic_for_main.add(item)
        parent.load_data()

        self.accept()

    def choice_item(self):
        self.window_choice_item = WindowChoiceItem(
            parent=self,
            logic_for_db=self.logic_for_db,
            model_for_db=self.model_for_db,
        )


class UpdateRowWindow(BaseRowWindow):
    def __init__(
        self,
        parent: QWidget,
        logic_for_main: 'LogicMainWindow',
        logic_for_db: 'LogicDBWindow',
        row_for_main: 'RowViewOnMainTable',
        index_row: int,
    ):
        self.index_row = index_row
        super().__init__(parent, logic_for_main, logic_for_db, row_for_main)

    def initUI(self):
        self.setWindowTitle('Изменить')
        self._initUI()
        self.button_choice.setEnabled(False)

        self.load_data()

        self.exec()

    def load_data(self):
        self.cursor_row = self.logic_for_main.get(self.index_row)

        self.label.setText(self.cursor_row.name)
        self.quantity_input.setValue(self.cursor_row.quantity)
        category = self.logic_for_db.dimension.get_category_by_dimension(
            self.cursor_row.dimension
        )
        dimensions = self.logic_for_db.dimension.get_dimensions_by_category(
            category
        )
        self.dimension_input.addItems(dimensions)
        self.dimension_input.setCurrentText(self.cursor_row.dimension)

    def perform_action(self):
        self.update_row()

    def update_row(self):
        if not self.validate_form():
            return

        parent = self.parent()
        price = self.logic_for_db.calculation(
            price=self.cursor_row.price,
            quantity=self.quantity_input.value(),
            dimension=self.dimension_input.currentText(),
        )
        item = self.row_for_main(
            name=self.cursor_row.name,
            quantity=self.quantity_input.value(),
            dimension=self.dimension_input.currentText(),
            price=price,
        )
        self.logic_for_main.update(self.index_row, item)
        parent.load_data()

        self.accept()


class WindowChoiceItem(QDialog):
    def __init__(
        self,
        parent: QWidget,
        logic_for_db: 'LogicDBWindow',
        model_for_db: 'RowViewOnDBTable',
    ):
        super().__init__(parent)
        self.logic_for_db = logic_for_db
        self.model_for_db = model_for_db
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Выбор ингредиента')
        self.setGeometry(340, 440, 700, 500)

        main_layout = QHBoxLayout()
        layout_left = QFormLayout()
        layout_right = QFormLayout()

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

        layout_left.addRow('', self.table_view)

        buttons = [
            ('Добавить', self.get_item),
            ('Выйти', self.reject),
        ]

        for name, func in buttons:
            button = QPushButton(name)
            button.clicked.connect(func)
            layout_right.addRow('', button)

        main_layout.addLayout(layout_left)
        main_layout.addLayout(layout_right)
        self.setLayout(main_layout)

        self.load_data()
        self.exec()

    def load_data(self):
        data = self.logic_for_db.get()
        model = self.model_for_db(data)
        self.table_view.setModel(model)
        self.table_view.hideColumn(0)

    def get_item(self):
        parent = self.parent()
        parent.cursor_row = self.get_selected_row()
        if parent.cursor_row is None:
            return
        parent.label.setText(parent.cursor_row.name)
        category = self.logic_for_db.dimension.get_category_by_dimension(
            parent.cursor_row.dimension
        )
        dimensions = self.logic_for_db.dimension.get_dimensions_by_category(
            category
        )
        parent.dimension_input.addItems(dimensions)
        self.accept()

    def get_selected_row(self):
        selected = self.table_view.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            model = self.table_view.model()
            if isinstance(model, self.model_for_db):
                return model.get_row(row)
        return None
