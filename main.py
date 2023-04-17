from PyQt6.QtWidgets import QApplication
from src.main_window import *

app = QApplication([])
window = MainWindow()
window.show()

app.exec()