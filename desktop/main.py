import sys
import qdarktheme
from PySide6.QtWidgets import QApplication

from desktop.main_window import MainWindow


def hook(a, b, c):
    sys.__excepthook__(a, b, c)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet(theme='light'))
    win = MainWindow()
    win.show()
    sys.excepthook = hook
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
