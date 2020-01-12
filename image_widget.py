import sys
from PyQt5.QtCore import QRect, QRectF, pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPainter, QColor
from bbox_editor import BboxEditor

class ImageWidget(QWidget):
	bboxesChanged = pyqtSignal()

	def __init__(self, parent=None):
		print('ImageWidget()')
		super().__init__(parent)
		self.defaultBboxes = [QRectF(0, 0.1, 1, 0.8), QRectF(0.2, 0.1, 0.8, 0.8)]
		self.bboxEditors = [BboxEditor(self), BboxEditor(self)]
		self.bboxEditors[0].setColor(QColor(0, 255, 0))
		self.bboxEditors[1].setColor(QColor(255, 0, 0))
		for ed in self.bboxEditors: ed.changed.connect(self.editorChanged)
		self.activeEditorIdx = 0
		self.bboxEditors[self.activeEditorIdx].setActive(True)
		self.img = QImage()

	def editorChanged(self):
		self.update()
		self.bboxesChanged.emit()

	def getBboxes01(self):
		bboxes = []
		for ed in self.bboxEditors: bboxes.append(ed.getBbox01())
		return bboxes

	def setBboxes01(self, bboxes):
		print('setBboxes01() bboxes:', bboxes)
		for i in range(0, len(self.bboxEditors)):
			if i < len(bboxes):
				self.bboxEditors[i].setBbox01(bboxes[i])
		self.update()

	def setTargetRatio(self, ratio):
		print('setTargetRatio() ratio:', ratio)
		for ed in self.bboxEditors: ed.setTargetRatio(ratio)

	def setStayInside(self, stay):
		for ed in self.bboxEditors: ed.setStayInside(stay)

	def openImage(self, path):
		print('openImage() path:', path)
		self.img.load(path)
		for i, ed in enumerate(self.bboxEditors):
			ed.setDrawingArea(self.getImageRect())
			ed.setBbox01(self.defaultBboxes[i])
		self.update()

	def paintEvent(self, e):
		print('ImageWidget::paintEvent()', e)
		qpainter = QPainter(self)
		#qpainter.drawImage(QRect(0, 0, self.width(), self.height()), self.img)
		qpainter.drawImage(self.getImageRect(), self.img)
		for ed in self.bboxEditors: ed.paint(qpainter)

	def resizeEvent(self, e):
		for ed in self.bboxEditors: ed.setDrawingArea(self.getImageRect())
		print('ImageWidget::resizeEvent()', e)

	def mouseMoveEvent(self, e):
		for ed in self.bboxEditors: ed.mouseMoveEvent(e)

	def mousePressEvent(self, e):
		for ed in self.bboxEditors: ed.mousePressEvent(e)

	def mouseReleaseEvent(self, e):
		for ed in self.bboxEditors: ed.mouseReleaseEvent(e)

	def wheelEvent(self, e):
		for ed in self.bboxEditors: ed.wheelEvent(e)

	def setActiveEditor(self, idx):
		for ed in self.bboxEditors: ed.setActive(False)
		self.activeEditorIdx = idx
		self.bboxEditors[self.activeEditorIdx].setActive(True)

	def switchEditor(self):
		self.activeEditorIdx += 1
		if self.activeEditorIdx > 1:
			self.activeEditorIdx = 0
		print('switchEditor() activeEditorIdx:', self.activeEditorIdx)
		self.setActiveEditor(self.activeEditorIdx)
		self.update()

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


