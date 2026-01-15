from PyQt6.QtGui import QAction
import sys
from PyQt6.QtCore import Qt, QAbstractTableModel
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
    QMenu,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
)


# 1. Создаем модель данных для таблицы
class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()])

        # Выделение выбранной строки цветом
        if role == Qt.ItemDataRole.BackgroundRole:
            if index.row() % 2 == 0:
                return Qt.GlobalColor.lightGray
        return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        if self._data:
            return len(self._data[0])
        return 0

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                headers = ['ID', 'Название', 'Количество', 'Цена', 'Дата']
                return headers[section]
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_data()

    def initUI(self):
        self.setWindowTitle('Управление товарами')
        self.setGeometry(100, 100, 900, 600)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QHBoxLayout()

        # Левая панель с таблицей
        left_panel = QVBoxLayout()

        # Создаем таблицу с моделью
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)  # Выделение строк
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)     # Одна строка за раз
        self.table_view.setAlternatingRowColors(True)  # Чередование цветов строк
        self.table_view.setSortingEnabled(True)        # Включить сортировку

        left_panel.addWidget(self.table_view)

        # Правая панель с кнопками
        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Кнопки управления
        btn_add = QPushButton('Добавить')
        btn_add.clicked.connect(self.add_item)
        btn_add.setMinimumHeight(40)

        btn_edit = QPushButton('Редактировать')
        btn_edit.clicked.connect(self.edit_item)
        btn_edit.setMinimumHeight(40)

        btn_delete = QPushButton('Удалить')
        btn_delete.clicked.connect(self.delete_item)
        btn_delete.setMinimumHeight(40)
        btn_delete.setStyleSheet("background-color: #ff6b6b; color: white;")

        btn_refresh = QPushButton('Обновить')
        btn_refresh.clicked.connect(self.load_data)
        btn_refresh.setMinimumHeight(40)

        # Информация о выделенной строке
        self.info_label = QLabel('Выделено строк: 0')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("padding: 10px; background-color: #f0f0f0;")

        # Подключаем сигнал выделения строк
        if self.table_view.selectionModel():
            self.table_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Добавляем виджеты в правую панель
        right_panel.addWidget(QLabel('Действия:'))
        right_panel.addWidget(btn_add)
        right_panel.addWidget(btn_edit)
        right_panel.addWidget(btn_delete)
        right_panel.addWidget(btn_refresh)
        right_panel.addSpacing(20)
        right_panel.addWidget(self.info_label)
        right_panel.addStretch()

        # Создаем панель поиска
        search_panel = QHBoxLayout()
        search_panel.addWidget(QLabel('Поиск:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Введите текст...')
        self.search_input.textChanged.connect(self.filter_data)
        search_panel.addWidget(self.search_input)

        left_panel.addLayout(search_panel)

        # Собираем все вместе
        main_layout.addLayout(left_panel, 4)  # 80% ширины
        main_layout.addLayout(right_panel, 1)  # 20% ширины

        central_widget.setLayout(main_layout)

        # Создаем контекстное меню
        self.create_context_menu()

        # Подключаем двойной клик для редактирования
        self.table_view.doubleClicked.connect(self.on_double_click)

    def create_context_menu(self):
        """Создаем контекстное меню для таблицы"""
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)

        # Создаем меню
        self.context_menu = QMenu(self)

        self.edit_action = QAction('Редактировать', self)
        self.edit_action.triggered.connect(self.edit_item)

        self.delete_action = QAction('Удалить', self)
        self.delete_action.triggered.connect(self.delete_item)

        self.copy_action = QAction('Копировать', self)
        self.copy_action.triggered.connect(self.copy_item)

        self.context_menu.addAction(self.edit_action)
        self.context_menu.addAction(self.delete_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.copy_action)

    def show_context_menu(self, position):
        """Показываем контекстное меню"""
        index = self.table_view.indexAt(position)
        if index.isValid():
            self.context_menu.exec(self.table_view.viewport().mapToGlobal(position))

    def load_data(self, filter_text=''):
        """Загрузка данных из БД (заглушка - в реальности подключите вашу БД)"""
        # Пример данных (в реальности загружайте из БД)
        data = [
            [1, 'Молоко', 10, 85.50, '2024-01-15'],
            [2, 'Хлеб', 25, 45.00, '2024-01-14'],
            [3, 'Яйца', 15, 120.00, '2024-01-13'],
            [4, 'Сахар', 8, 65.00, '2024-01-12'],
            [5, 'Масло', 12, 180.00, '2024-01-11'],
            [6, 'Сыр', 7, 350.00, '2024-01-10'],
            [7, 'Кофе', 9, 450.00, '2024-01-09'],
            [8, 'Чай', 20, 120.00, '2024-01-08'],
        ]

        # Фильтрация данных
        if filter_text:
            filtered_data = []
            for row in data:
                if any(filter_text.lower() in str(cell).lower() for cell in row):
                    filtered_data.append(row)
            data = filtered_data

        # Устанавливаем модель данных
        self.model = TableModel(data)
        self.table_view.setModel(self.model)

        # Настраиваем ширину колонок
        self.table_view.horizontalHeader().setStretchLastSection(True)
        for i in range(self.model.columnCount(None)):
            self.table_view.setColumnWidth(i, 150)

    def filter_data(self):
        """Фильтрация данных по тексту поиска"""
        self.load_data(self.search_input.text())

    def on_selection_changed(self):
        """Обработка изменения выделения"""
        selected = self.table_view.selectionModel().selectedRows()
        self.info_label.setText(f'Выделено строк: {len(selected)}')

        # Показываем информацию о выделенной строке
        if selected:
            index = selected[0]
            row = index.row()
            data = self.model._data[row]
            self.info_label.setText(f'Выбрано: {data[1]}, Цена: {data[3]} руб.')

    def get_selected_row_data(self):
        """Получить данные выделенной строки"""
        selected = self.table_view.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            return self.model._data[row]
        return None

    def add_item(self):
        """Добавление новой записи"""
        dialog = QDialog(self)
        dialog.setWindowTitle('Добавить товар')

        layout = QFormLayout()

        name_input = QLineEdit()
        quantity_input = QSpinBox()
        quantity_input.setRange(0, 1000)
        price_input = QDoubleSpinBox()
        price_input.setRange(0, 100000)
        price_input.setPrefix('₽ ')

        layout.addRow('Название:', name_input)
        layout.addRow('Количество:', quantity_input)
        layout.addRow('Цена:', price_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addRow(buttons)
        dialog.setLayout(layout)

        if dialog.exec():
            # Здесь добавьте код для сохранения в БД
            QMessageBox.information(self, 'Успех',
                                   f'Добавлено: {name_input.text()}\n'
                                   f'Количество: {quantity_input.value()}\n'
                                   f'Цена: {price_input.value()} руб.')
            self.load_data()  # Обновляем таблицу

    def edit_item(self):
        """Редактирование выделенной записи"""
        data = self.get_selected_row_data()
        if not data:
            QMessageBox.warning(self, 'Ошибка', 'Выберите строку для редактирования')
            return

        dialog = QDialog(self)
        dialog.setWindowTitle('Редактировать товар')

        layout = QFormLayout()

        name_input = QLineEdit(str(data[1]))
        quantity_input = QSpinBox()
        quantity_input.setValue(int(data[2]))
        quantity_input.setRange(0, 1000)

        price_input = QDoubleSpinBox()
        price_input.setValue(float(data[3]))
        price_input.setRange(0, 100000)
        price_input.setPrefix('₽ ')

        layout.addRow('Название:', name_input)
        layout.addRow('Количество:', quantity_input)
        layout.addRow('Цена:', price_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addRow(buttons)
        dialog.setLayout(layout)

        if dialog.exec():
            # Здесь добавьте код для обновления в БД
            QMessageBox.information(self, 'Успех', 'Данные обновлены')
            self.load_data()  # Обновляем таблицу

    def delete_item(self):
        """Удаление выделенной записи"""
        data = self.get_selected_row_data()
        if not data:
            QMessageBox.warning(self, 'Ошибка', 'Выберите строку для удаления')
            return

        reply = QMessageBox.question(self, 'Подтверждение',
                                    f'Удалить "{data[1]}"?',
                                    QMessageBox.StandardButton.Yes | 
                                    QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Здесь добавьте код для удаления из БД
            QMessageBox.information(self, 'Успех', f'Удалено: {data[1]}')
            self.load_data()  # Обновляем таблицу

    def copy_item(self):
        """Копирование данных выделенной строки"""
        data = self.get_selected_row_data()
        if data:
            text = '\t'.join(str(x) for x in data)
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, 'Скопировано', 'Данные скопированы в буфер')

    def on_double_click(self, index):
        """Редактирование по двойному клику"""
        self.edit_item()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
