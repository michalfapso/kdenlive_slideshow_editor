# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image = ImageWidget(self.centralwidget)
        self.image.setObjectName("image")
        self.verticalLayout.addWidget(self.image)
        self.labelInfoPath = QtWidgets.QLabel(self.centralwidget)
        self.labelInfoPath.setObjectName("labelInfoPath")
        self.verticalLayout.addWidget(self.labelInfoPath)
        self.labelInfoScale = QtWidgets.QLabel(self.centralwidget)
        self.labelInfoScale.setObjectName("labelInfoScale")
        self.verticalLayout.addWidget(self.labelInfoScale)
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setObjectName("listView")
        self.verticalLayout.addWidget(self.listView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkboxStayInside = QtWidgets.QCheckBox(self.centralwidget)
        self.checkboxStayInside.setChecked(True)
        self.checkboxStayInside.setObjectName("checkboxStayInside")
        self.horizontalLayout.addWidget(self.checkboxStayInside)
        self.buttonSwitchInOutEditor = QtWidgets.QPushButton(self.centralwidget)
        self.buttonSwitchInOutEditor.setObjectName("buttonSwitchInOutEditor")
        self.horizontalLayout.addWidget(self.buttonSwitchInOutEditor)
        self.buttonSwapInOutEditor = QtWidgets.QPushButton(self.centralwidget)
        self.buttonSwapInOutEditor.setObjectName("buttonSwapInOutEditor")
        self.horizontalLayout.addWidget(self.buttonSwapInOutEditor)
        self.buttonImageNext = QtWidgets.QPushButton(self.centralwidget)
        self.buttonImageNext.setObjectName("buttonImageNext")
        self.horizontalLayout.addWidget(self.buttonImageNext)
        self.buttonImagePrev = QtWidgets.QPushButton(self.centralwidget)
        self.buttonImagePrev.setObjectName("buttonImagePrev")
        self.horizontalLayout.addWidget(self.buttonImagePrev)
        self.buttonDone = QtWidgets.QPushButton(self.centralwidget)
        self.buttonDone.setObjectName("buttonDone")
        self.horizontalLayout.addWidget(self.buttonDone)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(3, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.labelInfoPath.setText(_translate("MainWindow", "InfoPath"))
        self.labelInfoScale.setText(_translate("MainWindow", "InfoScale"))
        self.checkboxStayInside.setText(_translate("MainWindow", "Stay Inside Image"))
        self.buttonSwitchInOutEditor.setText(_translate("MainWindow", "Switch In/Out Editor"))
        self.buttonSwapInOutEditor.setText(_translate("MainWindow", "Swap In/Out"))
        self.buttonImageNext.setText(_translate("MainWindow", "Next Image"))
        self.buttonImagePrev.setText(_translate("MainWindow", "Prev Image"))
        self.buttonDone.setText(_translate("MainWindow", "Done"))


from image_widget import ImageWidget
