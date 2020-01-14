import sys
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QKeySequence
from main_window import Ui_MainWindow
import traceback
import json
import re
import opentimelineio as otio
import time
from kdenlive_file import KdenliveFile

class AppWindow(QMainWindow):
	def __init__(self):
		print('AppWindow::__init__()')
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.buttonDone             .clicked.connect(self.slot_on_buttonDone_clicked)
		self.ui.buttonSwitchInOutEditor.clicked.connect(self.slot_on_buttonSwitchInOutEditor_clicked)
		self.ui.buttonImageNext        .clicked.connect(self.slot_on_buttonImageNext_clicked)
		self.ui.buttonImagePrev        .clicked.connect(self.slot_on_buttonImagePrev_clicked)
		self.ui.checkboxStayInside     .toggled.connect(self.slot_on_checkboxStayInside_toggled)
		self.ui.buttonSwitchInOutEditor.setShortcut(QKeySequence('Tab'))
		self.ui.buttonImageNext        .setShortcut(QKeySequence('Space'))
		self.ui.buttonImagePrev        .setShortcut(QKeySequence('Backspace'))
		self.ui.checkboxStayInside     .setShortcut(QKeySequence('s'))
		self.ui.image.setTargetRatio(1920 / 1080) # Aspect ratio of the video slideshow
		self.ui.image.bboxesChanged.connect(self.bboxesChanged)
		self.kdenliveFile = None
		self.images = []
		self.imagesData = {}
		if re.match('.*\.kdenlive', sys.argv[1]):
			print('open kdenlive file')
			self.kdenliveFile = KdenliveFile()
			self.kdenliveFile.Load(sys.argv[1])
			self.imagesData = self.kdenliveFile.GetImagesData()
			self.imagesData = dict(filter(lambda elem: re.match('.*\.jpg', elem[0]), self.imagesData.items()))
			for img_path in self.imagesData:
				self.images.append(img_path)
		else:
			self.images = sys.argv[1:]
			print('images:', self.images)
			try:
				with open('image_bboxes.json', 'r') as f:
					json_str = f.read()
					print('json_str:', json_str)
					self.fromJson(json_str)
			except:
				print('WARNING: unable to parse json data')
				traceback.print_exc()
		self.imageIdx = 0
		img_path = self.images[self.imageIdx]
		print('imagesData:', self.imagesData)
		self.setImageIdx(self.imageIdx)
		self.show()

	def closeEvent(self, e):
		self.save()

	def bboxesChanged(self):
		self.updateInfo()

	def updateInfo(self):
		bboxes = self.ui.image.getBboxes01()
		self.ui.labelInfoPath .setText(self.images[self.imageIdx])
		self.ui.labelInfoScale.setText('in -> out scale: %02f' % (bboxes[1].width() / bboxes[0].width() if bboxes[0].width() > 0 else -1))

	def slot_on_checkboxStayInside_toggled(self, checked):
		print('toggled()', checked)
		self.ui.image.setStayInside(checked)
		img_path = self.images[self.imageIdx]
		self.imagesData[img_path]['stay_inside_image'] = checked

	def toJson(self):
		out = {}
		for img_path in self.imagesData:
			print('img_path:', img_path)
			out[img_path] = {}
			out[img_path]['stay_inside_image'] = self.imagesData[img_path]['stay_inside_image'] if 'stay_inside_image' in self.imagesData[img_path] else True
			out[img_path]['bboxes'] = []
			for bbox in self.imagesData[img_path]['bboxes']:
				out[img_path]['bboxes'].append({
					'x': bbox.x(),
					'y': bbox.y(),
					'w': bbox.width(),
					'h': bbox.height()})
		return json.dumps(out, indent=4)

	def fromJson(self, jsonStr):
		self.imagesData = {}
		jsonObj = json.loads(jsonStr)
		print('jsonObj:', jsonObj)
		for img_path in jsonObj:
			print('img_path:', img_path)
			bboxes = []
			for bbox in jsonObj[img_path]['bboxes']:
				print('bbox:', bbox)
				bboxes.append(QRectF(bbox['x'], bbox['y'], bbox['w'], bbox['h']))
			self.imagesData[img_path] = {'stay_inside_image': jsonObj[img_path]['stay_inside_image'], 'bboxes': bboxes}
		print('imagesData:', self.imagesData)

	def slot_on_buttonDone_clicked(self):
		print('clicked')
		self.close()

	def slot_on_buttonSwitchInOutEditor_clicked(self):
		print('switch editor')
		traceback.print_stack(file = sys.stdout)
		self.ui.image.switchEditor()

	def setImageIdx(self, idx):
		print('setImageIdx() ', self.imageIdx, '->', idx)
		print('imagesData:', self.imagesData)
		self.saveCurrentImageData()
		self.imageIdx = max(0, min(len(self.images)-1, idx))
		img_path = self.images[self.imageIdx]
		self.ui.image.openImage(img_path)
		if img_path in self.imagesData:
			print('img_path:', img_path, 'bboxes:', self.imagesData[img_path])
			self.ui.checkboxStayInside.setChecked(self.imagesData[img_path]['stay_inside_image'])
			self.ui.image.setBboxes01(self.imagesData[img_path]['bboxes'])
		self.updateInfo()

	def slot_on_buttonImageNext_clicked(self):
		print('on_buttonImageNext_clicked()')
		self.setImageIdx(self.imageIdx + 1)

	def slot_on_buttonImagePrev_clicked(self):
		print('on_buttonImagePrev_clicked()')
		self.setImageIdx(self.imageIdx - 1)

	def saveCurrentImageData(self):
		bboxes = self.ui.image.getBboxes01()
		for bbox in bboxes:
			if bbox.isEmpty():
				return
		img_path = self.images[self.imageIdx]
		if not img_path in self.imagesData:
			self.imagesData[img_path] = {}
		self.imagesData[img_path]['bboxes'] = bboxes
		print('saveCurrentImageData() bboxes:', bboxes)

	def save(self):
		self.saveCurrentImageData()
		json_str = self.toJson()

		print('json_str:', json_str)
		with open("image_bboxes.json", "w") as text_file:
			text_file.write(json_str)

		if self.kdenliveFile is not None:
			self.kdenliveFile.SetImagesData(self.imagesData)
			self.kdenliveFile.AddBeats('Radioactive- Gatsby Souns live.mp3', '/media/miso/data/mp3/Dali Hornak/Radioactive- Gatsby Souns live.mp3.downbeats')
			self.kdenliveFile.AddBeatGuides()
			self.kdenliveFile.SynchronizeToBeats()
			output_filename = re.sub(r'\.kdenlive', '_out.kdenlive', self.kdenliveFile.inputFilename)
			self.kdenliveFile.Save(output_filename)
			print('inputFilename:', )

		print('save() done')

if len(sys.argv) == 1:
	print('Usage: ' + sys.argv[0] + ' photo0.jpg photo1.jpg photo2.jpg ...')
	print('Output is generated to image_bboxes.json')
else:
	app = QApplication(sys.argv)
	w = AppWindow()
	w.show()
	sys.exit(app.exec_())

