import time
import os
import sys

from PySide import QtCore, QtGui

import Utils
import SubiT
import Logs

from GuiWidgets import GWTextInput
from GuiWidgets import GWListWidget
from GuiWidgets import GWListWidget_Log
from Settings.AboutBoxDialog    import AboutBoxDialog
from Settings.SettingsBoxDialog import SettingsBoxDialog
from Settings.UpdateGui         import UpdateGui


IMAGES_LOCATION = os.path.join(os.path.split(os.path.abspath(__file__))[0]
                                                  .replace('\\library.zip', '')
                                                  , 'Images')

class BOXES_SIZES:
    WIDTH = 50
    LOG_HEIGHT = 7
    CHOICE_HEIGHT = 8
    FRAME_PAD = 2

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class gui(QtGui.QMainWindow):
    def __init__(self):    
        super(gui, self).__init__()
        
        self.setObjectName(_fromUtf8("SubiTMainForm"))
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setEnabled(True)
        self.resize(710, 390)
        self.setGeometry(QtGui.QCursor().pos().x(), QtGui.QCursor().pos().y(),710, 390)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(710, 390))
        self.setMaximumSize(QtCore.QSize(710, 390))
        self.setWindowTitle(QtGui.QApplication.translate("SubiTMainForm", "SubiT - %s" % SubiT.VERSION, None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(IMAGES_LOCATION, "icon.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.logGroupBox = QtGui.QGroupBox(self)
        self.logGroupBox.setGeometry(QtCore.QRect(10, 0, 691, 131))
        self.logGroupBox.setTitle(QtGui.QApplication.translate("SubiTMainForm", " Log ", None, QtGui.QApplication.UnicodeUTF8))
        self.logGroupBox.setObjectName(_fromUtf8("logGroupBox"))
        #self.logTextBrowser = GWTextEdit(self.logGroupBox)
        #self.logTextBrowser = QtGui.QListWidget(self.logGroupBox)
        self.logTextBrowser = GWListWidget_Log(self.logGroupBox)
        self.logTextBrowser.setGeometry(QtCore.QRect(5, 20, 681, 101))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logTextBrowser.sizePolicy().hasHeightForWidth())
        self.logTextBrowser.setSizePolicy(sizePolicy)
        self.logTextBrowser.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.logTextBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.logTextBrowser.setObjectName(_fromUtf8("logTextBrowser"))

        self.moviesGroupBox = QtGui.QGroupBox(self)
        self.moviesGroupBox.setGeometry(QtCore.QRect(10, 130, 341, 201))
        self.moviesGroupBox.setTitle(QtGui.QApplication.translate("SubiTMainForm", " Movies ", None, QtGui.QApplication.UnicodeUTF8))
        self.moviesGroupBox.setObjectName(_fromUtf8("moviesGroupBox"))
        self.moviesListWidget = GWListWidget(self.moviesGroupBox)
        self.moviesListWidget.setGeometry(QtCore.QRect(5, 20, 331, 101))
        self.moviesListWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.moviesListWidget.setObjectName(_fromUtf8("moviesListWidget"))
        self.moviesListWidget.setEnabled(False)
        self.inputGoupBox = QtGui.QGroupBox(self.moviesGroupBox)
        self.inputGoupBox.setGeometry(QtCore.QRect(10, 120, 321, 81))
        self.inputGoupBox.setTitle(QtGui.QApplication.translate("SubiTMainForm", "Input ", None, QtGui.QApplication.UnicodeUTF8))
        self.inputGoupBox.setFlat(True)
        self.inputGoupBox.setObjectName(_fromUtf8("inputGoupBox"))
        
        self.inputLineEdit = GWTextInput(self.inputGoupBox)
        self.inputLineEdit.setGeometry(QtCore.QRect(0, 20, 295, 21))
        self.inputLineEdit.setObjectName(_fromUtf8("inputLineEdit"))
        self.inputLineEdit.setEnabled(False)
        
        self.browseBTN = QtGui.QToolButton(self.inputGoupBox)
        self.browseBTN.setGeometry(QtCore.QRect(295, 20, 25, 21))
        self.browseBTN.setText(QtGui.QApplication.translate("SubiTMainForm", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.browseBTN.setAutoRaise(False)
        self.browseBTN.setEnabled(False)
        self.browseBTN.setArrowType(QtCore.Qt.NoArrow)
        self.browseBTN.setObjectName(_fromUtf8("browseBTN"))
        self.goBTN = QtGui.QPushButton(self.inputGoupBox)
        self.goBTN.setGeometry(QtCore.QRect(0, 42, 321, 30))
        self.goBTN.setText(QtGui.QApplication.translate("SubiTMainForm", "Go", None, QtGui.QApplication.UnicodeUTF8))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(IMAGES_LOCATION, "icon-go.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.goBTN.setIcon(icon1)
        self.goBTN.setIconSize(QtCore.QSize(24, 24))
        self.goBTN.setCheckable(False)
        self.goBTN.setAutoExclusive(False)
        self.goBTN.setEnabled(False)
        self.goBTN.setAutoDefault(False)
        self.goBTN.setDefault(True)
        self.goBTN.setCheckable(True)
        self.goBTN.setFlat(False)
        self.goBTN.setObjectName(_fromUtf8("goBTN"))
        self.versionsGroupBox = QtGui.QGroupBox(self)
        self.versionsGroupBox.setGeometry(QtCore.QRect(360, 130, 341, 251))
        self.versionsGroupBox.setTitle(QtGui.QApplication.translate("SubiTMainForm", " Versions ", None, QtGui.QApplication.UnicodeUTF8))
        self.versionsGroupBox.setObjectName(_fromUtf8("versionsGroupBox"))
        self.versionsListWidget = GWListWidget(self.versionsGroupBox)
        self.versionsListWidget.setGeometry(QtCore.QRect(5, 20, 331, 221))
        self.versionsListWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.versionsListWidget.setObjectName(_fromUtf8("versionsListWidget"))
        self.versionsListWidget.setEnabled(False)
        self.settingsBTN = QtGui.QCommandLinkButton(self)
        self.settingsBTN.setGeometry(QtCore.QRect(10, 335, 111, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Segoe UI"))
        font.setItalic(False)
        font.setKerning(True)
        self.settingsBTN.setFont(font)
        self.settingsBTN.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.settingsBTN.setAutoFillBackground(False)
        self.settingsBTN.setText(QtGui.QApplication.translate("SubiTMainForm", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(IMAGES_LOCATION, "icon-config.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.settingsBTN.setIcon(icon2)
        self.settingsBTN.setIconSize(QtCore.QSize(32, 32))
        self.settingsBTN.setCheckable(False)
        self.settingsBTN.setAutoRepeat(False)
        self.settingsBTN.setObjectName(_fromUtf8("settingsBTN"))
        self.aboutBTN = QtGui.QCommandLinkButton(self)
        self.aboutBTN.setGeometry(QtCore.QRect(130, 335, 111, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Segoe UI"))
        font.setItalic(False)
        font.setKerning(True)
        self.aboutBTN.setFont(font)
        self.aboutBTN.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.aboutBTN.setAutoFillBackground(False)
        self.aboutBTN.setText(QtGui.QApplication.translate("SubiTMainForm", "About", None, QtGui.QApplication.UnicodeUTF8))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(IMAGES_LOCATION, "icon-about.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.aboutBTN.setIcon(icon3)
        self.aboutBTN.setIconSize(QtCore.QSize(32, 32))
        self.aboutBTN.setCheckable(False)
        self.aboutBTN.setAutoRepeat(False)
        self.aboutBTN.setObjectName(_fromUtf8("aboutBTN"))
        self.aboutBTN.clicked.connect(self.showabout)
        self.settingsBTN.clicked.connect(self.showSettings)
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        pass
   
    @staticmethod    
    def load():
        app = QtGui.QApplication(sys.argv)
        Utils.GuiInstance = gui()
        Utils.GuiInstance.show()
        UpdateGui.Singleton()
        sys.exit(app.exec_())
    
    def writelog(self, message):        
        """Writes log message to the main window"""
        #Utils.sleep(0.05) #Use sleep to avoid to much items waiting for the mutex to release (inside the log write function)
        #Send the log message via the signal
        #self.logTextBrowser.doAddItem.str_signal.emit(message) 
        self.logTextBrowser.addItemAsync(message)
        
    
    #===========================================================
    # Sub selection Handling
    #===========================================================
    def setversionchoices(self, choices, message):       
        self.subselected = False
        self.versionchoices = choices
        
        Utils.writelog( message )
        
        #self.versionsListWidget.setEnabled(True)
        self.versionsListWidget.enable(True)
        self.versionsListWidget.clear()
        
        for choice in choices:
            #self.versionsListWidget.doAddItem.str_signal.emit(gui.getUnicode(choice.VerSum))
            self.versionsListWidget.addItemAsync(gui.getUnicode(choice.VerSum))
            
                
    def getsubselection(self):
        #self.versionsListWidget.setEnabled(True)
        self.versionsListWidget.enable(True)
        self.versionsListWidget.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)
        self.versionsListWidget.doubleClicked.connect(self.notifySubSelection)

    def notifySubSelection(self):
        self.notifyselection('SUB')
    #===========================================================================
    # Movie selection handling
    #===========================================================================
    def setmoviechoices(self, choices, message):
        self.movieselected = False
        self.moviechoices = choices
        
        Utils.writelog( message )

        #self.moviesListWidget.setEnabled(True)        
        self.moviesListWidget.enable(True)        
        self.moviesListWidget.clear()
        
        for choice in choices:
            #self.moviesListWidget.doAddItem.str_signal.emit(gui.getUnicode(choice.MovieName + ' -> ' + choice.VerSum))
            self.moviesListWidget.addItemAsync(gui.getUnicode(choice.MovieName + ' -> ' + choice.VerSum))
            
        self.moviesListWidget.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)
        
    def getmovieselection(self):
        #self.moviesListWidget.setEnabled(True)        
        self.moviesListWidget.enable(True)        
        self.moviesListWidget.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)
        self.moviesListWidget.doubleClicked.connect(self.notifyMovieSelection)

    
    def notifyMovieSelection(self):
        self.notifyselection('MOVIE')

    #===========================================================================
    # Selection logic
    #===========================================================================
    def notifyselection(self, source):
        if source == 'SUB':
            self.subselected = bool(self.versionsListWidget.currentRow()+1)
        elif source == 'MOVIE':
            self.movieselected = bool(self.moviesListWidget.currentRow()+1)
    
    def getselection(self, type):
        selection = ('','')
        if type == 'SUB':
            self.subselected = False
            self.getsubselection()
            #Wait for selection
            while not self.subselected: 
                time.sleep(0.05)
            selection = ('SUB', self.versionchoices[self.versionsListWidget.currentRow()])
            self.versionsListWidget.clear()
                
        elif type == 'MOVIE':
            self.movieselected = False
            self.getmovieselection()
            #Wait for selection
            while not self.movieselected: time.sleep(0.05)
            selection = ('MOVIE', self.moviechoices[self.moviesListWidget.currentRow()])
            
        elif type == 'ANY':
            self.subselected = False
            self.movieselected = False
            self.getsubselection()
            self.getmovieselection()
            
            #Wait for selection
            while (not self.subselected) and (not self.movieselected): 
                time.sleep(0.05)
                
            if self.subselected:
                selection = ('SUB', self.versionchoices[self.versionsListWidget.currentRow()])
                self.versionsListWidget.clear()
                self.moviesListWidget.clear()
                
            elif self.movieselected:
                selection = ('MOVIE', self.moviechoices[self.moviesListWidget.currentRow()])
                
        #self.versionsListWidget.setEnabled(False)
        #self.moviesListWidget.setEnabled(False)

        self.versionsListWidget.enable(False)
        self.moviesListWidget.enable(False)
      
        return selection
            
    #===========================================================================        
    
    def getuserinput(self, message, canempty, withdialog=False):
        Utils.writelog( message )
        return self.inputLineEdit.waitForInput(self.goBTN, canempty=canempty, brwsbtn=self.browseBTN if withdialog else None)
                        
    def showabout(self):
        AboutBoxDialog(self).open()
    
    def showSettings(self):
        self.getSettings().open()
    

    _settingsBoxDialog = None
    def getSettings(self):        
        gui._settingsBoxDialog = None
        sig = Communicate()
        sig.objSignal.connect(self.slot_getSettings)
        sig.objSignal.emit(self)

        while not gui._settingsBoxDialog:
            pass
        return gui._settingsBoxDialog

    @QtCore.Slot(QtGui.QMainWindow)
    def slot_getSettings(self):
        gui._settingsBoxDialog = SettingsBoxDialog(self)
    
    def showUpdate(self):
        sig = Communicate()
        sig.objSignal.connect(self.showUpdateSlot)
        sig.objSignal.emit(self)
        
        
    @QtCore.Slot(QtGui.QMainWindow)
    def showUpdateSlot(self):
        UpdateGui.Singleton().open()

    @staticmethod
    def getUnicode(message):
        return message
        formatted_message = message
        try:
            formatted_message = unicode(formatted_message, 'utf-8')
        except UnicodeDecodeError as eX:
            try:
                formatted_message = unicode(formatted_message)
            except:
                formatted_message = message
        return formatted_message

class Communicate(QtCore.QObject):
    objSignal = QtCore.Signal(QtCore.QObject)