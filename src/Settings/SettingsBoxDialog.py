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
import SubiT
import Utils
import Registry
from Settings import Config

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
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(self.onApplyClicked)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.onCancelClicked)
        
        self.settingsTabWidget = QtGui.QTabWidget(self)
        self.settingsTabWidget.setGeometry(QtCore.QRect(10, 10, 380, 190))
        self.settingsTabWidget.setObjectName("settingsTabWidget")

        self.globalTab = QtGui.QWidget()
        self.globalTab.setObjectName("globalTab")
        self.settingsTabWidget.addTab(self.globalTab, "Global")
        self.handlersTab = QtGui.QWidget()
        self.handlersTab.setObjectName("handlersTab")
        self.settingsTabWidget.addTab(self.handlersTab, "Handlers")

        self.globalCheckBox_closeOnFinish = QtGui.QCheckBox(parent = self.globalTab, text = 'Close on finish')
        self.globalCheckBox_closeOnFinish.setGeometry(QtCore.QRect(10, 10, 371, 20))

        self.globalTab_updateGroupBox = QtGui.QGroupBox(self.globalTab, title = 'Updates')
        self.globalTab_updateGroupBox.setGeometry(QtCore.QRect(10, 35, 355, 103))
        self.globalCheckBox_checkForUpdates = QtGui.QCheckBox(parent = self.globalTab_updateGroupBox, text = 'Check for updates')
        self.globalCheckBox_checkForUpdates.setGeometry(QtCore.QRect(10, 15, 340, 20))
        self.globalCheckBox_autoUpdate = QtGui.QCheckBox(parent = self.globalTab_updateGroupBox, text = 'Auto update')
        self.globalCheckBox_autoUpdate.setGeometry(QtCore.QRect(10, 35, 340, 20))
        #self.globalCheckBox_autoUpdate.setEnabled(os.name == 'nt')
        self.globalCheckBox_autoUpdate.setEnabled(False)
        self.globalTab_updateGroupBox_updateBtn = QtGui.QPushButton(self.globalTab_updateGroupBox)
        self.globalTab_updateGroupBox_updateBtn.setGeometry(QtCore.QRect(10, 55, 335, 25))
        self.globalTab_updateGroupBox_updateBtn.setText(QtGui.QApplication.translate("SubiTMainForm", "Check For Update", None, QtGui.QApplication.UnicodeUTF8))
        self.globalTab_updateGroupBox_updateBtn.clicked.connect(self.onUpdateClicked)
        self.globalTab_updateGroupBox_verLabel = QtGui.QLabel(self.globalTab_updateGroupBox)
        self.globalTab_updateGroupBox_verLabel.setGeometry(QtCore.QRect(10, 82, 355, 20))
        self.globalTab_updateGroupBox_verLabel.setText(QtGui.QApplication.translate("settingsQDialog", "Current Version: %s" % SubiT.VERSION, None, QtGui.QApplication.UnicodeUTF8))
        self.globalTab_updateGroupBox_verLabel.setEnabled(False)
        
        self.handlersLabel = QtGui.QLabel(self.handlersTab)
        self.handlersLabel.setGeometry(QtCore.QRect(10, 10, 355, 20))
        self.handlersLabel.setText(QtGui.QApplication.translate("settingsQDialog", "Choose the desired handler:", None, QtGui.QApplication.UnicodeUTF8))
        self.handlersLabel.setObjectName(_fromUtf8("label"))
        self.handlersComboBox = QtGui.QComboBox(self.handlersTab)
        self.handlersComboBox.setGeometry(QtCore.QRect(10, 30, 355, 22))
        self.handlersComboBox.setObjectName(_fromUtf8("handlersComboBox"))

        self.handlersTab_AdvanceGroupBox = QtGui.QGroupBox(self.handlersTab, title = 'Advanced')
        self.handlersTab_AdvanceGroupBox.setGeometry(QtCore.QRect(10, 80, 355, 80))

        self.handlersAdvancedCheckBox = QtGui.QCheckBox(parent = self.handlersTab, text = 'Enable advanced settings')
        self.handlersAdvancedCheckBox.setGeometry(QtCore.QRect(10, 60, 355, 20))
        self.handlersAdvancedCheckBox.stateChanged.connect(lambda i: self.handlersTab_AdvanceGroupBox.setEnabled(True if i == 2 else False))
        self.handlersAdvancedCheckBox.setChecked(True)

        self.handlersPrimaryLanguageLabel = QtGui.QLabel(self.handlersTab_AdvanceGroupBox)
        self.handlersPrimaryLanguageLabel.setGeometry(QtCore.QRect(10, 15, 90, 20))
        self.handlersPrimaryLanguageLabel.setText(QtGui.QApplication.translate("settingsQDialog", "Primary language:", None, QtGui.QApplication.UnicodeUTF8))
        self.handlersPrimaryLanguageLabel.setObjectName(_fromUtf8("handlersPrimaryLanguageLabel"))
        self.handlersPrimaryLanguageComboBox = QtGui.QComboBox(self.handlersTab_AdvanceGroupBox)
        self.handlersPrimaryLanguageComboBox.setGeometry(QtCore.QRect(120, 15, 85, 22))
        self.handlersPrimaryLanguageComboBox.setObjectName(_fromUtf8("handlersPrimaryLanguageComboBox"))


        self.handlersSecondaryLanguageLabel = QtGui.QLabel(self.handlersTab_AdvanceGroupBox)
        self.handlersSecondaryLanguageLabel.setGeometry(QtCore.QRect(10, 45, 110, 20))
        self.handlersSecondaryLanguageLabel.setText(QtGui.QApplication.translate("settingsQDialog", "Secondary language:", None, QtGui.QApplication.UnicodeUTF8))
        self.handlersSecondaryLanguageLabel.setObjectName(_fromUtf8("handlersSecondaryLanguageLabel"))
        self.handlersSecondaryLanguageComboBox = QtGui.QComboBox(self.handlersTab_AdvanceGroupBox)
        self.handlersSecondaryLanguageComboBox.setGeometry(QtCore.QRect(120, 45, 85, 22))
        self.handlersSecondaryLanguageComboBox.setObjectName(_fromUtf8("handlersSecondaryLanguageComboBox"))


        self.handlersLanguagesLabel = QtGui.QLabel(self.handlersTab_AdvanceGroupBox)
        self.handlersLanguagesLabel.setGeometry(QtCore.QRect(220, 15, 120, 50))
        self.handlersLanguagesLabel.setText(QtGui.QApplication.translate("settingsQDialog", "These handlers will be\r\nused when no result will\r\ncome up using the\r\nselected handler.", None, QtGui.QApplication.UnicodeUTF8))
        self.handlersLanguagesLabel.setObjectName(_fromUtf8("handlersLanguagesLabel"))
        self.handlersLanguagesLabel.setEnabled(False)

        #Add extension handling only if it's Windows
        if Utils.IsWindowPlatform():
            self.registryTab = QtGui.QWidget()
            self.registryTab.setObjectName("registryTab")
            self.settingsTabWidget.addTab(self.registryTab, "Registry")        

            self.extLabel = QtGui.QLabel(self.registryTab)
            self.extLabel.setGeometry(QtCore.QRect(10, 10, 355, 20))
            self.extLabel.setObjectName("extLabel")
            
            self.extListWidget = QtGui.QListWidget(self.registryTab)
            self.extListWidget.setGeometry(QtCore.QRect(10, 30, 245, 80))
            self.extListWidget.setObjectName("extListWidget")
            self.extLabel.setText(QtGui.QApplication.translate("SettingsBoxDialog", "Select file extensions for right click menu:", None, QtGui.QApplication.UnicodeUTF8))
            self.extListWidget.currentItemChanged.connect(self.onItemSelectionChanged)
            self.extListWidget.setEnabled(True)
            
            self.extDelButton = QtGui.QToolButton(self.registryTab)
            self.extDelButton.setGeometry(QtCore.QRect(260, 40, 100, 22))
            self.extDelButton.setText(QtGui.QApplication.translate("SettingsBoxDialog", "Delete", None, QtGui.QApplication.UnicodeUTF8))
            self.extDelButton.clicked.connect(self.onExtDelButtonClicked)
            
            self.extAddButton = QtGui.QToolButton(self.registryTab)
            self.extAddButton.setGeometry(QtCore.QRect(260, 65, 100, 22))
            self.extAddButton.setText(QtGui.QApplication.translate("SettingsBoxDialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
            self.extAddButton.clicked.connect(self.onExtAddButtonClicked)
            self.extAddButton.setEnabled(True)

            self.extCheckBox_registerExtensions = QtGui.QCheckBox(parent = self.registryTab, text = 'Register extensions')
            self.extCheckBox_registerExtensions.setGeometry(QtCore.QRect(10, 115, 340, 20))

        self.setConfigs()
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
        
    def retranslateUi(self):
        pass

    def setConfigs(self):
        #=============================================================
        #General tab
        CONFIG_CLOSE_ON_FINISH  = Config.SubiTConfig.Singleton().getBoolean('Global', 'close_on_finish')
        CONFIG_CHECK_UPDATES    = Config.SubiTConfig.Singleton().getBoolean('Global', 'check_updates')
        CONFIG_AUTO_UPDATE      = Config.SubiTConfig.Singleton().getBoolean('Global', 'auto_update')

        self.globalCheckBox_closeOnFinish.setChecked(CONFIG_CLOSE_ON_FINISH)
        self.globalCheckBox_checkForUpdates.setChecked(CONFIG_CHECK_UPDATES)
        #self.globalCheckBox_autoUpdate.setChecked(CONFIG_AUTO_UPDATE and os.name == 'nt')
        self.globalCheckBox_autoUpdate.setChecked(False)
        #=============================================================

        if Utils.IsWindowPlatform():
            #Registry tab
            CONFIG_REGISTER_EXTENSIONS = Config.SubiTConfig.Singleton().getBoolean('Registry', 'register_extensions')

            self.extCheckBox_registerExtensions.setChecked(CONFIG_REGISTER_EXTENSIONS)
            for ext in Registry.getExtList():
                self.addItemToExtListWidget(ext)
            if self.extListWidget.count() > 1:
                self.extDelButton.setEnabled(False)
        #=============================================================
        #Handlers tab
        CONFIG_PRIMARY_LANG         = Config.SubiTConfig.Singleton().getStr('Handlers', 'primary_lang')
        CONFIG_SECONDARY_LANG       = Config.SubiTConfig.Singleton().getStr('Handlers', 'secondary_lang')
        CONFIG_ADVANCED_SETTINGS    = Config.SubiTConfig.Singleton().getBoolean('Handlers', 'advanced_features')
        all_languages = []

        #Get handlers name from all avaliable handlers
        handlers_names = map(lambda x: x.HANDLER_NAME, SubHandlers.getHandlers())
        #Sort by both lang & handler name
        handlers_names.sort(lambda x, y: cmp(cmp(x[1], y[1]), cmp(x[0],y[0])), lambda z: z.split(' - '))
        selected_handler = SubHandlers.getSelectedHandler().HANDLER_NAME
        
        #group results using the right hand side of the handler name (the site name)
        for group, handlers in groupby(handlers_names, lambda h: h.split(' - ')[1]):
            for h in handlers:
                self.handlersComboBox.insertItem(0, h)
                l = h.split(' - ')[0]
                if l not in all_languages:
                    all_languages.append(l)
            self.handlersComboBox.insertSeparator(-1)
        #highlight the selected handler            
        self.handlersComboBox.setCurrentIndex(self.handlersComboBox.findText(selected_handler))

        import locale
        all_languages.sort(locale.strcoll, reverse=True) #Sort them, alphabeticly. we set reverse, because we're putting items at index of 0
        #group results using the left hand side of the handler name (the language)
        for lang in all_languages:
            self.handlersPrimaryLanguageComboBox.insertItem(0, lang)
            self.handlersSecondaryLanguageComboBox.insertItem(0, lang)

        self.handlersPrimaryLanguageComboBox.setCurrentIndex(self.handlersPrimaryLanguageComboBox.findText(CONFIG_PRIMARY_LANG))
        self.handlersSecondaryLanguageComboBox.setCurrentIndex(self.handlersSecondaryLanguageComboBox.findText(CONFIG_SECONDARY_LANG))
        
        self.handlersAdvancedCheckBox.setChecked(CONFIG_ADVANCED_SETTINGS)

    def onCancelClicked(self):
        self.close()
    
    def askForFirstRegistration(self):
        sig = Communicate()
        sig.objSignal.connect(self.slot_askForFirstRegistration)
        sig.objSignal.emit(self)

    @QtCore.Slot(QtGui.QDialog)
    def slot_askForFirstRegistration(self):
        ret = QtGui.QMessageBox.question(self, 'Context menu registration',
                               self.tr("Whould you like SubiT to appear in the right-click context menu of movie files?\r\n\r\nDefault extensions are: \r\n%s" % 
                                       Config.SubiTConfig.Singleton().getStr('Registry', 'keys').replace('|', ', ')),
                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            Registry.register_all()

    def tellUserToRunAsAdministrator(self):
        QtGui.QMessageBox.warning(self, 'Registration failure', "Registration for right-click context menu has failed using the current user privilages\r\n\r\nPlease run SubiT as Administrator, and try again.")
               
    def onApplyClicked(self):
        self.onSaveClicked()
        ret = QtGui.QMessageBox.question(self, 'Restart',
                               self.tr("In order to apply changes, application will need to restart.\r\nContinue?"),
                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            Utils.restart()
    
    def onSaveClicked(self):
        #Set global values
        Config.SubiTConfig.Singleton().setValue('Global', 'close_on_finish', self.globalCheckBox_closeOnFinish.isChecked())
        Config.SubiTConfig.Singleton().setValue('Global', 'check_updates', self.globalCheckBox_checkForUpdates.isChecked())
        #Config.SubiTConfig.Singleton().setValue('Global', 'auto_update', self.globalCheckBox_autoUpdate.isChecked() and os.name == 'nt')
        Config.SubiTConfig.Singleton().setValue('Global', 'auto_update', False)
        
        #Set handler values
        primarylang     = str(self.handlersPrimaryLanguageComboBox.currentText())
        secondarylang   = str(self.handlersSecondaryLanguageComboBox.currentText())
        selectedHandler = str(self.handlersComboBox.currentText())
        if selectedHandler in map(lambda x: x.HANDLER_NAME, SubHandlers.getHandlers()):
            SubHandlers.setSelectedHandler(str(self.handlersComboBox.currentText()))
        
        Config.SubiTConfig.Singleton().setValue('Handlers', 'selected_handler', selectedHandler)
        Config.SubiTConfig.Singleton().setValue('Handlers', 'advanced_features', self.handlersAdvancedCheckBox.isChecked())
        Config.SubiTConfig.Singleton().setValue('Handlers', 'primary_lang', primarylang)
        Config.SubiTConfig.Singleton().setValue('Handlers', 'secondary_lang', secondarylang)
        
        #Set registry values
        if Utils.IsWindowPlatform():
            #First we unregister the current extensions from the registry, in order to start from fresh
            Registry.unregister_all()
            CONFIG_REGISTER_EXTENSIONS = self.extCheckBox_registerExtensions.isChecked()
            Config.SubiTConfig.Singleton().setValue('Registry', 'register_extensions', CONFIG_REGISTER_EXTENSIONS)
                      
            #Best way to get all items from the QListWidget
            Registry.setExtList( map(lambda x: x.text(), filter(lambda item: item.checkState() == QtCore.Qt.CheckState.Checked and item.text() != NEW_EXT_ITEM_STR, 
                                                                self.extListWidget.findItems('.*', QtCore.Qt.MatchRegExp))))
            if CONFIG_REGISTER_EXTENSIONS:
                #After setting the new extensions, we register them
                Registry.register_all()
        
        Config.SubiTConfig.Singleton().save()

    def onUpdateClicked(self):
        import Update
        #Run update check with force set to true
        Update.performUpdate(True, False)
            
    def onItemSelectionChanged(self, event):
        self.extDelButton.setEnabled(True)
    
    def onExtAddButtonClicked(self, event=None):
        itemToAdd = self.addItemToExtListWidget(NEW_EXT_ITEM_STR)
        self.extListWidget.setCurrentItem(itemToAdd)
        self.extListWidget.editItem(itemToAdd)

    def verLabelUpdate(self, message):
        self.globalTab_updateGroupBox_verLabel.setText(message)
        
    def boolToCheckState(self, bool_value):
        if bool_value: return QtCore.Qt.CheckState.Checked
        else: return QtCore.Qt.CheckState.Unchecked
            
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

class Communicate(QtCore.QObject):
    objSignal = QtCore.Signal(QtCore.QObject)