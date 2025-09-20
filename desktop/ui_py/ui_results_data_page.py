# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'results_data_pageJPMeWb.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QPushButton,
    QSizePolicy, QTextBrowser, QWidget)

class Ui_results_data_page(object):
    def setupUi(self, results_data_page):
        if not results_data_page.objectName():
            results_data_page.setObjectName(u"results_data_page")
        results_data_page.resize(739, 550)
        self.gridLayout = QGridLayout(results_data_page)
        self.gridLayout.setObjectName(u"gridLayout")
        self.save_file_button = QPushButton(results_data_page)
        self.save_file_button.setObjectName(u"save_file_button")

        self.gridLayout.addWidget(self.save_file_button, 1, 0, 1, 1)

        self.label_2 = QLabel(results_data_page)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 2)

        self.filename_label = QLabel(results_data_page)
        self.filename_label.setObjectName(u"filename_label")

        self.gridLayout.addWidget(self.filename_label, 1, 1, 1, 1)

        self.textBrowser = QTextBrowser(results_data_page)
        self.textBrowser.setObjectName(u"textBrowser")

        self.gridLayout.addWidget(self.textBrowser, 2, 0, 1, 1)


        self.retranslateUi(results_data_page)

        QMetaObject.connectSlotsByName(results_data_page)
    # setupUi

    def retranslateUi(self, results_data_page):
        results_data_page.setWindowTitle(QCoreApplication.translate("results_data_page", u"Form", None))
        self.save_file_button.setText(QCoreApplication.translate("results_data_page", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0432 txt", None))
        self.label_2.setText(QCoreApplication.translate("results_data_page", u"\u0412\u044b\u0445\u043e\u0434\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435", None))
        self.filename_label.setText("")
    # retranslateUi

