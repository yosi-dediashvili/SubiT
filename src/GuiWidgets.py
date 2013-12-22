from PySide import QtCore, QtGui
import time
import Utils
import os

class GWTextInput(QtGui.QLineEdit):
    def waitForInput(self, gobtn, canempty=False, brwsbtn=None):
        self.goBTN = gobtn
        self.goBTN.setChecked(False)
        self.setEnabled(True)
        if brwsbtn is not None:
            brwsbtn.setEnabled(True)
            brwsbtn.clicked.connect(self.doBrowse)
            
        self.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)
        
        if not canempty:
            self.textChanged.connect(self.onTextChanged)
            
        else:
            self.goBTN.setEnabled(True)
        
        while not gobtn.isChecked():
           time.sleep(0.05) 
        
        self.setEnabled(False)
        gobtn.setEnabled(False)
        if brwsbtn is not None:
            brwsbtn.setEnabled(False)
        input = str(self.text())
        self.clear()
        return input
    
    def onTextChanged(self, text):
        self.goBTN.setEnabled(len(text) > 0)

        
    def doBrowse(self):
        chosendir = QtGui.QFileDialog.getExistingDirectory(None, 'Selected Directory', (self.text() if os.path.isdir(self.text()) else ''))
        self.clear()
        self.setText(chosendir)
        
    def keyPressEvent(self, event):
        if event.key() in (16777220, 16777221) and self.goBTN.isEnabled():
            self.goBTN.setChecked(True)
        QtGui.QLineEdit.keyPressEvent(self, event)

class Communicator(QtCore.QObject):
    str_signal = QtCore.Signal(str)

#===============================================================================
# Special class is made in order to supply a new signal -> sendAddItem, because 
# of the multi-threading (cross-thread and so...)
#===============================================================================
class GWListWidget(QtGui.QListWidget):
    def __init__(self, parent):
        super(GWListWidget, self).__init__(parent)
        self.doAddItem = Communicator()
        self.doAddItem.str_signal.connect(self.sendAddItem)
        
    @QtCore.Slot(str)
    def sendAddItem(self, item):
        self.addItem(item)