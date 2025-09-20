from PySide6.QtWidgets import QWidget

from desktop.ui_py.ui_results_visual_page import Ui_results_visual_page


class ResultsVisualPage(QWidget, Ui_results_visual_page):
    def __init__(self):
        super(ResultsVisualPage, self).__init__()

        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        pass
