import sys
from PyQt5.QtCore import QRect, QRectF
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPainter, QColor
from bbox_editor import BboxEditor

class ImageWidget(QWidget):
	def __init__(self, parent=None):
		print('ImageWidget()')
		super().__init__(parent)
		self.bboxEditor = BboxEditor(self)
		self.bboxEditor.setColor(QColor(255, 0, 0))
		self.bboxEditor.setActive(True)
		self.bboxEditor.changed.connect(self.update)
		self.img = QImage()

	def setTargetRatio(self, ratio):
		self.targetRatio = ratio

	def openImage(self, path):
		self.img.load(path)
		self.bboxEditor.setBbox01(QRectF(0.1, 0.1, 0.8, 0.8))
		self.update()

	def paintEvent(self, e):
		print('ImageWidget::paintEvent()', e)
		qpainter = QPainter(self)
		#qpainter.drawImage(QRect(0, 0, self.width(), self.height()), self.img)
		qpainter.drawImage(self.getImageRect(), self.img)
		self.bboxEditor.paint(qpainter)

	def resizeEvent(self, e):
		self.bboxEditor.setDrawingArea(self.getImageRect())
		print('ImageWidget::resizeEvent()', e)

	def mouseMoveEvent(self, e):
		self.bboxEditor.mouseMoveEvent(e)

	def mousePressEvent(self, e):
		self.bboxEditor.mousePressEvent(e)

	def mouseReleaseEvent(self, e):
		self.bboxEditor.mouseReleaseEvent(e)

	def wheelEvent(self, e):
		self.bboxEditor.wheelEvent(e)

	def getImageRect(self):
		print('ImageWidget::getImageRect()')
		ratio_img = self.img.width() / self.img.height()
		ratio_w   = self    .width() / self    .height()
		print('  ratio_img:', ratio_img)
		if ratio_w > ratio_img:
			h = self.height()
			w = h * ratio_img
		else:
			w = self.width()
			h = w / ratio_img

		return QRect(
			self.rect().center().x() - w/2,
			self.rect().center().y() - h/2,
			w,
			h)


