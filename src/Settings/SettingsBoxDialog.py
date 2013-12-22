# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SubiT_UI_Settings.ui'
#
# Created: Tue Dec 20 00:28:31 2011
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
from itertools import groupby

import SubHandlers
import os
import sys
import Gui
import Utils
import Registry

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

NEW_EXT_ITEM_STR = '<new item>'

class SettingsBoxDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.setObjectName(_fromUtf8("settingsQDialog"))
        self.resize(400, 240)
        self.setMinimumSize(QtCore.QSize(400, 240))
        self.setMaximumSize(QtCore.QSize(400, 240))
        self.setWindowTitle(QtGui.QApplication.translate("settingsQDialog", "SubiT - Settings", None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(Gui.IMAGES_LOCATION, "icon.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(230, 210, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        #self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(self.onApplyClicked)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.onCancelClicked)
        #self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.onApplyClicked)
        
        
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 381, 80))
        self.groupBox.setTitle(QtGui.QApplication.translate("settingsQDialog", "Handlers", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 20, 371, 20))
        self.label.setText(QtGui.QApplication.translate("settingsQDialog", "Choose the desired handler:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.handlersComboBox = QtGui.QComboBox(self.groupBox)
        self.handlersComboBox.setGeometry(QtCore.QRect(10, 40, 371, 22))
        self.handlersComboBox.setObjectName(_fromUtf8("handlersComboBox"))
        self.line = QtGui.QFrame(self)
        
        handlers_names = map(lambda x: x.HANDLER_NAME, SubHandlers.getHandlers())
        #Sort by both lang & handler name
        handlers_names.sort(lambda x, y: cmp(cmp(x[1], y[1]), cmp(x[0],y[0])), lambda z: z.split(' - '))

        selected_handler = SubHandlers.getSelectedHandler().HANDLER_NAME
        
        for group, handlers in groupby(handlers_names, lambda h: h.split(' - ')[1]):
            for h in handlers:
                self.handlersComboBox.insertItem(0, h)
            self.handlersComboBox.insertSeparator(-1)
            
        self.handlersComboBox.setCurrentIndex(self.handlersComboBox.findText(selected_handler))
        
        #Add extension handling only if it's Windows
        if os.name == 'nt':
            self.extGroupBox = QtGui.QGroupBox(self)
            self.extGroupBox.setGeometry(QtCore.QRect(10, 80, 381, 111))
            self.extGroupBox.setFlat(True)
            self.extGroupBox.setObjectName("extGroupBox")
            self.extLabel = QtGui.QLabel(self.extGroupBox)
            self.extLabel.setGeometry(QtCore.QRect(10, 20, 371, 20))
            self.extLabel.setObjectName("extLabel")
            
            self.extListWidget = QtGui.QListWidget(self.extGroupBox)
            self.extListWidget.setGeometry(QtCore.QRect(10, 40, 261, 71))
            self.extListWidget.setObjectName("extListWidget")
            self.extGroupBox.setTitle(QtGui.QApplication.translate("SettingsBoxDialog", "Extensions", None, QtGui.QApplication.UnicodeUTF8))
            self.extLabel.setText(QtGui.QApplication.translate("SettingsBoxDialog", "Select file extensions for right click menu:", None, QtGui.QApplication.UnicodeUTF8))
            self.extListWidget.currentItemChanged.connect(self.onItemSelectionChanged)
            self.extListWidget.setEnabled(True)
            
            self.extDelButton = QtGui.QToolButton(self.extGroupBox)
            self.extDelButton.setGeometry(QtCore.QRect(281, 40, 100, 22))
            self.extDelButton.setText(QtGui.QApplication.translate("SettingsBoxDialog", "Delete", None, QtGui.QApplication.UnicodeUTF8))
            self.extDelButton.clicked.connect(self.onExtDelButtonClicked)
            
            self.extAddButton = QtGui.QToolButton(self.extGroupBox)
            self.extAddButton.setGeometry(QtCore.QRect(281, 65, 100, 22))
            self.extAddButton.setText(QtGui.QApplication.translate("SettingsBoxDialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
            self.extAddButton.clicked.connect(self.onExtAddButtonClicked)
            self.extAddButton.setEnabled(True)
            
            
            for ext in Registry.getExtList():
                self.addItemToExtListWidget(ext)
            if self.extListWidget.count() > 1:
                self.extDelButton.setEnabled(False)
        
        self.line.setGeometry(QtCore.QRect(40, 190, 321, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
    def retranslateUi(self):
        pass

    def onCancelClicked(self):
        self.close()

    def onApplyClicked(self):
        self.onSaveClicked()
        ret = QtGui.QMessageBox.question(self, 'Restart',
                               self.tr("In order to apply changes, application will need to restart.\r\nContinue?"),
                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            #Subit.exe + path to movie
            if len(sys.argv) > 1:
                os.execl(sys.executable, sys.executable, '"%s"' % sys.argv[1])
            else:
                os.execl(sys.executable, sys.executable)
    
    def onSaveClicked(self):
        #Setting the new handler
        selectedHandler = str(self.handlersComboBox.currentText())
        if selectedHandler in map(lambda x: x.HANDLER_NAME, SubHandlers.getHandlers()):
            SubHandlers.setSelectedHandler(str(self.handlersComboBox.currentText()))
        
        if os.name == 'nt':
            #First we unregister the current extensions from the registry
            Registry.unregister_all()
            #Best way to get all items from the QListWidget
            Registry.setExtList( map(lambda x: x.text(), filter(lambda item: item.checkState() == QtCore.Qt.CheckState.Checked and item.text() != NEW_EXT_ITEM_STR, 
                                                                self.extListWidget.findItems('.*', QtCore.Qt.MatchRegExp))))
            #After setting the new extensions, we register them
            Registry.register_all()
            
    def onItemSelectionChanged(self, event):
        self.extDelButton.setEnabled(True)
    
    def onExtAddButtonClicked(self, event=None):
        itemToAdd = self.addItemToExtListWidget(NEW_EXT_ITEM_STR)
        self.extListWidget.setCurrentItem(itemToAdd)
        self.extListWidget.editItem(itemToAdd)
        
            
    def onExtDelButtonClicked(self, event=None):
        itemToDelete = self.extListWidget.takeItem(self.extListWidget.currentRow())
        itemToDelete = None
        if self.extListWidget.count() > 1:
            self.extDelButton.setEnabled(False)
        
    def addItemToExtListWidget(self, ext):
        item = QtGui.QListWidgetItem(ext)
        item.setFlags(  QtCore.Qt.ItemIsUserCheckable | 
                        QtCore.Qt.ItemIsSelectable    | 
                        QtCore.Qt.ItemIsEnabled       | 
                        QtCore.Qt.ItemIsEditable)
    
        item.setCheckState(QtCore.Qt.CheckState.Checked)
        self.extListWidget.addItem(item)
        return item