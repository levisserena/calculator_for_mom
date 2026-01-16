from abc import abstractmethod
from typing import TYPE_CHECKING, Union

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QWidget,
)

if TYPE_CHECKING:
    from app.logic.adapter import LogicDBWindow, LogicMainWindow
    from app.models import (
        RowViewOnDBTable,
        RowViewOnMainTable,
        ViewOnDBTableModels,
    )
    from app.windows.main import MainWindow


class BaseRowWindow(QDialog):
    """Базовое окно для создания и изменения строк."""

    def __init__(
        self,
        parent: QWidget,
        logic_for_main: 'LogicMainWindow',
        logic_for_db: 'LogicDBWindow',
        row_for_main: type['RowViewOnMainTable'],
        model_for_db: type['ViewOnDBTableModels'],
    ) -> None:
        super().__init__(parent)
        self.logic_for_main = logic_for_main
        self.logic_for_db = logic_for_db
        self.row_for_main = row_for_main
        self.model_for_db = model_for_db
        self.cursor_row_db: Union['RowViewOnDBTable', None]
        self.initUI()

    @abstractmethod
    def initUI(self) -> None:
        """Инициация пользовательского интерфейса."""
        pass

    def _initUI(self) -> None:
        """Часть инициации пользовательского интерфейса."""
        self.setGeometry(320, 420, 400, 120)

        main_layout = QFormLayout()
        layout_top = QHBoxLayout()

        self.label = QLabel()
        self.button_choice = QPushButton('Выбрать')
        self.button_choice.clicked.connect(self.choice_item)
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0, 10_000_000)
        self.quantity_input.setDecimals(4)
        self.dimension_input = QComboBox()

        layout_top.addWidget(self.label, stretch=2)
        layout_top.addWidget(self.button_choice, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._perform_action)
        buttons.rejected.connect(self.reject)

        for name, widget in (
            ('Название', layout_top),
            ('Количество', self.quantity_input),
            ('Размерность', self.dimension_input),
            ('', buttons),
        ):
            main_layout.addRow(name, widget)

        self.setLayout(main_layout)

    def _perform_action(self):
        """Выполнение действия окна."""
        if not self.validate_form():
            return

        if self.cursor_row_db is None:
            return

        price = self.logic_for_db.calculation(
            price=self.cursor_row_db.price,
            quantity=self.quantity_input.value(),
            current_dimension=self.dimension_input.currentText(),
            db_dimension=self.cursor_row_db.dimension,
        )
        item = self.row_for_main(
            id=self.cursor_row_db.id,
            name=self.cursor_row_db.name,
            quantity=self.quantity_input.value(),
            dimension=self.dimension_input.currentText(),
            price=price,
        )

        self.perform_action(item)

        parent: 'MainWindow' = self.parent()  # type: ignore
        parent.load_data()

        self.accept()

    @abstractmethod
    def perform_action(self, item: 'RowViewOnMainTable') -> None:
        """Выполнить действие окна."""
        pass

    def validate_form(self) -> bool:
        """Валидирование заполнение формы окна."""
        if self.quantity_input.value() == 0:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Количество должно быть больше 0!',
            )
            return False
        return True

    def choice_item(self) -> None:
        """Откроет окно с выбором ингредиента из базы данных."""
        self.window_choice_item = WindowChoiceItem(
            parent=self,
            logic_for_db=self.logic_for_db,
            model_for_db=self.model_for_db,
        )


class AddRowWindow(BaseRowWindow):
    """Окно добавления строчки в таблицу на главном окне."""

    def initUI(self) -> None:
        """Инициация пользовательского интерфейса."""
        self.setWindowTitle('Добавить')
        self._initUI()
        self.exec()

    def perform_action(self, item: 'RowViewOnMainTable') -> None:
        """Выполнить действие окна."""
        self.logic_for_main.add(item)


class UpdateRowWindow(BaseRowWindow):
    """Окно изменения строчки в таблицу на главном окне."""

    def __init__(
        self,
        parent: QWidget,
        logic_for_main: 'LogicMainWindow',
        logic_for_db: 'LogicDBWindow',
        row_for_main: type['RowViewOnMainTable'],
        model_for_db: type['ViewOnDBTableModels'],
        index_row: int,
    ) -> None:
        self.index_row = index_row
        self.cursor_row_main: Union['RowViewOnMainTable', None]
        super().__init__(
            parent, logic_for_main, logic_for_db, row_for_main, model_for_db
        )

    def initUI(self) -> None:
        """Инициация пользовательского интерфейса."""
        self.setWindowTitle('Изменить')
        self._initUI()
        self.load_data()
        self.exec()

    def load_data(self) -> None:
        """Обновление данных в таблице окна."""
        self.cursor_row_main = self.logic_for_main.get(self.index_row)
        self.cursor_row_db = self.logic_for_db.get(self.cursor_row_main.id)

        if self.cursor_row_main is not None:
            self.label.setText(self.cursor_row_main.name)
            self.quantity_input.setValue(self.cursor_row_main.quantity)
            dimensions = (
                self.logic_for_db.dimension.get_dimensions_same_category(
                    self.cursor_row_main.dimension
                )
            )
            self.dimension_input.addItems(dimensions)  # type: ignore
            self.dimension_input.setCurrentText(self.cursor_row_main.dimension)

    def perform_action(self, item: 'RowViewOnMainTable') -> None:
        """Выполнить действие окна."""
        self.logic_for_main.update(self.index_row, item)


class WindowChoiceItem(QDialog):
    """Окно выбора ингредиента из базы данных."""

    def __init__(
        self,
        parent: QWidget,
        logic_for_db: 'LogicDBWindow',
        model_for_db: type['ViewOnDBTableModels'],
    ) -> None:
        super().__init__(parent)
        self.logic_for_db = logic_for_db
        self.model_for_db = model_for_db
        self.initUI()

    def initUI(self) -> None:
        """Инициация пользовательского интерфейса."""
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
        if header:
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

    def load_data(self) -> None:
        """Обновление данных в таблице окна."""
        data = self.logic_for_db.get_all()
        model = self.model_for_db(data)
        self.table_view.setModel(model)
        self.table_view.hideColumn(0)

    def get_item(self) -> None:
        """
        Добавит ингредиент в окно добавления строчки в таблицу на главном окне.
        """
        parent: 'BaseRowWindow' = self.parent()  # type: ignore
        if parent is None:
            return
        parent.cursor_row_db = self.get_selected_row()
        if parent.cursor_row_db is None:
            return
        parent.label.setText(parent.cursor_row_db.name)
        dimensions = self.logic_for_db.dimension.get_dimensions_same_category(
            parent.cursor_row_db.dimension
        )
        parent.dimension_input.addItems(dimensions)  # type: ignore
        parent.dimension_input.setCurrentText(parent.cursor_row_db.dimension)
        self.accept()

    def get_selected_row(self) -> Union['RowViewOnDBTable', None]:
        """Вернет выделенную строку из таблицы (модель)."""
        selected = self.table_view.selectionModel().selectedRows()  # type: ignore
        if selected:
            row = selected[0].row()
            model = self.table_view.model()
            if isinstance(model, self.model_for_db):
                return model.get_row(row)
        return None
