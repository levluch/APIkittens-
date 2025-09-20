# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'results_visual_pagemyYPcP.ui'
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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSlider,
    QVBoxLayout, QWidget)

class Ui_results_visual_page(object):
    def setupUi(self, results_visual_page):
        if not results_visual_page.objectName():
            results_visual_page.setObjectName(u"results_visual_page")
        results_visual_page.resize(601, 478)
        self.verticalLayout = QVBoxLayout(results_visual_page)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.graphicsView = QGraphicsView(results_visual_page)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)

        self.groupBox = QGroupBox(results_visual_page)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.reset_pushButton = QPushButton(self.groupBox)
        self.reset_pushButton.setObjectName(u"reset_pushButton")

        self.horizontalLayout.addWidget(self.reset_pushButton)

        self.play_pushButton = QPushButton(self.groupBox)
        self.play_pushButton.setObjectName(u"play_pushButton")

        self.horizontalLayout.addWidget(self.play_pushButton)

        self.pause_pushButton = QPushButton(self.groupBox)
        self.pause_pushButton.setObjectName(u"pause_pushButton")

        self.horizontalLayout.addWidget(self.pause_pushButton)

        self.time_horizontalSlider = QSlider(self.groupBox)
        self.time_horizontalSlider.setObjectName(u"time_horizontalSlider")
        self.time_horizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout.addWidget(self.time_horizontalSlider)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.makespan_label = QLabel(self.groupBox)
        self.makespan_label.setObjectName(u"makespan_label")

        self.verticalLayout_2.addWidget(self.makespan_label)

        self.time_label = QLabel(self.groupBox)
        self.time_label.setObjectName(u"time_label")

        self.verticalLayout_2.addWidget(self.time_label)


        self.horizontalLayout.addLayout(self.verticalLayout_2)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(results_visual_page)

        QMetaObject.connectSlotsByName(results_visual_page)
    # setupUi

    def retranslateUi(self, results_visual_page):
        results_visual_page.setWindowTitle(QCoreApplication.translate("results_visual_page", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("results_visual_page", u"\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0430\u043d\u0438\u043c\u0430\u0446\u0438\u0435\u0439", None))
        self.reset_pushButton.setText(QCoreApplication.translate("results_visual_page", u"\u0421\u0431\u0440\u043e\u0441", None))
        self.play_pushButton.setText(QCoreApplication.translate("results_visual_page", u"\u041f\u0443\u0441\u043a", None))
        self.pause_pushButton.setText(QCoreApplication.translate("results_visual_page", u"\u041f\u0430\u0443\u0437\u0430", None))
        self.makespan_label.setText("")
        self.time_label.setText("")
    # retranslateUi

