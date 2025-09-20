import qdarktheme
from PySide6.QtWidgets import QPushButton, QApplication, QWidget
from PySide6.QtCore import Slot

from desktop.ui_py.ui_navigation_menu import Ui_navigation_menu


class NavigationMenu(QWidget, Ui_navigation_menu):
    def __init__(self):
        super(NavigationMenu, self).__init__()
        self.setupUi(self)

        self.theme = 'light'

        self.switch_theme_button.clicked.connect(self._change_theme)

    @Slot()
    def _change_theme(self) -> None:
        if self.theme == 'light':
            self.theme = 'dark'

        else:
            self.theme = 'light'

        QApplication.instance().setStyleSheet(qdarktheme.load_stylesheet(self.theme))
