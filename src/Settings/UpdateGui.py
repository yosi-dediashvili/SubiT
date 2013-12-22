# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SubiT_UI_Update.ui'
#
# Created: Fri Jan 27 11:07:43 2012
#      by: pyside-uic 0.2.13 running on PySide 1.0.9
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import os
import Gui
import Utils

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class UpdateGui(QtGui.QDialog):
    _Singelton = None
    @staticmethod
    def Singleton():
        if not UpdateGui._Singelton:
            UpdateGui._Singelton = UpdateGui(Utils.GuiInstance)
        return UpdateGui._Singelton


    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.setObjectName(_fromUtf8("UpdateGui"))
        self.resize(414, 75)
        self.setMinimumSize(QtCore.QSize(414, 75))
        self.setMaximumSize(QtCore.QSize(414, 75))
        self.setWindowTitle(QtGui.QApplication.translate("UpdateGui", "SubiT - Update", None, QtGui.QApplication.UnicodeUTF8))
        self.setModal(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(Gui.IMAGES_LOCATION, "icon.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        
        
        self.logLabel = QtGui.QLabel(self)
        self.logLabel.setGeometry(QtCore.QRect(80, 25, 311, 21))
        self.logLabel.setObjectName("logLabel")
        self.logLabel.setText('...')
        self.gifLabel = QtGui.QLabel(self)
        self.gifLabel.setGeometry(QtCore.QRect(10, 12, 40, 51))
        self.gifLabel.setObjectName("gifLabel")
        Utils.WriteDebug('Preload path: %s' % os.path.join(Gui.IMAGES_LOCATION, 'updatePreload.gif'))
        self.preloadMovie = QtGui.QMovie(os.path.join(Gui.IMAGES_LOCATION, 'updatePreload.gif'))
        self.preloadMovie.setSpeed(70)
        self.preloadMovie.start()
        self.gifLabel.setMovie(self.preloadMovie)


    def retranslateUi(self):
        pass

    def writeLog(self, message):
        self.logLabel.setText(message)

    def doCloseEvent(self):
        sig = Communicate()
        sig.objSignal.connect(self.doClose)
        sig.objSignal.emit(self)

    def askUserForLink(self, message, link):
        sig = Communicate()
        sig.mbSignal.connect(self.slot_askUserForLink)
        sig.mbSignal.emit(message, link)

    @QtCore.Slot(str, str)
    def slot_askUserForLink(self, message, link):
        #self = UpdateGui.Singleton()
        self.doCloseEvent()
        ret = QtGui.QMessageBox.question(   Utils.GuiInstance, 'Update',
                                            message,
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            import webbrowser
            webbrowser.get().open(link)

    @QtCore.Slot(QtGui.QDialog)
    def doClose(self, w):
        w.accept()

class Communicate(QtCore.QObject):
    objSignal   = QtCore.Signal(QtCore.QObject)
    mbSignal    = QtCore.Signal(str, str)