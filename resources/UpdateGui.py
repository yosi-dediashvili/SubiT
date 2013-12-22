# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SubiT_UI_Update.ui'
#
# Created: Fri Jan 27 11:07:43 2012
#      by: pyside-uic 0.2.13 running on PySide 1.0.9
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_UpdateGui(object):
    def setupUi(self, UpdateGui):
        UpdateGui.setObjectName("UpdateGui")
        UpdateGui.resize(414, 75)
        self.logLabel = QtGui.QLabel(UpdateGui)
        self.logLabel.setGeometry(QtCore.QRect(80, 30, 311, 21))
        self.logLabel.setObjectName("logLabel")
        self.gifLabel = QtGui.QLabel(UpdateGui)
        self.gifLabel.setGeometry(QtCore.QRect(10, 12, 46, 51))
        self.gifLabel.setObjectName("gifLabel")

        self.retranslateUi(UpdateGui)
        QtCore.QMetaObject.connectSlotsByName(UpdateGui)

    def retranslateUi(self, UpdateGui):
        UpdateGui.setWindowTitle(QtGui.QApplication.translate("UpdateGui", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.logLabel.setText(QtGui.QApplication.translate("UpdateGui", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.gifLabel.setText(QtGui.QApplication.translate("UpdateGui", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

