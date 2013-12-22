# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SubiT_UI_About.ui'
#
# Created: Tue Dec 20 00:17:58 2011
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_AboutBoxDialog(object):
    def setupUi(self, AboutBoxDialog):
        AboutBoxDialog.setObjectName(_fromUtf8("AboutBoxDialog"))
        AboutBoxDialog.resize(425, 290)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutBoxDialog.sizePolicy().hasHeightForWidth())
        AboutBoxDialog.setSizePolicy(sizePolicy)
        AboutBoxDialog.setMinimumSize(QtCore.QSize(425, 290))
        AboutBoxDialog.setMaximumSize(QtCore.QSize(425, 290))
        AboutBoxDialog.setWindowTitle(QtGui.QApplication.translate("AboutBoxDialog", "SubiT - About", None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AboutBoxDialog.setWindowIcon(icon)
        self.label = QtGui.QLabel(AboutBoxDialog)
        self.label.setGeometry(QtCore.QRect(0, 0, 425, 210))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Lucida Grande"))
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setFrameShadow(QtGui.QFrame.Sunken)
        self.label.setText(QtGui.QApplication.translate("AboutBoxDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/newPrefix/icon.png\" /></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">SubiT is an automated system for subtitle downloading.</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">                              </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">SubiT was created in order to ease the process of downloading </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">hebrew subtitles - with just one click you can download subtitles </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">for a whole collection of your favorite movies and TV shows.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Version: {0}</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.subit-app.sf.net\"><span style=\" font-size:8pt; text-decoration: underline; color:#0000ff;\">www.subit-app.sf.net</span></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setMargin(5)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.groupBox = QtGui.QGroupBox(AboutBoxDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 210, 411, 71))
        self.groupBox.setTitle(QtGui.QApplication.translate("AboutBoxDialog", "Powered By ", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(0, 20, 181, 51))
        self.label_2.setText(QtGui.QApplication.translate("AboutBoxDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.opensubtitles.org\"><img src=\":/newPrefix/os-icon.png\" /></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(AboutBoxDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutBoxDialog)

    def retranslateUi(self, AboutBoxDialog):
        pass

import Logo_rc
