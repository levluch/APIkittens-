from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal

from desktop.initial_data_page import InitialDataPage
from desktop.navigation_menu import NavigationMenu
from desktop.results_data_page import ResultsDataPage
from desktop.results_visual_page import ResultsVisualPage
from desktop.ui_py.ui_main_window import Ui_MainWindow
from desktop.solver import run_scheduler


class SolverThread(QThread):
    calculation_finished = Signal(list, str)

    def __init__(self, input_lines):
        super().__init__()
        self.input_lines = input_lines

    def run(self):
        try:
            result = run_scheduler(self.input_lines)
            self.calculation_finished.emit(result, "")
        except Exception as e:
            self.calculation_finished.emit([], f"Ошибка при выполнении расчёта: {str(e)}")


class MainWindow(QMainWindow, Ui_MainWindow):
    data_calculated = Signal(list, list, list)

    def __init__(self):
        super().__init__()

        self.results_visual_page = None
        self.results_page = None
        self.page_initial = None
        self.stacked_widget = None
        self.navigation_menu = None
        self.solver_thread = None
        self.operations = []
        self.robot_bases = []

        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.navigation_menu = NavigationMenu()
        self.horizontalLayout.addWidget(self.navigation_menu)

        self.setWindowIcon(QIcon('res/logo.jpg'))

        self.stacked_widget = QStackedWidget()
        self.page_initial = InitialDataPage()
        self.results_visual_page = ResultsVisualPage()
        self.results_page = ResultsDataPage()

        self.stacked_widget.addWidget(self.page_initial)
        self.stacked_widget.addWidget(self.results_visual_page)
        self.stacked_widget.addWidget(self.results_page)

        self.horizontalLayout.addWidget(self.stacked_widget)

        self.navigation_menu.initial_data_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )
        self.navigation_menu.visualisation_information_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(1)
        )
        self.navigation_menu.output_data_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(2)
        )
        self.navigation_menu.exit_button.clicked.connect(self.close)

        self.page_initial.calculate_triggered.connect(self.recalculate_solver)
        self.data_calculated.connect(self.display_results)

    def recalculate_solver(self, operations, robot_bases):
        if not self.page_initial.file_path:
            return
        self.operations = operations
        self.robot_bases = robot_bases
        content = self.page_initial.plainTextEdit.toPlainText()
        input_lines = content.splitlines()
        self.solver_thread = SolverThread(input_lines)
        self.solver_thread.calculation_finished.connect(self.on_calculation_finished)
        self.solver_thread.start()

    def on_calculation_finished(self, results, error_message):
        if error_message:
            QMessageBox.warning(self, 'Внимание', error_message)
        else:
            self.data_calculated.emit(results, self.operations, self.robot_bases)

    def display_results(self, results, operations, robot_bases):
        self.results_page.display_results('\n'.join(results))
        self.results_visual_page.display_results(results, operations, robot_bases)

        QMessageBox.information(
            self,
            'Расчет завершен',
            'Расчет успешно завершен, вы можете проверить результат во вкладках "Визуализация" и "Выходные данные"',
        )