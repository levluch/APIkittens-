from PySide6.QtWidgets import QWidget, QMessageBox, QFileDialog, QSizePolicy
from PySide6.QtCore import QThread, Signal, QTimer

from desktop.ui_py.ui_initial_data_page import Ui_initial_data_page


class SaveFileThread(QThread):
    save_finished = Signal(bool, str)

    def __init__(self, file_path, content):
        super().__init__()
        self.file_path = file_path
        self.content = content

    def run(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            self.save_finished.emit(True, "Файл успешно сохранён")
        except IOError as e:
            self.save_finished.emit(False, f"Ошибка при сохранении файла: {str(e)}")


class InitialDataPage(QWidget, Ui_initial_data_page):
    data_changed = Signal()

    def __init__(self):
        super(InitialDataPage, self).__init__()

        self.file_path = None
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_file)

        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.select_file_button.clicked.connect(self.select_file_handler)
        self.plainTextEdit.textChanged.connect(self.on_text_changed)

        self.plainTextEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def select_file_handler(self):
        try:
            self.select_file()
        except IOError:
            QMessageBox.warning(
                self,
                'Внимание',
                'Ошибка при чтении файла'
            )

    def select_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Text Files (*.txt)")
        if fname:
            self.filename_label.setText(fname)
            self.file_path = fname
            with open(fname, 'r', encoding='utf-8') as f:
                self.plainTextEdit.setPlainText(f.read())

            self.data_changed.emit()

    def on_text_changed(self):
        if self.file_path:
            self.save_timer.start(2000)

    def save_file(self):
        if not self.file_path:
            return
        content = self.plainTextEdit.toPlainText()
        self.save_thread = SaveFileThread(self.file_path, content)
        self.save_thread.save_finished.connect(self.on_save_finished)
        self.save_thread.start()

    def on_save_finished(self, success, message):
        if not success:
            QMessageBox.warning(self, 'Внимание', message)

        else:
            self.data_changed.emit()
