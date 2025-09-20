from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox

from ui_py.ui_results_data_page import Ui_results_data_page


class ResultsDataPage(QWidget, Ui_results_data_page):
    def __init__(self):
        super(ResultsDataPage, self).__init__()

        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.save_file_button.clicked.connect(self.save_file)

    def display_results(self, results):
        self.textBrowser.setText(results)

    def save_file(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Выберите файл", "", "Text Files (*.txt)")
        if fname:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(str(self.plainTextEdit.toPlainText()))

            self.filename_label.setText(f'Сохранено в: {fname}')

            QMessageBox.information(
                self,
                'Данные сохранены',
                'Данные успешно сохранены',
            )

    def select_file_handler(self):
        try:
            self.select_file()
        except IOError:
            QMessageBox.warning(
                self,
                'Внимание',
                'Ошибка при чтении файла'
            )
