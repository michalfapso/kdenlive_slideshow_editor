import sys
from PyQt5.QtCore import QObject, QRect, QRectF, QPoint, QPointF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QWidget
import datetime

class BboxEditor(QObject):
	changed = pyqtSignal()

	def __init__(self, parent=None):
		super().__init__(parent)
		self.bbox01 = QRectF()
		self.bboxDrawing = QRect()
		self.color = QColor()
		self.isActive = False
		self.posPress = QPoint()
		self.bbox01Press = QRect()
		self.isDragging = False
		self.prevWheelEventTimestamp = datetime.datetime.now()
		self.scalingMultiplier = 1

	def bbox01KeepInsideDrawingArea(self):
		if self.bbox01.width() > 1:
			self.bbox01.setWidth(1)
		if self.bbox01.height() > 1:
			self.bbox01.setHeight(1)
		if self.bbox01.x() < 0:
			self.bbox01.translate(-self.bbox01.x(), 0)
		if self.bbox01.y() < 0:
			self.bbox01.translate(0, -self.bbox01.y())
		if self.bbox01.x() + self.bbox01.width() > 1:
			self.bbox01.translate(1 - (self.bbox01.x() + self.bbox01.width()), 0)
		if self.bbox01.y() + self.bbox01.height() > 1:
			self.bbox01.translate(0, 1 - (self.bbox01.y() + self.bbox01.height()))

	def bbox01ToPixels(self):
		return QRect(
			self.bboxDrawing.x() + self.bbox01.x()*self.bboxDrawing.width (),
			self.bboxDrawing.y() + self.bbox01.y()*self.bboxDrawing.height(),
			self.bbox01.width ()*self.bboxDrawing.width (),
			self.bbox01.height()*self.bboxDrawing.height())

	def paint(self, qpainter):
		print('paint() bboxDrawing:', self.bboxDrawing, ' bbox01:', self.bbox01)
		r = self.bbox01ToPixels()

		# Main rect
		pen = QPen(QColor(255, 0, 0))
		pen.setWidth(3)
		qpainter.setPen(pen)
		#qpainter.setPen(QColor(0,0,0))
		qpainter.drawRect(r)
		# Outer rect
		#qpainter.setPen(QColor(255,255,255))
		#qpainter.drawRect(r.adjusted(-1, -1, 1, 1))
		# Inner rect
		#qpainter.setPen(QColor(255,255,255))
		#qpainter.drawRect(r.adjusted(1, 1, -1, -1))

	def setColor(self, color):
		self.color = color

	def setDrawingArea(self, qrect):
		self.bboxDrawing = qrect

	def setBbox01(self, qrect):
		self.bbox01 = qrect

	def getBbox01(self):
		return self.bbox01

	def setActive(self, active):
		self.isActive = active

	def mouseMoveEvent(self, e):
		if not self.isActive:
			return
		if self.isDragging:
			diff = e.pos() - self.posPress
			diff01 = QPointF(
				diff.x() / self.bboxDrawing.width (),
				diff.y() / self.bboxDrawing.height())
			print('mouseMoveEvent() bbox01:', self.bbox01, 'diff:', diff, 'diff01:', diff01)
			self.bbox01 = self.bbox01Press.translated(diff01)
			self.bbox01KeepInsideDrawingArea()
			self.changed.emit()

	def mousePressEvent(self, e):
		if not self.isActive:
			return
		bb = self.bbox01ToPixels()
		if (e.pos().x() >= bb.topLeft().x()) and \
			(e.pos().y() >= bb.topLeft().y()) and \
			e.pos().x() <= bb.bottomRight().x() and \
			e.pos().y() <= bb.bottomRight().y() \
			:
			self.isDragging = True
			self.posPress = e.pos()
			self.bbox01Press = self.bbox01

	def mouseReleaseEvent(self, e):
		if not self.isActive:
			return
		self.isDragging = False

	def wheelEvent(self, e):
		if not self.isActive:
			return
		t_diff = (datetime.datetime.now() - self.prevWheelEventTimestamp).total_seconds()
		if t_diff < 0.1:
			self.scalingMultiplier *= 1.5
		else:
			self.scalingMultiplier = 1
		print('wheelEvent() t:', self.prevWheelEventTimestamp, '->', datetime.datetime.now(), 't_diff:', t_diff, 'angleDelta:', e.angleDelta(), 'scalingMultiplier:', self.scalingMultiplier)
		#sign = -1 if e.angleDelta().y() < 0 else 1
		#scale = 1 + 0.1*sign
		scale = 0.01
		scale *= self.scalingMultiplier
		scale += 1
		if e.angleDelta().y() < 0:
			scale = 1 / scale
		diff_x = (self.bbox01.width () * (1 - scale)) / 2
		diff_y = (self.bbox01.height() * (1 - scale)) / 2
		print('wheelEvent() scale:', scale, 'diff:', diff_x, diff_y)
		self.bbox01.adjust(diff_x, diff_y, -diff_x, -diff_y)
		self.bbox01KeepInsideDrawingArea()
		self.prevWheelEventTimestamp = datetime.datetime.now()
		self.changed.emit()

