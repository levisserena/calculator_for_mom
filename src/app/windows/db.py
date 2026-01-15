from abc import ABC, abstractmethod

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QGridLayout,
    QFormLayout,
    QTableWidget,
    QTableView,
    QHeaderView,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QTextEdit,
)

from app.models import ViewOnMainTableModels, RowViewOnMainTable, ViewOnDBTableModels, RowViewOnDBTable
from app.logic.adapter import LogicMainWindow, logic_db_window
from app.logic.dimension import DimensionConverter
from app.db.repository import repository
from app.protocol import LogicDBWindowProtocol, RowViewProtocol


class DBWindow(QDialog):
    """Окно управления ингредиентов."""

    def __init__(
        self,
        parent: QWidget,
        logic_for_db: LogicDBWindowProtocol,
        model_for_db: RowViewProtocol,
    ):
        super().__init__(parent)
        self.logic_for_db = logic_for_db
        self.model_for_db = model_for_db
        self.initUI()

    def initUI(self):
        self.setWindowTitle('База данных')
        self.setGeometry(320, 420, 700, 500)

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
            ('Добавить', self.add_item),
            ('Изменить', self.update_item),
            ('Удалить', self.delete_item),
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

    def add_item(self):
        self.db_add_window = DBAddWindow(self, self.logic_for_db)
        self.load_data()

    def update_item(self):
        row = self.get_selected_row()

        if row is None:
            return

        self.db_add_window = DBUpdateWindow(self, self.logic_for_db, row)
        self.load_data()

    def delete_item(self):
        row = self.get_selected_row()

        if row is None:
            return

        btn_accept = QPushButton('Да')
        btn_reject = QPushButton('Нет')

        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setWindowTitle('Подтверждение')
        message_box.setText(f'Удалить {row}?')
        message_box.addButton(btn_accept, QMessageBox.ButtonRole.AcceptRole)
        message_box.addButton(btn_reject, QMessageBox.ButtonRole.RejectRole)
        message_box.exec()

        if message_box.clickedButton() == btn_accept:
            self.logic_for_db.delete(row.id)
            self.load_data()

    def get_selected_row(self):
        selected = self.table_view.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            model = self.table_view.model()
            if isinstance(model, self.model_for_db):
                return model.get_row(row)
        return None


class BaseDBDialogWindow(QDialog):

    def __init__(
        self,
        parent:  QWidget,
        logic_for_db: LogicDBWindowProtocol,
    ):
        super().__init__(parent)
        self.logic_for_db = logic_for_db
        self.initUI()

    @abstractmethod
    def initUI(self):
        pass

    def _initUI(self):
        self.setGeometry(340, 440, 400, 270)

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMinimumHeight(50)
        self.description_input.setMaximumHeight(100)
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 10_000_000)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 10_000_000)
        self.dimension_input = QComboBox()
        self.dimension_input.addItems(DimensionConverter.get_all())

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.perform_action)
        buttons.rejected.connect(self.reject)

        for name, widget in (
            ('Название', self.name_input),
            ('Описание', self.description_input),
            ('Количество', self.quantity_input),
            ('Размерность', self.dimension_input),
            ('Цена', self.price_input),
            ('', buttons),
        ):
            layout.addRow(name, widget)

        self.setLayout(layout)

    @abstractmethod
    def perform_action(self):
        pass

    def validate_form(self):
        """Валидирование заполнение формы окна."""
        if self.name_input.text() == '':
            QMessageBox.warning(
                self, 'Ошибка', 'Введите название!',
            )
            return False
        if self.quantity_input.value() == 0:
            QMessageBox.warning(
                self, 'Ошибка', 'Количество должно быть больше 0!',
            )
            return False
        if self.price_input.value() == 0:
            QMessageBox.warning(
                self, 'Ошибка', 'Цена должна быть больше 0!',
            )
            return False
        return True


class DBAddWindow(BaseDBDialogWindow):
    """Окно добавления ингредиента в базу данных."""

    def initUI(self):
        self.setWindowTitle('Добавить предмет')
        self._initUI()
        self.exec()

    def perform_action(self):
        self.create_item()

    def create_item(self):
        """Добавит запись в базу данных."""
        if not self.validate_form():
            return

        self.logic_for_db.add(
            name=self.name_input.text(),
            quantity=self.quantity_input.value(),
            price=self.price_input.value(),
            dimension=self.dimension_input.currentText(),
            description=self.description_input.toPlainText(),
        )

        self.accept()


class DBUpdateWindow(BaseDBDialogWindow):

    def __init__(
        self,
        parent: QWidget,
        logic_for_db: LogicDBWindowProtocol,
        row: RowViewProtocol,
    ):
        self.row = row
        super().__init__(parent, logic_for_db)

    def initUI(self):
        self.setWindowTitle('Изменить предмет')
        self._initUI()

        self.id_item = self.row.id
        self.name_input.setText(self.row.name)
        self.description_input.setText(self.row.description)
        self.quantity_input.setValue(1)
        self.price_input.setValue(float(self.row.price))

        index_dimension = self.dimension_input.findText(
            self.row.dimension, Qt.MatchFlag.MatchFixedString
        )
        if index_dimension >= 0:
            self.dimension_input.setCurrentIndex(index_dimension)

        self.exec()

    def perform_action(self):
        self.update_item()

    def update_item(self):
        if not self.validate_form():
            return

        self.logic_for_db.update(
            id_item=self.id_item,
            name=self.name_input.text(),
            quantity=self.quantity_input.value(),
            price=self.price_input.value(),
            dimension=self.dimension_input.currentText(),
            description=self.description_input.toPlainText(),
        )

        self.accept()
