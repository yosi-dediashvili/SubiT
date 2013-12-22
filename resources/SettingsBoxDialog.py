# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SubiT_UI_Settings.ui'
#
# Created: Tue Jan 24 21:01:19 2012
#      by: pyside-uic 0.2.13 running on PySide 1.0.9
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_settingsQDialog(object):
    def setupUi(self, settingsQDialog):
        settingsQDialog.setObjectName("settingsQDialog")
        settingsQDialog.resize(421, 273)
        settingsQDialog.setMinimumSize(QtCore.QSize(0, 0))
        settingsQDialog.setMaximumSize(QtCore.QSize(1000, 1000))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        settingsQDialog.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(settingsQDialog)
        self.buttonBox.setGeometry(QtCore.QRect(250, 240, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.settingsTabWidget = QtGui.QTabWidget(settingsQDialog)
        self.settingsTabWidget.setGeometry(QtCore.QRect(10, 10, 401, 221))
        self.settingsTabWidget.setObjectName("settingsTabWidget")
        self.globalTab = QtGui.QWidget()
        self.globalTab.setObjectName("globalTab")
        self.settingsTabWidget.addTab(self.globalTab, "")
        self.handlersTab = QtGui.QWidget()
        self.handlersTab.setObjectName("handlersTab")
        self.handlersLabel = QtGui.QLabel(self.handlersTab)
        self.handlersLabel.setGeometry(QtCore.QRect(10, 10, 371, 20))
        self.handlersLabel.setObjectName("handlersLabel")
        self.handlersComboBox = QtGui.QComboBox(self.handlersTab)
        self.handlersComboBox.setGeometry(QtCore.QRect(10, 30, 371, 22))
        self.handlersComboBox.setObjectName("handlersComboBox")
        self.settingsTabWidget.addTab(self.handlersTab, "")
        self.registryTab = QtGui.QWidget()
        self.registryTab.setObjectName("registryTab")
        self.extLabel = QtGui.QLabel(self.registryTab)
        self.extLabel.setGeometry(QtCore.QRect(10, 20, 371, 20))
        self.extLabel.setObjectName("extLabel")
        self.extGroupBox = QtGui.QGroupBox(self.registryTab)
        self.extGroupBox.setGeometry(QtCore.QRect(0, 60, 381, 111))
        self.extGroupBox.setFlat(True)
        self.extGroupBox.setObjectName("extGroupBox")
        self.listWidget = QtGui.QListWidget(self.extGroupBox)
        self.listWidget.setGeometry(QtCore.QRect(10, 40, 141, 71))
        self.listWidget.setObjectName("listWidget")
        item = QtGui.QListWidgetItem(self.listWidget)
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        item = QtGui.QListWidgetItem(self.listWidget)
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        item = QtGui.QListWidgetItem(self.listWidget)
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        self.settingsTabWidget.addTab(self.registryTab, "")

        self.retranslateUi(settingsQDialog)
        self.settingsTabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(settingsQDialog)

    def retranslateUi(self, settingsQDialog):
        settingsQDialog.setWindowTitle(QtGui.QApplication.translate("settingsQDialog", "SubiT - Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.settingsTabWidget.setTabText(self.settingsTabWidget.indexOf(self.globalTab), QtGui.QApplication.translate("settingsQDialog", "Tab 1", None, QtGui.QApplication.UnicodeUTF8))
        self.handlersLabel.setText(QtGui.QApplication.translate("settingsQDialog", "Choose the desired handler:", None, QtGui.QApplication.UnicodeUTF8))
        self.settingsTabWidget.setTabText(self.settingsTabWidget.indexOf(self.handlersTab), QtGui.QApplication.translate("settingsQDialog", "Tab 2", None, QtGui.QApplication.UnicodeUTF8))
        self.extLabel.setText(QtGui.QApplication.translate("settingsQDialog", "Select file extensions for right click menu:", None, QtGui.QApplication.UnicodeUTF8))
        self.extGroupBox.setTitle(QtGui.QApplication.translate("settingsQDialog", "Extensions", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        self.listWidget.item(0).setText(QtGui.QApplication.translate("settingsQDialog", ".mkv", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidget.item(1).setText(QtGui.QApplication.translate("settingsQDialog", ".avi", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidget.item(2).setText(QtGui.QApplication.translate("settingsQDialog", ".mp4", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.settingsTabWidget.setTabText(self.settingsTabWidget.indexOf(self.registryTab), QtGui.QApplication.translate("settingsQDialog", "Page", None, QtGui.QApplication.UnicodeUTF8))

