# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\MainWindowGui.ui'
#
# Created: Thu Aug 21 15:17:18 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setEnabled(True)
        MainWindow.resize(536, 534)
        MainWindow.setWindowOpacity(1.0)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(0, 0, 391, 271))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setLineWidth(3)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayoutWidget_3 = QtGui.QWidget(self.frame)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(10, 10, 372, 251))
        self.gridLayoutWidget_3.setObjectName(_fromUtf8("gridLayoutWidget_3"))
        self.Scan_gridLayout = QtGui.QGridLayout(self.gridLayoutWidget_3)
        self.Scan_gridLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.Scan_gridLayout.setMargin(0)
        self.Scan_gridLayout.setObjectName(_fromUtf8("Scan_gridLayout"))
        self.label_12 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.Scan_gridLayout.addWidget(self.label_12, 5, 0, 1, 1)
        self.Scan_1st_Range = QtGui.QDoubleSpinBox(self.gridLayoutWidget_3)
        self.Scan_1st_Range.setMinimum(0.01)
        self.Scan_1st_Range.setMaximum(9999.0)
        self.Scan_1st_Range.setSingleStep(1.0)
        self.Scan_1st_Range.setProperty("value", 10.0)
        self.Scan_1st_Range.setObjectName(_fromUtf8("Scan_1st_Range"))
        self.Scan_gridLayout.addWidget(self.Scan_1st_Range, 4, 2, 1, 1)
        self.Scan_start_pushButton = QtGui.QPushButton(self.gridLayoutWidget_3)
        self.Scan_start_pushButton.setObjectName(_fromUtf8("Scan_start_pushButton"))
        self.Scan_gridLayout.addWidget(self.Scan_start_pushButton, 7, 0, 1, 5)
        self.Scan_2nd_Accuracy = QtGui.QDoubleSpinBox(self.gridLayoutWidget_3)
        self.Scan_2nd_Accuracy.setMinimum(0.01)
        self.Scan_2nd_Accuracy.setMaximum(10000.0)
        self.Scan_2nd_Accuracy.setProperty("value", 0.1)
        self.Scan_2nd_Accuracy.setObjectName(_fromUtf8("Scan_2nd_Accuracy"))
        self.Scan_gridLayout.addWidget(self.Scan_2nd_Accuracy, 5, 3, 1, 1)
        self.Scan_3rd_UnitLabel = QtGui.QLabel(self.gridLayoutWidget_3)
        self.Scan_3rd_UnitLabel.setObjectName(_fromUtf8("Scan_3rd_UnitLabel"))
        self.Scan_gridLayout.addWidget(self.Scan_3rd_UnitLabel, 6, 4, 1, 1)
        self.Scan_3rd_Range = QtGui.QDoubleSpinBox(self.gridLayoutWidget_3)
        self.Scan_3rd_Range.setMinimum(0.01)
        self.Scan_3rd_Range.setMaximum(9999.0)
        self.Scan_3rd_Range.setProperty("value", 10.0)
        self.Scan_3rd_Range.setObjectName(_fromUtf8("Scan_3rd_Range"))
        self.Scan_gridLayout.addWidget(self.Scan_3rd_Range, 6, 2, 1, 1)
        self.label_11 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.Scan_gridLayout.addWidget(self.label_11, 4, 0, 1, 1)
        self.label_14 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.Scan_gridLayout.addWidget(self.label_14, 1, 1, 1, 1)
        self.label_9 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_9.setStyleSheet(_fromUtf8("font: 14pt \"MS Shell Dlg 2\";"))
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.Scan_gridLayout.addWidget(self.label_9, 0, 0, 1, 5)
        self.Scan_3rd_comboBox = QtGui.QComboBox(self.gridLayoutWidget_3)
        self.Scan_3rd_comboBox.setObjectName(_fromUtf8("Scan_3rd_comboBox"))
        self.Scan_3rd_comboBox.addItem(_fromUtf8(""))
        self.Scan_gridLayout.addWidget(self.Scan_3rd_comboBox, 6, 1, 1, 1)
        self.label_13 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.Scan_gridLayout.addWidget(self.label_13, 6, 0, 1, 1)
        self.Scan_2nd_UnitLabel = QtGui.QLabel(self.gridLayoutWidget_3)
        self.Scan_2nd_UnitLabel.setObjectName(_fromUtf8("Scan_2nd_UnitLabel"))
        self.Scan_gridLayout.addWidget(self.Scan_2nd_UnitLabel, 5, 4, 1, 1)
        self.Scan_2nd_Range = QtGui.QDoubleSpinBox(self.gridLayoutWidget_3)
        self.Scan_2nd_Range.setMinimum(0.01)
        self.Scan_2nd_Range.setMaximum(9999.0)
        self.Scan_2nd_Range.setProperty("value", 10.0)
        self.Scan_2nd_Range.setObjectName(_fromUtf8("Scan_2nd_Range"))
        self.Scan_gridLayout.addWidget(self.Scan_2nd_Range, 5, 2, 1, 1)
        self.Scan_2nd_comboBox = QtGui.QComboBox(self.gridLayoutWidget_3)
        self.Scan_2nd_comboBox.setObjectName(_fromUtf8("Scan_2nd_comboBox"))
        self.Scan_2nd_comboBox.addItem(_fromUtf8(""))
        self.Scan_gridLayout.addWidget(self.Scan_2nd_comboBox, 5, 1, 1, 1)
        self.Scan_1st_UnitLabel = QtGui.QLabel(self.gridLayoutWidget_3)
        self.Scan_1st_UnitLabel.setObjectName(_fromUtf8("Scan_1st_UnitLabel"))
        self.Scan_gridLayout.addWidget(self.Scan_1st_UnitLabel, 4, 4, 1, 1)
        self.Scan_Detector_comboBox = QtGui.QComboBox(self.gridLayoutWidget_3)
        self.Scan_Detector_comboBox.setObjectName(_fromUtf8("Scan_Detector_comboBox"))
        self.Scan_gridLayout.addWidget(self.Scan_Detector_comboBox, 3, 1, 1, 1)
        self.label_10 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.Scan_gridLayout.addWidget(self.label_10, 3, 0, 1, 1)
        self.label_15 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.Scan_gridLayout.addWidget(self.label_15, 1, 2, 1, 1)
        self.label_4 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.Scan_gridLayout.addWidget(self.label_4, 1, 4, 1, 1)
        self.Scan_Detector_UnitLabel = QtGui.QLabel(self.gridLayoutWidget_3)
        self.Scan_Detector_UnitLabel.setObjectName(_fromUtf8("Scan_Detector_UnitLabel"))
        self.Scan_gridLayout.addWidget(self.Scan_Detector_UnitLabel, 3, 4, 1, 1)
        self.Scan_stop_pushButton = QtGui.QPushButton(self.gridLayoutWidget_3)
        self.Scan_stop_pushButton.setObjectName(_fromUtf8("Scan_stop_pushButton"))
        self.Scan_gridLayout.addWidget(self.Scan_stop_pushButton, 8, 0, 1, 5)
        self.label_18 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.Scan_gridLayout.addWidget(self.label_18, 1, 3, 1, 1)
        self.Scan_1st_Accuracy = QtGui.QDoubleSpinBox(self.gridLayoutWidget_3)
        self.Scan_1st_Accuracy.setMinimum(0.01)
        self.Scan_1st_Accuracy.setMaximum(10000.0)
        self.Scan_1st_Accuracy.setProperty("value", 0.1)
        self.Scan_1st_Accuracy.setObjectName(_fromUtf8("Scan_1st_Accuracy"))
        self.Scan_gridLayout.addWidget(self.Scan_1st_Accuracy, 4, 3, 1, 1)
        self.Scan_3rd_Accuracy = QtGui.QDoubleSpinBox(self.gridLayoutWidget_3)
        self.Scan_3rd_Accuracy.setMinimum(0.01)
        self.Scan_3rd_Accuracy.setMaximum(10000.0)
        self.Scan_3rd_Accuracy.setProperty("value", 0.1)
        self.Scan_3rd_Accuracy.setObjectName(_fromUtf8("Scan_3rd_Accuracy"))
        self.Scan_gridLayout.addWidget(self.Scan_3rd_Accuracy, 6, 3, 1, 1)
        self.Scan_Detector_UnitLabel_2 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.Scan_Detector_UnitLabel_2.setObjectName(_fromUtf8("Scan_Detector_UnitLabel_2"))
        self.Scan_gridLayout.addWidget(self.Scan_Detector_UnitLabel_2, 2, 4, 1, 1)
        self.label_17 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.Scan_gridLayout.addWidget(self.label_17, 2, 1, 1, 1)
        self.Scan_Delay_Range = QtGui.QDoubleSpinBox(self.gridLayoutWidget_3)
        self.Scan_Delay_Range.setMinimum(1.0)
        self.Scan_Delay_Range.setMaximum(10000.0)
        self.Scan_Delay_Range.setProperty("value", 10.0)
        self.Scan_Delay_Range.setObjectName(_fromUtf8("Scan_Delay_Range"))
        self.Scan_gridLayout.addWidget(self.Scan_Delay_Range, 2, 2, 1, 1)
        self.label_16 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.Scan_gridLayout.addWidget(self.label_16, 2, 0, 1, 1)
        self.Scan_1st_comboBox = QtGui.QComboBox(self.gridLayoutWidget_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Scan_1st_comboBox.sizePolicy().hasHeightForWidth())
        self.Scan_1st_comboBox.setSizePolicy(sizePolicy)
        self.Scan_1st_comboBox.setObjectName(_fromUtf8("Scan_1st_comboBox"))
        self.Scan_1st_comboBox.addItem(_fromUtf8(""))
        self.Scan_gridLayout.addWidget(self.Scan_1st_comboBox, 4, 1, 1, 1)
        self.Scan_Mult_Detector_comboBox = QtGui.QCheckBox(self.gridLayoutWidget_3)
        self.Scan_Mult_Detector_comboBox.setObjectName(_fromUtf8("Scan_Mult_Detector_comboBox"))
        self.Scan_gridLayout.addWidget(self.Scan_Mult_Detector_comboBox, 3, 2, 1, 1)
        self.Scan_Dropdown = dropdown(self.gridLayoutWidget_3)
        self.Scan_Dropdown.setMinimumSize(QtCore.QSize(75, 0))
        self.Scan_Dropdown.setObjectName(_fromUtf8("Scan_Dropdown"))
        self.Scan_gridLayout.addWidget(self.Scan_Dropdown, 3, 3, 1, 1)
        self.frame_2 = QtGui.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(390, 0, 141, 271))
        self.frame_2.setFrameShape(QtGui.QFrame.Box)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setLineWidth(3)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.gridLayoutWidget = QtGui.QWidget(self.frame_2)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 121, 251))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.Monitor_gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.Monitor_gridLayout.setMargin(0)
        self.Monitor_gridLayout.setObjectName(_fromUtf8("Monitor_gridLayout"))
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setStyleSheet(_fromUtf8("font: 14pt \"MS Shell Dlg 2\";"))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.Monitor_gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.Monitor_comboBox = QtGui.QComboBox(self.gridLayoutWidget)
        self.Monitor_comboBox.setObjectName(_fromUtf8("Monitor_comboBox"))
        self.Monitor_gridLayout.addWidget(self.Monitor_comboBox, 1, 0, 1, 1)
        self.Monitor_pushButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.Monitor_pushButton.setObjectName(_fromUtf8("Monitor_pushButton"))
        self.Monitor_gridLayout.addWidget(self.Monitor_pushButton, 2, 0, 1, 1)
        self.frame_3 = QtGui.QFrame(self.centralwidget)
        self.frame_3.setGeometry(QtCore.QRect(0, 270, 531, 221))
        self.frame_3.setFrameShape(QtGui.QFrame.Box)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setLineWidth(3)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.gridLayoutWidget_2 = QtGui.QWidget(self.frame_3)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 511, 201))
        self.gridLayoutWidget_2.setObjectName(_fromUtf8("gridLayoutWidget_2"))
        self.Controler_gridLayout = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.Controler_gridLayout.setMargin(0)
        self.Controler_gridLayout.setObjectName(_fromUtf8("Controler_gridLayout"))
        self.label_7 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.Controler_gridLayout.addWidget(self.label_7, 5, 2, 1, 1)
        self.label_8 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.Controler_gridLayout.addWidget(self.label_8, 5, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.Controler_gridLayout.addWidget(self.label_6, 5, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_2.setStyleSheet(_fromUtf8("font: 14pt \"MS Shell Dlg 2\";"))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.Controler_gridLayout.addWidget(self.label_2, 1, 0, 1, 5)
        self.Controler_BusyLabel = QtGui.QLabel(self.gridLayoutWidget_2)
        self.Controler_BusyLabel.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);\n"
"font: 14pt \"MS Shell Dlg 2\";"))
        self.Controler_BusyLabel.setText(_fromUtf8(""))
        self.Controler_BusyLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.Controler_BusyLabel.setObjectName(_fromUtf8("Controler_BusyLabel"))
        self.Controler_gridLayout.addWidget(self.Controler_BusyLabel, 5, 3, 1, 2)
        self.Controler_Go = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.Controler_Go.setObjectName(_fromUtf8("Controler_Go"))
        self.Controler_gridLayout.addWidget(self.Controler_Go, 2, 3, 1, 2)
        self.Controler_Select_scan = QtGui.QComboBox(self.gridLayoutWidget_2)
        self.Controler_Select_scan.setObjectName(_fromUtf8("Controler_Select_scan"))
        self.Controler_gridLayout.addWidget(self.Controler_Select_scan, 2, 0, 1, 3)
        self.Controler_Refocus = QtGui.QPushButton(self.gridLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Controler_Refocus.sizePolicy().hasHeightForWidth())
        self.Controler_Refocus.setSizePolicy(sizePolicy)
        self.Controler_Refocus.setObjectName(_fromUtf8("Controler_Refocus"))
        self.Controler_gridLayout.addWidget(self.Controler_Refocus, 3, 4, 2, 1)
        self.label_21 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.Controler_gridLayout.addWidget(self.label_21, 3, 3, 1, 1)
        self.Controler_3rd_comboBox = QtGui.QComboBox(self.gridLayoutWidget_2)
        self.Controler_3rd_comboBox.setObjectName(_fromUtf8("Controler_3rd_comboBox"))
        self.Controler_3rd_comboBox.addItem(_fromUtf8(""))
        self.Controler_gridLayout.addWidget(self.Controler_3rd_comboBox, 4, 3, 1, 1)
        self.Controler_2nd_comboBox = QtGui.QComboBox(self.gridLayoutWidget_2)
        self.Controler_2nd_comboBox.setObjectName(_fromUtf8("Controler_2nd_comboBox"))
        self.Controler_2nd_comboBox.addItem(_fromUtf8(""))
        self.Controler_gridLayout.addWidget(self.Controler_2nd_comboBox, 4, 2, 1, 1)
        self.label_20 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.Controler_gridLayout.addWidget(self.label_20, 3, 2, 1, 1)
        self.label_19 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.Controler_gridLayout.addWidget(self.label_19, 3, 1, 1, 1)
        self.Controler_1st_comboBox = QtGui.QComboBox(self.gridLayoutWidget_2)
        self.Controler_1st_comboBox.setObjectName(_fromUtf8("Controler_1st_comboBox"))
        self.Controler_gridLayout.addWidget(self.Controler_1st_comboBox, 4, 1, 1, 1)
        self.Controler_Detector_comboBox = QtGui.QComboBox(self.gridLayoutWidget_2)
        self.Controler_Detector_comboBox.setObjectName(_fromUtf8("Controler_Detector_comboBox"))
        self.Controler_gridLayout.addWidget(self.Controler_Detector_comboBox, 4, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.Controler_gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 536, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label_12.setText(_translate("MainWindow", "2nd Direction", None))
        self.Scan_start_pushButton.setText(_translate("MainWindow", "Start", None))
        self.Scan_3rd_UnitLabel.setText(_translate("MainWindow", "None", None))
        self.label_11.setText(_translate("MainWindow", "1st Direction", None))
        self.label_14.setText(_translate("MainWindow", "Device", None))
        self.label_9.setText(_translate("MainWindow", "Scan", None))
        self.Scan_3rd_comboBox.setItemText(0, _translate("MainWindow", "None", None))
        self.label_13.setText(_translate("MainWindow", "3rd Direction", None))
        self.Scan_2nd_UnitLabel.setText(_translate("MainWindow", "None", None))
        self.Scan_2nd_comboBox.setItemText(0, _translate("MainWindow", "None", None))
        self.Scan_1st_UnitLabel.setText(_translate("MainWindow", "s", None))
        self.label_10.setText(_translate("MainWindow", "Detector", None))
        self.label_15.setText(_translate("MainWindow", "Range", None))
        self.label_4.setText(_translate("MainWindow", "Units", None))
        self.Scan_Detector_UnitLabel.setText(_translate("MainWindow", "TextLabel", None))
        self.Scan_stop_pushButton.setText(_translate("MainWindow", "Stop", None))
        self.label_18.setText(_translate("MainWindow", "Accuracy", None))
        self.Scan_Detector_UnitLabel_2.setText(_translate("MainWindow", "ms", None))
        self.label_17.setText(_translate("MainWindow", "Adwin", None))
        self.label_16.setText(_translate("MainWindow", "Delay", None))
        self.Scan_1st_comboBox.setItemText(0, _translate("MainWindow", "Time", None))
        self.Scan_Mult_Detector_comboBox.setText(_translate("MainWindow", "Mult Detect", None))
        self.label.setText(_translate("MainWindow", "Monitor", None))
        self.Monitor_pushButton.setText(_translate("MainWindow", "Show", None))
        self.label_7.setText(_translate("MainWindow", "Increment", None))
        self.label_8.setText(_translate("MainWindow", "Name", None))
        self.label_6.setText(_translate("MainWindow", "Position", None))
        self.label_2.setText(_translate("MainWindow", "Device Controler", None))
        self.Controler_Go.setText(_translate("MainWindow", "Go to position", None))
        self.Controler_Refocus.setText(_translate("MainWindow", "Refocus", None))
        self.label_21.setText(_translate("MainWindow", "3rd Direction", None))
        self.Controler_3rd_comboBox.setItemText(0, _translate("MainWindow", "None", None))
        self.Controler_2nd_comboBox.setItemText(0, _translate("MainWindow", "None", None))
        self.label_20.setText(_translate("MainWindow", "2nd Direction", None))
        self.label_19.setText(_translate("MainWindow", "1st Direction", None))
        self.label_3.setText(_translate("MainWindow", "Detector", None))

from dropdown import dropdown
