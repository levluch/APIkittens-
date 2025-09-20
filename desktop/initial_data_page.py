from PySide6.QtWidgets import QWidget, QMessageBox, QFileDialog, QSizePolicy
from PySide6.QtCore import QThread, Signal, QTimer

from ui_py.ui_initial_data_page import Ui_initial_data_page


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
    calculate_triggered = Signal(list, list)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.file_path = None
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_file)

        self.init_ui()

    def init_ui(self):
        self.select_file_button.clicked.connect(self.select_file_handler)
        self.calculate_button.clicked.connect(self.handle_calculate)
        self.plainTextEdit.textChanged.connect(self.on_text_changed)
        self.plainTextEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def select_file_handler(self):
        try:
            self.select_file()
        except IOError:
            QMessageBox.warning(self, 'Внимание', 'Ошибка при чтении файла')
        except ValueError:
            QMessageBox.warning(self, 'Внимание', 'Ошибка в формате данных файла')

    def select_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Text Files (*.txt)")
        if fname:
            self.filename_label.setText(fname)
            self.file_path = fname
            with open(fname, 'r', encoding='utf-8') as f:
                content = f.read()
                self.plainTextEdit.setPlainText(content)

    def handle_calculate(self):
        if not self.file_path:
            QMessageBox.warning(self, 'Внимание', 'Сначала выберите файл')
            return
        content = self.plainTextEdit.toPlainText()
        try:
            operations, robot_bases = self.parse_input_data(content)
            self.calculate_triggered.emit(operations, robot_bases)
        except ValueError:
            QMessageBox.warning(self, 'Внимание', 'Ошибка в формате данных файла')

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

    def parse_input_data(self, content):
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            return [], []
        try:
            num_robots, num_operations = map(int, lines[0].split())
            idx = 1
            robot_bases = [tuple(map(float, lines[idx + i].split())) for i in range(num_robots)]
            idx += num_robots
            idx += 6
            idx += 1
            operations = []
            for i in range(num_operations):
                vals = list(map(float, lines[idx + i].split()))
                operations.append({'pick': tuple(vals[0:3]), 'place': tuple(vals[3:6]), 't_i': vals[6]})
            return operations, robot_bases
        except (ValueError, IndexError):
            raise ValueError("Некорректный формат входных данных")
