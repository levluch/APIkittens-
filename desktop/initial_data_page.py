import pandas as pd
from PySide6.QtWidgets import QWidget, QMessageBox, QFileDialog

from desktop.ui_py.ui_initial_data_page import Ui_initial_data_page


class InitialDataPage(QWidget, Ui_initial_data_page):
    def __init__(self):
        super(InitialDataPage, self).__init__()

        self.file_path = None

        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.select_file_button.clicked.connect(self.select_file_handler)

    def select_file_handler(self):
        try:
            self.select_file()
        except IOError:
            QMessageBox.warning(
                self,
                'Внимание',
                'Неправильный формат файла'
            )

    def select_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Выберите XLSX", "", "XLSX Files (*.xlsx)")
        if fname:
            self.filename_label.setText(fname)
            self.file_path = fname  # Сохраняем путь к файлу
