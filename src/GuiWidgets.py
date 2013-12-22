from PySide import QtCore, QtGui
import time
import os

import Logs
import Utils
import Gui

class GWTextInput(QtGui.QLineEdit):
    _userInput  = None
    _canEmpty   = False
    def waitForInput(self, gobtn, canempty=False, brwsbtn=None):
        GWTextInput._userInput = None
        sig = Communicator.Singleton()
        sig.input_signal.connect(self.slot_waitForInput)
        sig.input_signal.emit(gobtn, canempty, brwsbtn)

        #Thats the worker thread sleeping, not the gui thread (gui thread is working in slot_waitForInput)
        while GWTextInput._userInput is None:
            pass

        return GWTextInput._userInput

    @QtCore.Slot(QtGui.QPushButton, bool, QtGui.QToolButton)
    def slot_waitForInput(self, gobtn, canempty, brwsbtn):
        self._canEmpty = canempty
        gobtn.setEnabled(False)
        self.setEnabled(True)
        
        if brwsbtn is not None:
            brwsbtn.setEnabled(True)
            brwsbtn.clicked.connect(self.doBrowse)
        
        self.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)

        if not canempty:
            self.textChanged.connect(self.onTextChanged)
        else:
            gobtn.setEnabled(True)
            
    def onTextChanged(self, text):
        Utils.GuiInstance.goBTN.setEnabled(bool(text) or self._canEmpty)

    def onGoPressed(self):
        self.setEnabled(False)
        Utils.GuiInstance.goBTN.setEnabled(False)
        Utils.GuiInstance.browseBTN.setEnabled(False)
        GWTextInput._userInput = str(self.text())
        self.clear()

        
    def doBrowse(self):
        chosendir = QtGui.QFileDialog.getExistingDirectory(None, 'Selected Directory', (self.text() if os.path.isdir(self.text()) else ''))
        self.clear()
        self.setText(chosendir)
        
    def keyPressEvent(self, event):
        if event.key() in (16777220, 16777221) and Utils.GuiInstance.goBTN.isEnabled():
            self.onGoPressed()
        QtGui.QLineEdit.keyPressEvent(self, event)

class Communicator(QtCore.QObject):
    _comm = None
    @staticmethod
    def Singleton():
        if Communicator._comm is None:
            Communicator._comm = Communicator()
        return Communicator._comm

    str_signal      = QtCore.Signal(str)
    log_signal      = QtCore.Signal(str)
    input_signal    = QtCore.Signal(QtGui.QPushButton, bool, QtGui.QToolButton)
    obj_signal      = QtCore.Signal(QtCore.QObject)
    bool_signal     = QtCore.Signal(bool)

#===============================================================================
# Special class is made in order to supply a new signal -> sendAddItem, because 
# of the multi-threading (cross-thread and so...)
#===============================================================================
class GWListWidget_Log(QtGui.QListWidget):
    _mutex = QtCore.QMutex()
    _comm = None
    def __init__(self, parent):
        super(GWListWidget_Log, self).__init__(parent)
        self._comm = Communicator()
        self._comm.log_signal.connect(self.sendAddItem)

    def addItemAsync(self, message):
        self._comm = Communicator()
        self._comm.log_signal.connect(self.sendAddItem)
        self._comm.log_signal.emit(message)

    @QtCore.Slot(str)
    def sendAddItem(self, log_message):
        try:
            QtCore.QMutexLocker(GWListWidget._mutex).relock()
            delim = Logs.LOGS.DELIMITER #String Splitter
            splitted_message = log_message.split(delim)
            color_message   = splitted_message[0] if len(splitted_message) > 1 else 'OTHER'
            real_message    = splitted_message[1] if len(splitted_message) > 1 else splitted_message[0]

            #Use dict in order to get the color
            color = (Logs.LOGS.TYPE_TO_COLOR[color_message] if color_message in Logs.LOGS.
                     TYPE_TO_COLOR else Logs.LOGS.TYPE_TO_COLOR['OTHER'])

            logItem = QtGui.QListWidgetItem(Gui.gui.getUnicode(real_message))
            logItem.setForeground(QtGui.QBrush(QtGui.QColor(color)))
        
            #Insert log message, and scroll to latest line
            self.addItem(logItem)        
            self.setCurrentItem(logItem)            
            self.scrollToItem(logItem, QtGui.QAbstractItemView.ScrollHint.EnsureVisible)        
        except:
            QtCore.QMutexLocker(GWListWidget._mutex).unlock()

class GWListWidget(QtGui.QListWidget):
    _mutex = QtCore.QMutex()
    _comm = None
    def __init__(self, parent):
        super(GWListWidget, self).__init__(parent)
        self._comm = Communicator()
        self._comm.str_signal.connect(self.sendAddItem)
        self._comm.bool_signal.connect(self.slot_enable)

    def addItemAsync(self, message):
        self._comm.str_signal.emit(message)

    def enable(self, bool_val):
        self._comm.bool_signal.emit(bool_val)
    @QtCore.Slot(bool)
    def slot_enable(self, bool_val):
        self.setEnabled(bool_val)
    @QtCore.Slot(str)
    def sendAddItem(self, message):
        try:
            QtCore.QMutexLocker(GWListWidget._mutex).relock()
            
            logItem = QtGui.QListWidgetItem(message)
            #logItem.setForeground(QtGui.QBrush(QtGui.QColor(color)))
            #Insert log message, and scroll to latest line
            self.addItem(logItem)        
            self.setCurrentItem(logItem)            
            self.scrollToItem(logItem, QtGui.QAbstractItemView.ScrollHint.EnsureVisible)        
        except:
            QtCore.QMutexLocker(GWListWidget._mutex).unlock()
    