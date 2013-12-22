# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/dev/SubiT/2.1.0/resources/gui\SubiTUpdateUi.ui'
#
# Created: Sun Oct 07 14:39:56 2012
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_UpdateDialog(object):
    def setupUi(self, UpdateDialog):
        UpdateDialog.setObjectName("UpdateDialog")
        UpdateDialog.resize(350, 180)
        UpdateDialog.setMinimumSize(QtCore.QSize(350, 180))
        UpdateDialog.setMaximumSize(QtCore.QSize(350, 180))
        UpdateDialog.setSizeIncrement(QtCore.QSize(350, 180))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Global/icon-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        UpdateDialog.setWindowIcon(icon)
        UpdateDialog.setAutoFillBackground(False)
        self.verticalLayout = QtGui.QVBoxLayout(UpdateDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtGui.QLabel(UpdateDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.groupBox = QtGui.QGroupBox(UpdateDialog)
        self.groupBox.setTitle("")
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.currentVersionLabel = QtGui.QLabel(self.groupBox)
        self.currentVersionLabel.setAutoFillBackground(False)
        self.currentVersionLabel.setObjectName("currentVersionLabel")
        self.horizontalLayout.addWidget(self.currentVersionLabel)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 8)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.latestVersionLabel = QtGui.QLabel(self.groupBox)
        self.latestVersionLabel.setObjectName("latestVersionLabel")
        self.horizontalLayout_2.addWidget(self.latestVersionLabel)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 8)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addWidget(self.groupBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.label_6 = QtGui.QLabel(UpdateDialog)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_3.addWidget(self.label_6)
        self.latestVersionLinkLabel = QtGui.QLabel(UpdateDialog)
        self.latestVersionLinkLabel.setTextFormat(QtCore.Qt.RichText)
        self.latestVersionLinkLabel.setOpenExternalLinks(True)
        self.latestVersionLinkLabel.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.latestVersionLinkLabel.setObjectName("latestVersionLinkLabel")
        self.verticalLayout_3.addWidget(self.latestVersionLinkLabel)
        self.buttonBox = QtGui.QDialogButtonBox(UpdateDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3.setStretch(0, 6)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(UpdateDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), UpdateDialog.close)
        QtCore.QMetaObject.connectSlotsByName(UpdateDialog)

    def retranslateUi(self, UpdateDialog):
        UpdateDialog.setWindowTitle(QtGui.QApplication.translate("UpdateDialog", "New Version of SubiT", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("UpdateDialog", "New version of SubiT is available!", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("UpdateDialog", "Your version is:", None, QtGui.QApplication.UnicodeUTF8))
        self.currentVersionLabel.setText(QtGui.QApplication.translate("UpdateDialog", "1.3.1", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("UpdateDialog", "Latest version is:", None, QtGui.QApplication.UnicodeUTF8))
        self.latestVersionLabel.setText(QtGui.QApplication.translate("UpdateDialog", "2.0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("UpdateDialog", "You can get the latest version from:", None, QtGui.QApplication.UnicodeUTF8))
        self.latestVersionLinkLabel.setText(QtGui.QApplication.translate("UpdateDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.subit-app.sourceforge.net\"><span style=\" text-decoration: underline; color:#0000ff;\">http://www.subit-app.sourceforge.net</span></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

from Interaction import ImagesResources
