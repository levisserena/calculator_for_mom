from PyQt6.QtWidgets import QApplication

from app.windows.main import MainWindow
from app.db.repository import start

app = QApplication([])
window = MainWindow()


if __name__ == '__main__':
    start.create_table()
    app.exec()
