# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SubiT_UI_Settings.ui'
#
# Created: Thu Dec 22 23:42:05 2011
#      by: pyside-uic 0.2.13 running on PySide 1.0.9
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_settingsQDialog(object):
    def setupUi(self, settingsQDialog):
        settingsQDialog.setObjectName("settingsQDialog")
        settingsQDialog.resize(400, 240)
        settingsQDialog.setMinimumSize(QtCore.QSize(400, 240))
        settingsQDialog.setMaximumSize(QtCore.QSize(400, 240))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        settingsQDialog.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(settingsQDialog)
        self.buttonBox.setGeometry(QtCore.QRect(230, 210, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.handlersGroupBox = QtGui.QGroupBox(settingsQDialog)
        self.handlersGroupBox.setGeometry(QtCore.QRect(10, 10, 381, 80))
        self.handlersGroupBox.setFlat(True)
        self.handlersGroupBox.setObjectName("handlersGroupBox")
        self.handlersLabel = QtGui.QLabel(self.handlersGroupBox)
        self.handlersLabel.setGeometry(QtCore.QRect(10, 20, 371, 20))
        self.handlersLabel.setObjectName("handlersLabel")
        self.handlersComboBox = QtGui.QComboBox(self.handlersGroupBox)
        self.handlersComboBox.setGeometry(QtCore.QRect(10, 40, 371, 22))
        self.handlersComboBox.setObjectName("handlersComboBox")
        self.line = QtGui.QFrame(settingsQDialog)
        self.line.setGeometry(QtCore.QRect(40, 190, 321, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.extGroupBox = QtGui.QGroupBox(settingsQDialog)
        self.extGroupBox.setGeometry(QtCore.QRect(10, 80, 381, 111))
        self.extGroupBox.setFlat(True)
        self.extGroupBox.setObjectName("extGroupBox")
        self.extLabel = QtGui.QLabel(self.extGroupBox)
        self.extLabel.setGeometry(QtCore.QRect(10, 20, 371, 20))
        self.extLabel.setObjectName("extLabel")
        self.extListView = QtGui.QListView(self.extGroupBox)
        self.extListView.setGeometry(QtCore.QRect(10, 40, 371, 71))
        self.extListView.setObjectName("extListView")

        self.retranslateUi(settingsQDialog)
        QtCore.QMetaObject.connectSlotsByName(settingsQDialog)

    def retranslateUi(self, settingsQDialog):
        settingsQDialog.setWindowTitle(QtGui.QApplication.translate("settingsQDialog", "SubiT - Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.handlersGroupBox.setTitle(QtGui.QApplication.translate("settingsQDialog", "Handlers", None, QtGui.QApplication.UnicodeUTF8))
        self.handlersLabel.setText(QtGui.QApplication.translate("settingsQDialog", "Choose the desired handler:", None, QtGui.QApplication.UnicodeUTF8))
        self.extGroupBox.setTitle(QtGui.QApplication.translate("settingsQDialog", "Extensions", None, QtGui.QApplication.UnicodeUTF8))
        self.extLabel.setText(QtGui.QApplication.translate("settingsQDialog", "Select file extensions for right click menu:", None, QtGui.QApplication.UnicodeUTF8))

