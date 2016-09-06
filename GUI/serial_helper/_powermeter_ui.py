# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'powermeter.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_PowermeterWindow(object):
    def setupUi(self, PowermeterWindow):
        PowermeterWindow.setObjectName(_fromUtf8("PowermeterWindow"))
        PowermeterWindow.resize(581, 268)
        self.centralwidget = QtGui.QWidget(PowermeterWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.lcdPower = QtGui.QLCDNumber(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lcdPower.sizePolicy().hasHeightForWidth())
        self.lcdPower.setSizePolicy(sizePolicy)
        self.lcdPower.setObjectName(_fromUtf8("lcdPower"))
        self.horizontalLayout_9.addWidget(self.lcdPower)
        self.lblUnit = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblUnit.sizePolicy().hasHeightForWidth())
        self.lblUnit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(48)
        self.lblUnit.setFont(font)
        self.lblUnit.setObjectName(_fromUtf8("lblUnit"))
        self.horizontalLayout_9.addWidget(self.lblUnit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_8.addWidget(self.label_2)
        self.txtLambda = QtGui.QLineEdit(self.centralwidget)
        self.txtLambda.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtLambda.sizePolicy().hasHeightForWidth())
        self.txtLambda.setSizePolicy(sizePolicy)
        self.txtLambda.setBaseSize(QtCore.QSize(100, 0))
        self.txtLambda.setObjectName(_fromUtf8("txtLambda"))
        self.horizontalLayout_8.addWidget(self.txtLambda)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_8.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem)
        self.chkAttn = QtGui.QCheckBox(self.centralwidget)
        self.chkAttn.setObjectName(_fromUtf8("chkAttn"))
        self.horizontalLayout_8.addWidget(self.chkAttn)
        spacerItem1 = QtGui.QSpacerItem(58, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem1)
        self.btnConnect = QtGui.QPushButton(self.centralwidget)
        self.btnConnect.setObjectName(_fromUtf8("btnConnect"))
        self.horizontalLayout_8.addWidget(self.btnConnect)
        self.btnChart = QtGui.QPushButton(self.centralwidget)
        self.btnChart.setObjectName(_fromUtf8("btnChart"))
        self.horizontalLayout_8.addWidget(self.btnChart)
        self.verticalLayout_2.addLayout(self.horizontalLayout_8)
        PowermeterWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(PowermeterWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 581, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        PowermeterWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(PowermeterWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        PowermeterWindow.setStatusBar(self.statusbar)

        self.retranslateUi(PowermeterWindow)
        QtCore.QMetaObject.connectSlotsByName(PowermeterWindow)

    def retranslateUi(self, PowermeterWindow):
        PowermeterWindow.setWindowTitle(_translate("PowermeterWindow", "Power Meter", None))
        self.lblUnit.setText(_translate("PowermeterWindow", "mW", None))
        self.label_2.setText(_translate("PowermeterWindow", "Wavelength", None))
        self.label.setText(_translate("PowermeterWindow", "nm", None))
        self.chkAttn.setText(_translate("PowermeterWindow", "ATTN", None))
        self.btnConnect.setText(_translate("PowermeterWindow", "Connect", None))
        self.btnChart.setText(_translate("PowermeterWindow", "Show Chart", None))

