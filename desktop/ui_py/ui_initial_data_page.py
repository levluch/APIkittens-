# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'initial_data_pageyKcnRC.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QTableView, QWidget)

class Ui_initial_data_page(object):
    def setupUi(self, initial_data_page):
        if not initial_data_page.objectName():
            initial_data_page.setObjectName(u"initial_data_page")
        initial_data_page.resize(739, 550)
        self.gridLayout = QGridLayout(initial_data_page)
        self.gridLayout.setObjectName(u"gridLayout")
        self.data_table = QTableView(initial_data_page)
        self.data_table.setObjectName(u"data_table")

        self.gridLayout.addWidget(self.data_table, 3, 0, 1, 2)

        self.filename_label = QLabel(initial_data_page)
        self.filename_label.setObjectName(u"filename_label")

        self.gridLayout.addWidget(self.filename_label, 1, 1, 1, 1)

        self.label_2 = QLabel(initial_data_page)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 2)

        self.select_file_button = QPushButton(initial_data_page)
        self.select_file_button.setObjectName(u"select_file_button")

        self.gridLayout.addWidget(self.select_file_button, 1, 0, 1, 1)


        self.retranslateUi(initial_data_page)

        QMetaObject.connectSlotsByName(initial_data_page)
    # setupUi

    def retranslateUi(self, initial_data_page):
        initial_data_page.setWindowTitle(QCoreApplication.translate("initial_data_page", u"Form", None))
        self.filename_label.setText("")
        self.label_2.setText(QCoreApplication.translate("initial_data_page", u"\u0418\u0441\u0445\u043e\u0434\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435", None))
        self.select_file_button.setText(QCoreApplication.translate("initial_data_page", u"\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0444\u0430\u0439\u043b", None))
    # retranslateUi

