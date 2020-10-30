# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form_image_bbox_editor.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FormImageBboxEditor(object):
    def setupUi(self, FormImageBboxEditor):
        FormImageBboxEditor.setObjectName("FormImageBboxEditor")
        FormImageBboxEditor.resize(684, 471)
        self.verticalLayout = QtWidgets.QVBoxLayout(FormImageBboxEditor)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image = ImageWidget(FormImageBboxEditor)
        self.image.setObjectName("image")
        self.verticalLayout.addWidget(self.image)
        self.labelInfoPath = QtWidgets.QLabel(FormImageBboxEditor)
        self.labelInfoPath.setObjectName("labelInfoPath")
        self.verticalLayout.addWidget(self.labelInfoPath)
        self.labelInfoScale = QtWidgets.QLabel(FormImageBboxEditor)
        self.labelInfoScale.setObjectName("labelInfoScale")
        self.verticalLayout.addWidget(self.labelInfoScale)
        self.listView = QtWidgets.QListView(FormImageBboxEditor)
        self.listView.setObjectName("listView")
        self.verticalLayout.addWidget(self.listView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkboxStayInside = QtWidgets.QCheckBox(FormImageBboxEditor)
        self.checkboxStayInside.setChecked(True)
        self.checkboxStayInside.setObjectName("checkboxStayInside")
        self.horizontalLayout.addWidget(self.checkboxStayInside)
        self.buttonSwitchInOutEditor = QtWidgets.QPushButton(FormImageBboxEditor)
        self.buttonSwitchInOutEditor.setObjectName("buttonSwitchInOutEditor")
        self.horizontalLayout.addWidget(self.buttonSwitchInOutEditor)
        self.buttonSwapInOutEditor = QtWidgets.QPushButton(FormImageBboxEditor)
        self.buttonSwapInOutEditor.setObjectName("buttonSwapInOutEditor")
        self.horizontalLayout.addWidget(self.buttonSwapInOutEditor)
        self.buttonImageNext = QtWidgets.QPushButton(FormImageBboxEditor)
        self.buttonImageNext.setObjectName("buttonImageNext")
        self.horizontalLayout.addWidget(self.buttonImageNext)
        self.buttonImagePrev = QtWidgets.QPushButton(FormImageBboxEditor)
        self.buttonImagePrev.setObjectName("buttonImagePrev")
        self.horizontalLayout.addWidget(self.buttonImagePrev)
        self.buttonDone = QtWidgets.QPushButton(FormImageBboxEditor)
        self.buttonDone.setObjectName("buttonDone")
        self.horizontalLayout.addWidget(self.buttonDone)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(3, 1)

        self.retranslateUi(FormImageBboxEditor)
        QtCore.QMetaObject.connectSlotsByName(FormImageBboxEditor)

    def retranslateUi(self, FormImageBboxEditor):
        _translate = QtCore.QCoreApplication.translate
        FormImageBboxEditor.setWindowTitle(_translate("FormImageBboxEditor", "Form"))
        self.labelInfoPath.setText(_translate("FormImageBboxEditor", "InfoPath"))
        self.labelInfoScale.setText(_translate("FormImageBboxEditor", "InfoScale"))
        self.checkboxStayInside.setText(_translate("FormImageBboxEditor", "Stay Inside Image"))
        self.buttonSwitchInOutEditor.setText(_translate("FormImageBboxEditor", "Switch In/Out Editor"))
        self.buttonSwapInOutEditor.setText(_translate("FormImageBboxEditor", "Swap In/Out"))
        self.buttonImageNext.setText(_translate("FormImageBboxEditor", "Next Image"))
        self.buttonImagePrev.setText(_translate("FormImageBboxEditor", "Prev Image"))
        self.buttonDone.setText(_translate("FormImageBboxEditor", "Done"))


from image_widget import ImageWidget
