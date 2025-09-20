# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'navigation_menuXDWHiH.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_navigation_menu(object):
    def setupUi(self, navigation_menu):
        if not navigation_menu.objectName():
            navigation_menu.setObjectName(u"navigation_menu")
        navigation_menu.resize(250, 559)
        navigation_menu.setMinimumSize(QSize(200, 0))
        navigation_menu.setMaximumSize(QSize(250, 16777215))
        self.gridLayout = QGridLayout(navigation_menu)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea = QScrollArea(navigation_menu)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMinimumSize(QSize(200, 0))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 230, 539))
        self.gridLayout_2 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.initial_data_button = QPushButton(self.scrollAreaWidgetContents)
        self.initial_data_button.setObjectName(u"initial_data_button")

        self.verticalLayout.addWidget(self.initial_data_button)

        self.visualisation_information_button = QPushButton(self.scrollAreaWidgetContents)
        self.visualisation_information_button.setObjectName(u"visualisation_information_button")

        self.verticalLayout.addWidget(self.visualisation_information_button)

        self.output_data_button = QPushButton(self.scrollAreaWidgetContents)
        self.output_data_button.setObjectName(u"output_data_button")

        self.verticalLayout.addWidget(self.output_data_button)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")

        self.verticalLayout.addLayout(self.gridLayout_3)

        self.switch_theme_button = QPushButton(self.scrollAreaWidgetContents)
        self.switch_theme_button.setObjectName(u"switch_theme_button")

        self.verticalLayout.addWidget(self.switch_theme_button)

        self.exit_button = QPushButton(self.scrollAreaWidgetContents)
        self.exit_button.setObjectName(u"exit_button")

        self.verticalLayout.addWidget(self.exit_button)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)


        self.retranslateUi(navigation_menu)

        QMetaObject.connectSlotsByName(navigation_menu)
    # setupUi

    def retranslateUi(self, navigation_menu):
        navigation_menu.setWindowTitle(QCoreApplication.translate("navigation_menu", u"Form", None))
        self.initial_data_button.setText(QCoreApplication.translate("navigation_menu", u"\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0434\u0430\u043d\u043d\u044b\u0445", None))
        self.visualisation_information_button.setText(QCoreApplication.translate("navigation_menu", u"\u0412\u0438\u0437\u0443\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f", None))
        self.output_data_button.setText(QCoreApplication.translate("navigation_menu", u"\u0412\u044b\u0445\u043e\u0434\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435", None))
        self.switch_theme_button.setText(QCoreApplication.translate("navigation_menu", u"\u041f\u0435\u0440\u0435\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u0442\u0435\u043c\u044b", None))
        self.exit_button.setText(QCoreApplication.translate("navigation_menu", u"\u0412\u044b\u0445\u043e\u0434", None))
    # retranslateUi

