from PyQt5.QtCore import QObject, QRect, QRectF, QPoint, QPointF, pyqtSignal
from PyQt5.QtGui import QColor, QPen
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
		self.targetRatio = 1
		self.stayInside = True

	def setTargetRatio(self, ratio):
		self.targetRatio = ratio
		self.setBbox01(self.bbox01)

	def setStayInside(self, stay):
		self.stayInside = stay
		self.setBbox01(self.bbox01)

	def bbox01KeepInsideDrawingArea(self):
		# r = w0*w / h0*h
		# h0*h = w0*w / r
		# h0 = w0*w / r / h
		w = self.bbox01.width () * self.bboxDrawing.width ()
		h = self.bbox01.height() * self.bboxDrawing.height()
		print('bbox01KeepInsideDrawingArea() bboxDrawing:', self.bboxDrawing, 'w:', w, 'h:', h)
		if h == 0:
			return
		if w/h != self.targetRatio:
			print('bbox01KeepInsideDrawingArea() bbox01 a:', self.bbox01, 'targetRatio:', self.targetRatio)
			self.bbox01.setHeight(w / self.targetRatio / self.bboxDrawing.height())
			print('bbox01KeepInsideDrawingArea() bbox01 b:', self.bbox01)
		if self.stayInside:
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
		print('bbox01KeepInsideDrawingArea() bbox01 c:', self.bbox01, 'toPixels:', self.bbox01ToPixels())

	def bbox01ToPixels(self):
		r = QRect(
			int(self.bboxDrawing.x() + self.bbox01.x()*self.bboxDrawing.width ()),
			int(self.bboxDrawing.y() + self.bbox01.y()*self.bboxDrawing.height()),
			int(self.bbox01.width ()*self.bboxDrawing.width ()),
			int(self.bbox01.width ()*self.bboxDrawing.width () / self.targetRatio))
			#self.bbox01.height()*self.bboxDrawing.height())
		print('bbox01ToPixels() r:', r.width(), r.height(), 'bboxDrawing:', self.bboxDrawing, 'bbox01:', self.bbox01)
		return r

	def paint(self, qpainter):
		r = self.bbox01ToPixels()
		print('paint() bboxDrawing:', self.bboxDrawing, ' bbox01:', self.bbox01, 'r:', r)

		c = self.color
		w = 3 if self.isActive else 1
		#c.setAlpha(255 if self.isActive else 127)

		# Outer white rect
		pen = QPen(QColor(255,255,255))
		pen.setWidth(w + 2)
		qpainter.setPen(pen)
		qpainter.drawRect(r)

		# Main colored rect
		pen = QPen(c)
		pen.setWidth(w)
		qpainter.setPen(pen)
		qpainter.drawRect(r)

	def setColor(self, color):
		self.color = color
		self.changed.emit()

	def setDrawingArea(self, qrect):
		self.bboxDrawing = qrect
		self.changed.emit()

	def setBbox01(self, qrect):
		self.bbox01 = qrect
		self.bbox01KeepInsideDrawingArea()
		self.changed.emit()

	def getBbox01(self):
		return self.bbox01

	def setActive(self, active):
		self.isActive = active
		self.changed.emit()

	def mouseMoveEvent(self, e):
		if not self.isActive:
			return
		if self.isDragging:
			diff = e.pos() - self.posPress
			diff01 = QPointF(
				diff.x() / self.bboxDrawing.width (),
				diff.y() / self.bboxDrawing.height())
			print('mouseMoveEvent() bbox01:', self.bbox01, 'diff:', diff, 'diff01:', diff01)
			self.setBbox01(self.bbox01Press.translated(diff01))

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
		if e.angleDelta().y() > 0:
			scale = 1 / scale
		diff_x = (self.bbox01.width () * (1 - scale)) / 2
		diff_y = (self.bbox01.height() * (1 - scale)) / 2
		print('wheelEvent() scale:', scale, 'diff:', diff_x, diff_y)
		self.setBbox01(self.bbox01.adjusted(diff_x, diff_y, -diff_x, -diff_y))
		self.prevWheelEventTimestamp = datetime.datetime.now()

	def getBbox01(self):
		return self.bbox01
