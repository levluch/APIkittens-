from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtGui import QIcon

from desktop.initial_data_page import InitialDataPage
from desktop.navigation_menu import NavigationMenu
from desktop.ui_py.ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.page_initial = None
        self.stacked_widget = None
        self.navigation_menu = None

        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.navigation_menu = NavigationMenu()
        self.horizontalLayout.addWidget(self.navigation_menu)

        self.setWindowIcon(QIcon('res/logo.jpg'))

        self.stacked_widget = QStackedWidget()
        self.page_initial = InitialDataPage()

        self.stacked_widget.addWidget(self.page_initial)

        self.horizontalLayout.addWidget(self.stacked_widget)

        self.navigation_menu.initial_data_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )
