from PySide6.QtCore import QAbstractTableModel, Qt, Signal
import pandas as pd


class InitialDataModel(QAbstractTableModel):
    def __init__(self, data, file_path):
        super().__init__()

        self.data = data
        self.file_path = file_path