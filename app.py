import sys
#from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtCore, QtGui, QtWidgets
from main_window import Ui_MainWindow

class AppWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.buttonDone.clicked.connect(self.on_button_clicked)
		self.ui.image.openImage('/media/miso/data/foto/2016-08-24..27 Torquay 1/export/IMG_0465.jpg')
		self.show()

	def on_button_clicked(self):
		print('clicked')

app = QtWidgets.QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())

