from PyQt5.QtWidgets import QWidget
from form_image_bbox_editor_ui import Ui_FormImageBboxEditor

class FormImageBboxEditor(QWidget):
	def __init__(self):
		print('FormImageBboxEditor::__init__()')
		super().__init__()
		self.ui = Ui_FormImageBboxEditor()
		self.ui.setupUi(self)
		self.ui.buttonDone             .clicked.connect(self.slot_on_buttonDone_clicked)
		self.ui.buttonSwitchInOutEditor.clicked.connect(self.slot_on_buttonSwitchInOutEditor_clicked)
		self.ui.buttonSwapInOutEditor  .clicked.connect(self.slot_on_buttonSwapInOutEditor_clicked)
		self.ui.buttonImageNext        .clicked.connect(self.slot_on_buttonImageNext_clicked)
		self.ui.buttonImagePrev        .clicked.connect(self.slot_on_buttonImagePrev_clicked)
		self.ui.checkboxStayInside     .toggled.connect(self.slot_on_checkboxStayInside_toggled)
		self.ui.buttonSwitchInOutEditor.setShortcut(QKeySequence('Tab'))
		self.ui.buttonSwapInOutEditor  .setShortcut(QKeySequence('w'))
		self.ui.buttonImageNext        .setShortcut(QKeySequence('Space'))
		self.ui.buttonImagePrev        .setShortcut(QKeySequence('Backspace'))
		self.ui.checkboxStayInside     .setShortcut(QKeySequence('s'))
		self.ui.image.setTargetRatio(1920 / 1080) # Aspect ratio of the video slideshow
		self.ui.image.bboxesChanged.connect(self.bboxesChanged)
