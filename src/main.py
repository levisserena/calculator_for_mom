from PyQt6.QtWidgets import QApplication

from app.db.repository import start
from app.windows.main import MainWindow

app = QApplication([])
window = MainWindow()


if __name__ == '__main__':
    start.create_table()
    app.exec()
