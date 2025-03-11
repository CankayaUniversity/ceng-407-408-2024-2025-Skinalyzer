from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTableView, QTextBrowser, QVBoxLayout,
    QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(832, 616)
        Widget.setStyleSheet("QWidget#Widget { background-color: white; }")

        self.scrollArea = QScrollArea(Widget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(0, 0, 832, 868))
        self.scrollArea.setStyleSheet("QScrollArea { background-color: white; }")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 832, 2000))
        self.scrollAreaWidgetContents.setStyleSheet("QWidget#scrollAreaWidgetContents { background-color: white; }")

        self.layoutWidget_2 = QWidget(self.scrollAreaWidgetContents)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(40, 16, 781, 91))
        self.horizontalLayout_5 = QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_33 = QLabel(self.layoutWidget_2)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setStyleSheet(u"font: 600 9pt \"Segoe UI\";")
        self.label_33.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        


        self.horizontalLayout_5.addWidget(self.label_33)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_13)

        self.about_us = QLabel(self.layoutWidget_2)
        self.about_us.setObjectName(u"about_us")
        self.about_us.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_5.addWidget(self.about_us)
        self.about_us.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)



        self.horizontalSpacer_14 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_14)

        self.contact = QLabel(self.layoutWidget_2)
        self.contact.setObjectName(u"contact")
        self.contact.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_5.addWidget(self.contact)

        self.horizontalSpacer_15 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_15)

        self.Profil = QLabel(self.layoutWidget_2)
        self.Profil.setObjectName(u"Profil")
        self.Profil.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_5.addWidget(self.Profil)

        self.tableView = QTableView(self.scrollAreaWidgetContents)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setGeometry(QRect(0, 0, 831, 101))
        self.tableView.setStyleSheet(u"background-color: rgb(157, 81, 113);")
        self.tableView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(60, 160, 731, 411))
        self.frame.setStyleSheet(u"QFrame {\n"
"    border-radius: 15px;\n"
"    background-color: #dcdcdc;  /* Daha gri renk */\n"
"    \n"
"\n"
"    border: 1px solid #b0b0b0;  /* Hafif gri kenar */\n"
"    padding: 5px;\n"
"}\n"
"")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layoutWidget_6 = QWidget(self.frame)
        self.layoutWidget_6.setObjectName(u"layoutWidget_6")
        self.layoutWidget_6.setGeometry(QRect(20, 20, 316, 201))
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget_6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_37 = QLabel(self.layoutWidget_6)
        self.label_37.setObjectName(u"label_37")
        self.label_37.setStyleSheet(u"QLabel {\n"
"	font: 600 12pt \"Segoe UI\";\n"
"    border: none;\n"
"    border-radius: 0;\n"
"    padding: 0;\n"
"    color: rgb(0, 0, 0);\n"
"}\n"
"")

        self.verticalLayout_3.addWidget(self.label_37)

        self.verticalSpacer_13 = QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_13)

        self.verticalSpacer_14 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_14)

        self.label_38 = QLabel(self.layoutWidget_6)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setStyleSheet(u"QLabel {\n"
"	font: 9pt \"Segoe UI\";\n"
"	\n"
"    border: none;\n"
"    border-radius: 0;\n"
"    padding: 0;\n"
"    color: rgb(0, 0, 0);\n"
"}")

        self.verticalLayout_3.addWidget(self.label_38)

        self.verticalSpacer_15 = QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_15)

        self.textBrowser_5 = QTextBrowser(self.layoutWidget_6)
        self.textBrowser_5.setObjectName(u"textBrowser_5")
        self.textBrowser_5.setStyleSheet(u"QTextBrowser{\n"
"    border: none;\n"
"    border-radius: 0;\n"
"    padding: 0;\n"
"    color: rgb(0, 0, 0);\n"
"}")

        self.verticalLayout_3.addWidget(self.textBrowser_5)

        self.label_39 = QLabel(self.layoutWidget_6)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setStyleSheet(u"QLabel {\n"
"	font: 9pt \"Segoe UI\";\n"
"	\n"
"    border: none;\n"
"    border-radius: 0;\n"
"    padding: 0;\n"
"    color: rgb(0, 0, 0);\n"
"}")

        self.verticalLayout_3.addWidget(self.label_39)

        self.uploadButton_5 = QPushButton(self.frame)
        self.uploadButton_5.setObjectName(u"uploadButton_5")
        self.uploadButton_5.setGeometry(QRect(120, 360, 101, 31))
        self.uploadButton_5.setStyleSheet(u"background-color: rgb(157, 81, 113);")
        self.label_40 = QLabel(self.frame)
        self.label_40.setObjectName(u"label_40")
        self.label_40.setGeometry(QRect(50, 230, 241, 111))
        self.label_40.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.frame_2 = QFrame(self.scrollAreaWidgetContents)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(60, 630, 741, 161))
        self.frame_2.setStyleSheet(u"QFrame {\n"
"    border-radius: 15px;\n"
"    background-color: #dcdcdc;  /* Daha gri renk */\n"
"    border: 1px solid #b0b0b0;  /* Hafif gri kenar */\n"
"    padding: 5px;\n"
"}")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) 
        self.showButton = QPushButton(self.frame_2)
        self.showButton.setObjectName(u"showButton")
        self.showButton.setGeometry(QRect(330, 100, 83, 29))
        self.showButton.setStyleSheet(u"background-color: rgb(157, 81, 113);")
        self.label_41 = QLabel(self.frame_2)
        self.label_41.setObjectName(u"label_41")
        self.label_41.setGeometry(QRect(110, 40, 471, 41))
        self.label_41.setStyleSheet(u"QLabel {\n"
"	font: 9pt \"Segoe UI\";\n"
"	color: rgb(0, 0, 0);\n"
"    border: none;\n"
"    border-radius: 0;\n"
"    padding: 0;\n"
"    color: rgb(0, 0, 0);\n"
"}")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.tableView.raise_()
        self.layoutWidget_2.raise_()
        self.frame.raise_()
        self.frame_2.raise_()

        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.label_33.setText(QCoreApplication.translate("Widget", u"SKINANAYZER", None))
        self.about_us.setText(QCoreApplication.translate("Widget", u"About us", None))
        self.contact.setText(QCoreApplication.translate("Widget", u"Contact ", None))
        self.Profil.setText(QCoreApplication.translate("Widget", u"Profil", None))
        self.label_37.setText(QCoreApplication.translate("Widget", u"Skinanalyzer  ", None))
        self.label_38.setText(QCoreApplication.translate("Widget", u"Skinanalyzer : AI- Based Skin Cancer Detection", None))
        self.textBrowser_5.setHtml(QCoreApplication.translate("Widget", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Skinanalyer evaluates symptoms on your skin and assists in early disease diagnosis through the power of innovative artificial intelligence (AI) skin technology. </p></body></html>", None))
        self.label_39.setText(QCoreApplication.translate("Widget", u"Make sure to consult your doctor without delay.", None))
        self.uploadButton_5.setText(QCoreApplication.translate("Widget", u"Upload Photo", None))
        self.label_40.setText(QCoreApplication.translate("Widget", u"TextLabel", None))
        self.showButton.setText(QCoreApplication.translate("Widget", u"Show", None))
        self.label_41.setText(QCoreApplication.translate("Widget", u"You can access your saved analyse history by clicking the button below", None))
   

