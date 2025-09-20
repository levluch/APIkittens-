from PySide6.QtWidgets import QMainWindow

from desktop.ui_py.ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        pass
