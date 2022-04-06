import sys
from PyQt5.QtCore import QRectF, QPointF, QSettings
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtGui import QKeySequence
from main_window_ui import Ui_MainWindow
import traceback
import json
import re
import os
from kdenlive_file import KdenliveFile

class AppWindow(QMainWindow):
	def __init__(self):
		print('AppWindow::__init__()')
		super().__init__()
		self.settings = QSettings('./settings.ini', QSettings.IniFormat)
		self.defaultBboxesLandscape = [QRectF(0, 0.1, 1, 0.8), QRectF(0.1, 0.1, 0.9, 0.8)]
		self.defaultBboxesPortrait  = [QRectF(0, 0, 1, 0), QRectF(0.05, 0.05, 0.9, 0)]

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.buttonDone             .clicked.connect(self.slot_on_buttonDone_clicked)
		self.ui.buttonSwitchInOutEditor.clicked.connect(self.slot_on_buttonSwitchInOutEditor_clicked)
		self.ui.buttonSwapInOutEditor  .clicked.connect(self.slot_on_buttonSwapInOutEditor_clicked)
		self.ui.buttonImageNext        .clicked.connect(self.slot_on_buttonImageNext_clicked)
		self.ui.buttonImagePrev        .clicked.connect(self.slot_on_buttonImagePrev_clicked)
		self.ui.buttonLoadKdenlive     .clicked.connect(self.slot_on_buttonLoadKdenlive_clicked)
		self.ui.buttonLoadImages       .clicked.connect(self.slot_on_buttonLoadImages_clicked)
		self.ui.buttonSaveKdenlive     .clicked.connect(self.slot_on_buttonSaveKdenlive_clicked)
		self.ui.buttonSaveBboxesJson   .clicked.connect(self.slot_on_buttonSaveBboxesJson_clicked)
		self.ui.buttonApplyBboxRatioMultiplier.clicked.connect(self.slot_on_buttonApplyBboxRatioMultiplier_clicked)
		self.ui.lineeditTargetVideoResolution.textChanged.connect(self.slot_on_lineeditTargetVideoResolution_textChanged)
		self.ui.checkboxStayInside     .toggled.connect(self.slot_on_checkboxStayInside_toggled)
		self.ui.buttonLoadKdenlive     .setShortcut(QKeySequence('Ctrl+o'))
		self.ui.buttonSwitchInOutEditor.setShortcut(QKeySequence('Tab'))
		self.ui.buttonSwapInOutEditor  .setShortcut(QKeySequence('w'))
		self.ui.buttonImageNext        .setShortcut(QKeySequence('Space'))
		self.ui.buttonImagePrev        .setShortcut(QKeySequence('Backspace'))
		self.ui.checkboxStayInside     .setShortcut(QKeySequence('s'))
		self.ui.buttonSaveKdenlive.setEnabled(False)
		self.ui.buttonImageNext   .setEnabled(False)
		self.ui.buttonImagePrev   .setEnabled(False)
		self.ui.lineeditTargetVideoResolution.setText('1920x1080')
#		self.ui.image.setTargetRatio(1920 / 1080) # Aspect ratio of the video slideshow
		self.ui.image.bboxesChanged.connect(self.bboxesChanged)
		self.fileFormats = [
			'All supported formats: *.kdenlive, *.json (*.kdenlive *.json)',
			'Kdenlive Project Files: *.kdenlive (*.kdenlive)',
			'Bboxes Json: *.json (*.json)',
		]
		self.kdenliveFile = None
		self.images = []
		self.imagesData = {}
		self.imageIdx = 0
		if len(sys.argv) > 1:
			if re.match('.*\.kdenlive', sys.argv[1]):
				self.LoadKdenliveFile(sys.argv[1])
			else:
				self.images = sys.argv[1:]
				print('images:', self.images)

			# Load bboxes from json
			try:
				self.LoadBboxesJson(self.getBboxesFilename())
			except:
				print('WARNING: unable to parse json data')
				traceback.print_exc()

			# Override json bboxes with kdenlive clip transformations
			if self.kdenliveFile is not None:
				self.KdenliveFileToImagesData()

			img_path = self.images[self.imageIdx]
			print('imagesData:', self.imagesData)
			self.SetImageIdx(self.imageIdx)

		self.show()

	def setShortcut(button, shortcutStr):
		button.setShortcut(QKeySequence(shortcutStr))
		button.setText(button.text() + ' ['+shortcutStr+']')

	def closeEvent(self, e):
		print('closeEvent()')
		#self.save()

	def bboxesChanged(self):
		self.updateInfo()

	def updateInfo(self):
		if len(self.images) == 0:
			return
		bboxes = self.ui.image.getBboxes01()
		#print('images:', self.images)
		#print('bboxes:', bboxes)
		self.ui.labelInfoPath .setText(self.images[self.imageIdx])
		self.ui.labelInfoScale.setText('in -> out scale: %02f' % (bboxes[1].width() / bboxes[0].width() if bboxes[0].width() > 0 else -1))

	def getTargetRatio(self):
		a = self.ui.lineeditTargetVideoResolution.text().split('x')
		w = int(a[0])
		h = int(a[1])
		return w / h # Aspect ratio of the video slideshow

	def slot_on_lineeditTargetVideoResolution_textChanged(self, text):
		self.ui.image.setTargetRatio(self.getTargetRatio()) # Aspect ratio of the video slideshow

	def slot_on_checkboxStayInside_toggled(self, checked):
		print('toggled()', checked)
#		print('CHECK 611 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])
		self.ui.image.setStayInside(checked)
#		print('CHECK 612 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])
		img_path = self.images[self.imageIdx]
#		print('CHECK 613 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])
		self.imagesData[img_path]['stay_inside_image'] = checked
#		print('CHECK 614 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])

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
			if img_path not in self.images:
				self.images.append(img_path)
		print('imagesData:', self.imagesData)

	def slot_on_buttonDone_clicked(self):
		print('clicked')
		self.close()

	def slot_on_buttonSwitchInOutEditor_clicked(self):
		print('switch editor')
		#traceback.print_stack(file = sys.stdout)
		self.ui.image.switchEditor()

	def slot_on_buttonSwapInOutEditor_clicked(self):
		print('swap editor')
		self.ui.image.swapEditors()

	def areBboxesInsideImage(self, bboxes):
		inside = True
		for bbox in bboxes:
			if bbox.left() < 0 or bbox.top() < 0 or bbox.right() > 1 or bbox.bottom() > 1:
				inside = False
			print('areBboxesInsideImage() bbox:', bbox, 'inside:', inside)
		print('areBboxesInsideImage() return ', inside)
		return inside

	def SetImageIdx(self, idx):
		print('SetImageIdx() ', self.imageIdx, '->', idx)
#		print('CHECK 1 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])

		#print('SetImageIdx() imagesData:', self.imagesData)
		self.SaveCurrentImageData()
#		print('CHECK 2 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])

		# Temporarily don't restrict bboxes
		self.ui.checkboxStayInside.setChecked(False)

#		print('CHECK 3 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])
		self.imageIdx = max(0, min(len(self.images)-1, idx))
		print('SetImageIdx() imageIdx:', self.imageIdx)
		img_path = self.images[self.imageIdx]
		print('SetImageIdx() img_path:', img_path)
		self.ui.image.openImage(img_path)
#		print('CHECK 4 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])
		bboxes = []
		if img_path in self.imagesData:
			print('SetImageIdx() img_path:', img_path, 'bboxes:', self.imagesData[img_path])
			#self.ui.checkboxStayInside.setChecked(self.imagesData[img_path]['stay_inside_image'])
			bboxes = []
			if 'bboxes' in self.imagesData[img_path]:
				bboxes = self.imagesData[img_path]['bboxes']
#		print('CHECK 5 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])
		print('SetImageIdx() bboxes 1:', bboxes)

		if len(bboxes) != 2:
			print('SetImageIdx() no bboxes found -> creating default bboxes')
			bboxes = []
			img_size = self.ui.image.getImageSize()

			if img_size.width() > img_size.height():
				for bbox in self.defaultBboxesLandscape:
					bboxes.append(QRectF(bbox))
				print('SetImageIdx() bboxes 2:', bboxes)
			else:
				ratio_img = img_size.height() / img_size.width()
				ratio_target = self.getTargetRatio()
				print('SetImageIdx() ratio_img:', ratio_img)
				for bbox in self.defaultBboxesPortrait:
					bbox_copy = QRectF(bbox)
					bbox_copy.setWidth(bbox_copy.width() * ratio_img * ratio_target)
					bbox_copy.setHeight(bbox_copy.width() / ratio_img / ratio_target)
					print('SetImageIdx() bbox_copy: ', bbox_copy)
					bbox_copy.moveCenter(QPointF(0.5, 0.5))
					print('SetImageIdx() bbox_copy: ', bbox_copy)
					bboxes.append(bbox_copy)
				print('SetImageIdx() bboxes 3:', bboxes)
#		print('CHECK 6 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])

		if len(bboxes) == 2:
			print('SetImageIdx() bboxes:', bboxes)
			self.ui.image.setBboxes01(bboxes)
#			print('CHECK 61 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])
			stay_inside = self.areBboxesInsideImage(bboxes)
			print('SetImageIdx() stay_inside:', stay_inside)
#			print('CHECK 62 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])
			self.ui.checkboxStayInside.setChecked(stay_inside)
#			print('CHECK 63 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])
#		print('CHECK 7 3567_IMG.jpg bboxes: ',self.imagesData['clips/3567_IMG.jpg']['bboxes'])

		self.ui.buttonImagePrev.setEnabled(self.imageIdx > 0)
		self.ui.buttonImageNext.setEnabled(self.imageIdx + 1 < len(self.images))
		self.updateInfo()

	def slot_on_buttonImageNext_clicked(self):
		print('on_buttonImageNext_clicked()')
		self.SetImageIdx(self.imageIdx + 1)

	def slot_on_buttonImagePrev_clicked(self):
		print('on_buttonImagePrev_clicked()')
		self.SetImageIdx(self.imageIdx - 1)

	def LoadKdenliveFile(self, filename):
		print('LoadKdenliveFile()')
		self.kdenliveFile = KdenliveFile()
		self.kdenliveFile.Load(filename)
		self.ui.buttonSaveKdenlive.setEnabled(True)

	def KdenliveFileToImagesData(self):
		images_data = self.kdenliveFile.GetImagesData()
		images_data = dict(filter(lambda elem: re.match('.*\.jpg', elem[0]), images_data.items()))
		for img_path in images_data:
			if img_path not in self.images:
				self.images.append(img_path)
		for img_path in images_data:
			print('img_path:', img_path)
			if 'bboxes' in images_data[img_path] and len(images_data[img_path]['bboxes']) > 0:
				if img_path in self.imagesData:
					print('overriding json bboxes:', self.imagesData[img_path], ' with clip transform bboxes:', images_data[img_path])
				self.imagesData[img_path] = images_data[img_path]
		self.imagesData = {**self.imagesData, **images_data}

	def LoadBboxesJson(self, filename):
		with open(filename, 'r') as f:
			json_str = f.read()
			print('json_str:', json_str)
			self.fromJson(json_str)

	def slot_on_buttonLoadKdenlive_clicked(self):
		print('slot_on_buttonLoadKdenlive_clicked()')
		#filename, filt = QFileDialog.getOpenFileName(self, "Load .kdenlive", "", "Kdenlive Project Files (*.kdenlive)")
		filename, filt = QFileDialog.getOpenFileName(self, "Load .kdenlive", self.settings.value('filedialog_path', ''), ';;'.join(self.fileFormats), self.fileFormats[0])
		if filename is None or filename == '':
			return
		self.settings.setValue('filedialog_path', os.path.dirname(filename))
		ext = os.path.splitext(filename)[1].lower()
		print('filename:', filename)
		print('filt:', filt)
		print('ext:', ext)
		if ext == '.kdenlive':
			self.LoadKdenliveFile(filename)
			self.KdenliveFileToImagesData()
		elif ext == '.json':
			self.LoadBboxesJson(filename)
		self.SetImageIdx(0)

	def LoadImages(self, filenames):
		self.images = filenames
		self.SetImageIdx(0)

	def slot_on_buttonLoadImages_clicked(self):
		print('slot_on_buttonLoadImages_clicked()')
		filenames, filt = QFileDialog.getOpenFileNames(self, "Load images", self.settings.value('filedialog_path', ''), "Image Files (*.jpg, *.png, *.tiff)")
		if filenames is None or filenames == '':
			return
		self.settings.setValue('filedialog_path', os.path.dirname(filenames))
		print('filenames:', filenames)
		self.LoadImages(filenames)

	def SaveKdenlive(self, filename):
		self.SaveCurrentImageData()
		if self.kdenliveFile is None:
			return
		#self.setBboxesRatioMultiplier(0.5)
		self.kdenliveFile.GroupClipsWithSameBoundaries()
		#self.kdenliveFile.AddBeats('Radioactive- Gatsby Souns live.mp3', '/media/miso/data/mp3/Dali Hornak/Radioactive- Gatsby Souns live.mp3.downbeats')
		self.kdenliveFile.AddBeatsForAllMusicClips()
		self.kdenliveFile.AddBeatGuides()
		self.kdenliveFile.SynchronizeToBeats()
		# Note: SetImagesData() has to be applied after SynchronizeToBeats() which modifies duration of clips
		self.kdenliveFile.SetImagesData(self.imagesData)
		self.kdenliveFile.Save(filename)
		self.kdenliveFile.DumpClipsLength()
		print('filename:', filename)

		# Check saved file:
		#f_saved = KdenliveFile()
		#f_saved.Load(filename)
		#print('f_saved:')
		#f_saved.DumpClipsLength()

	def slot_on_buttonSaveKdenlive_clicked(self):
		print('slot_on_buttonSaveKdenlive_clicked()')
		filename, filt = QFileDialog.getSaveFileName(self, "Save .kdenlive", self.settings.value('filedialog_path', ''), "Kdenlive Project Files (*.kdenlive)")
		if filename is None or filename == '':
			return
		self.settings.setValue('filedialog_path', os.path.dirname(filename))
		print('filename:', filename)
		self.SaveKdenlive(filename)

	def SaveBboxesJson(self, filename):
		self.SaveCurrentImageData()
		json_str = self.toJson()
		print('json_str:', json_str)
		with open(filename, "w") as text_file:
			text_file.write(json_str)

	def slot_on_buttonSaveBboxesJson_clicked(self):
		print('slot_on_buttonSaveBboxesJson_clicked()')
		filename, filt = QFileDialog.getSaveFileName(self, "Save bboxes .json", self.settings.value('filedialog_path', ''), "Bboxes json (*.json)")
		if filename is None or filename == '':
			return
		self.settings.setValue('filedialog_path', os.path.dirname(filename))
		print('filename:', filename)
		self.SaveBboxesJson(filename)


	def SaveCurrentImageData(self):
		bboxes = self.ui.image.getBboxes01()
		for bbox in bboxes:
			if bbox.isEmpty():
				return
		img_path = self.images[self.imageIdx]
		if not img_path in self.imagesData:
			self.imagesData[img_path] = {}
		self.imagesData[img_path]['bboxes'] = bboxes
		print('SaveCurrentImageData() img_path:', img_path, 'bboxes:', bboxes)

	def getBboxesFilename(self):
		if self.kdenliveFile is None:
			return 'image_bboxes.json'
		else:
			return re.sub(r'\.kdenlive', '_bboxes.json', self.kdenliveFile.inputFilename)

	def setBboxesRatioMultiplier(self, ratioMultiplier):
		print('setBboxesRatioMultiplier() len:', len(self.imagesData))
		for img_path in self.imagesData:
			print('setBboxesRatioMultiplier() img_path:', img_path)
			if 'bboxes' not in self.imagesData[img_path]:
				continue
			bboxes = self.imagesData[img_path]['bboxes']
			if len(bboxes) != 2:
				continue
			bbox_small = bboxes[0]
			bbox_large = bboxes[1]
			if bbox_small.width() > bbox_large.width():
				# swap
				bbox_small, bbox_large = bbox_large, bbox_small

			print('setBboxesRatioMultiplier() bbox_small:', bbox_small)
			print('setBboxesRatioMultiplier() bbox_large:', bbox_large)
			diff_l = bbox_small.left  () - bbox_large.left  ()
			diff_r = bbox_small.right () - bbox_large.right ()
			diff_t = bbox_small.top   () - bbox_large.top   ()
			diff_b = bbox_small.bottom() - bbox_large.bottom()
			bbox_small.setLeft  (bbox_large.left  () + diff_l*ratioMultiplier)
			bbox_small.setTop   (bbox_large.top   () + diff_t*ratioMultiplier)
			bbox_small.setRight (bbox_large.right () + diff_r*ratioMultiplier)
			bbox_small.setBottom(bbox_large.bottom() + diff_b*ratioMultiplier)
			print('setBboxesRatioMultiplier() bbox_small adjusted:', bbox_small)
			print('setBboxesRatioMultiplier() bboxes:', bboxes)
		# Update view
		self.SetImageIdx(self.imageIdx)

	def slot_on_buttonApplyBboxRatioMultiplier_clicked(self):
		print('slot_on_buttonApplyBboxRatioMultiplier_clicked()')
		mul = self.ui.spinboxBboxRatioMultiplier.value()
		print('slot_on_buttonApplyBboxRatioMultiplier_clicked() mul:', mul)
		self.setBboxesRatioMultiplier(mul)

# if len(sys.argv) == 1:
# 	print('Usage: ' + sys.argv[0] + ' photo0.jpg photo1.jpg photo2.jpg ...')
# 	print('Output is generated to image_bboxes.json')
# else:
app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())
