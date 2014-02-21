# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\dev\__subit__\resources\gui\SubiTLanguageUi.ui'
#
# Created: Sat Jan 18 23:10:30 2014
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 250)
        Dialog.setMinimumSize(QtCore.QSize(400, 250))
        Dialog.setMaximumSize(QtCore.QSize(400, 250))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Global/icon-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.languageSelectLabel = QtGui.QLabel(Dialog)
        self.languageSelectLabel.setWordWrap(True)
        self.languageSelectLabel.setObjectName("languageSelectLabel")
        self.verticalLayout.addWidget(self.languageSelectLabel)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.languageOrderListWidget = QtGui.QListWidget(Dialog)
        self.languageOrderListWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.languageOrderListWidget.setDragEnabled(False)
        self.languageOrderListWidget.setObjectName("languageOrderListWidget")
        self.horizontalLayout.addWidget(self.languageOrderListWidget)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setContentsMargins(2, 25, 2, 25)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.languageUpToolButton = QtGui.QToolButton(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.languageUpToolButton.sizePolicy().hasHeightForWidth())
        self.languageUpToolButton.setSizePolicy(sizePolicy)
        self.languageUpToolButton.setMinimumSize(QtCore.QSize(0, 25))
        self.languageUpToolButton.setMaximumSize(QtCore.QSize(16777215, 25))
        self.languageUpToolButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Settings/icon-settings-uparrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.languageUpToolButton.setIcon(icon1)
        self.languageUpToolButton.setObjectName("languageUpToolButton")
        self.verticalLayout_3.addWidget(self.languageUpToolButton)
        self.languageDownToolButton = QtGui.QToolButton(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.languageDownToolButton.sizePolicy().hasHeightForWidth())
        self.languageDownToolButton.setSizePolicy(sizePolicy)
        self.languageDownToolButton.setMinimumSize(QtCore.QSize(0, 25))
        self.languageDownToolButton.setMaximumSize(QtCore.QSize(16777215, 25))
        self.languageDownToolButton.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Settings/icon-settings-downarrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.languageDownToolButton.setIcon(icon2)
        self.languageDownToolButton.setObjectName("languageDownToolButton")
        self.verticalLayout_3.addWidget(self.languageDownToolButton)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.horizontalLayout.setStretch(0, 10)
        self.horizontalLayout.setStretch(1, 2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setWordWrap(True)
        self.label_3.setOpenExternalLinks(True)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 15)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.languageOkCancelLayout = QtGui.QHBoxLayout()
        self.languageOkCancelLayout.setSpacing(3)
        self.languageOkCancelLayout.setContentsMargins(-1, -1, -1, 0)
        self.languageOkCancelLayout.setObjectName("languageOkCancelLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.languageOkCancelLayout.addItem(spacerItem)
        self.okPushButton = QtGui.QPushButton(Dialog)
        self.okPushButton.setEnabled(False)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Settings/icon-settings-ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okPushButton.setIcon(icon3)
        self.okPushButton.setObjectName("okPushButton")
        self.languageOkCancelLayout.addWidget(self.okPushButton)
        self.cancelPushButton = QtGui.QPushButton(Dialog)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/Settings/icon-settings-cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelPushButton.setIcon(icon4)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.languageOkCancelLayout.addWidget(self.cancelPushButton)
        self.verticalLayout.addLayout(self.languageOkCancelLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Preferred languages", None, QtGui.QApplication.UnicodeUTF8))
        self.languageSelectLabel.setText(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Before we begin, SubiT needs to know your preferred language for subtitles.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Please select a language (or languages) from the list below:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.languageOrderListWidget.setSortingEnabled(False)
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/MainWindow/icon-main-info.png\" /></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Please feel free to </span><a href=\"http://subit-app.sourceforge.net/contact.html\"><span style=\" text-decoration: underline; color:#0000ff;\">contact us</span></a><span style=\" font-size:8pt;\"> if your language is missing from SubiT. We will do our best to include it in the next version.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.okPushButton.setText(QtGui.QApplication.translate("Dialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPushButton.setText(QtGui.QApplication.translate("Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

from Interaction import ImagesResources
