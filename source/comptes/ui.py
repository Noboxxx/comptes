import json
import os
import csv
import re
import traceback
from pathlib import Path

from PySide6.QtCharts import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from .core import *

__folder__ = os.path.dirname(__file__)


ICON_FOLDER = os.path.join(__folder__, 'icon')

CATEGORIES_ICON_FOLDER = os.path.join(ICON_FOLDER, 'categories')

"""
class YoutubeDownloaderWid(QWidget):
	
	SETTINGS_FILE = os.path.join(YOUTUBE_DOWNLOADER_APP_DATA, 'settings.json')

	DEFAULT_URL = 'https://www.youtube.com/watch?v=4aDkKJfZl7w'
	DEFAULT_URL_MESSAGE = 'Aucune vidéo trouvée...'

	DEFAULT_SETTINGS = {
		'destination': str(Path.home().joinpath('downloads'))
	}

	def __init__(self):
		super().__init__()

		# settings
		self.settings = self.loadSettings()

		# widgets
		self.urlLine = QLineEdit()
		self.urlLine.setText(self.DEFAULT_URL)
		self.urlLine.textEdited.connect(self.reloadUrlMessageLine)

		self.urlMessageLine = QLabel(self.DEFAULT_URL_MESSAGE)

		urlLayout = QVBoxLayout()
		urlLayout.addWidget(self.urlLine)
		urlLayout.addWidget(self.urlMessageLine)

		self.destinationLine = QLineEdit(self.settings['destination'])
		self.destinationLine.setReadOnly(True)

		self.selectDestinationBtn = QPushButton()
		self.selectDestinationBtn.setToolTip('Sélectionner le dossier de destination')
		self.selectDestinationBtn.setIcon(QIcon(os.path.join(ICON_FOLDER, 'open.png')))
		self.selectDestinationBtn.setFixedWidth(60)
		self.selectDestinationBtn.clicked.connect(self.selectDestination)

		self.displayDestinationBtn = QPushButton()
		self.displayDestinationBtn.setToolTip('Ouvrir le dossier de destination')
		self.displayDestinationBtn.setFixedWidth(60)
		self.displayDestinationBtn.setIcon(QIcon(os.path.join(ICON_FOLDER, 'search.png')))
		self.displayDestinationBtn.clicked.connect(self.displayDestination)

		self.downloadButton = QPushButton('Télécharger')
		self.downloadButton.setFixedWidth(200)
		self.downloadButton.clicked.connect(self.download)

		self.formatCombo = QComboBox()
		self.formatCombo.setFixedWidth(250)
		for frmt in FORMATS:
			self.formatCombo.addItem(frmt)

		# destinationLayout
		destinationLayout = QHBoxLayout()
		destinationLayout.addWidget(self.destinationLine)
		destinationLayout.addWidget(self.selectDestinationBtn)
		destinationLayout.addWidget(self.displayDestinationBtn)

		# gridLayout
		grid = QGridLayout()

		row = -1

		row += 1
		grid.addWidget(QLabel('Lien Youtube'), row, 0, Qt.AlignTop)
		grid.addLayout(urlLayout, row, 1)

		row += 1
		grid.addWidget(QLabel('Destination'), row, 0, Qt.AlignTop)
		grid.addLayout(destinationLayout, row, 1)

		row += 1
		grid.addWidget(QLabel('Format'), row, 0, Qt.AlignTop)
		grid.addWidget(self.formatCombo, row, 1)

		row += 1
		grid.addWidget(self.downloadButton, row, 0, 1, 2, Qt.AlignRight)

		# mainLayout
		mainLayout = QVBoxLayout(self)
		mainLayout.setAlignment(Qt.AlignTop)
		mainLayout.addLayout(grid)

	def reload(self):
		self.reloadUrlMessageLine()

	def loadSettings(self):
		if not os.path.isfile(self.SETTINGS_FILE):
			return self.DEFAULT_SETTINGS

		with open(self.SETTINGS_FILE, 'r') as f:
			user_settings = json.load(f)
			return {**self.DEFAULT_SETTINGS, **user_settings}

	def saveSettings(self):
		settings_directory = os.path.dirname(self.SETTINGS_FILE)
		if not os.path.isdir(settings_directory):
			os.makedirs(settings_directory)

		with open(self.SETTINGS_FILE, 'w') as f:
			json.dump(self.settings, f)

	def selectDestination(self):
		directory = QFileDialog.getExistingDirectory()
		print(f'directory: {directory}')
		if not directory:
			return
		self.destinationLine.setText(directory)
		self.settings['destination'] = directory

		self.saveSettings()

	def displayDestination(self):
		os.startfile(self.destinationLine.text())

	def reloadUrlMessageLine(self):
		url = self.urlLine.text()

		self.urlMessageLine.setText(self.DEFAULT_URL_MESSAGE)

		videos = getVideos(url)

		messageStack = list()
		messageStack.append(f'{len(videos)} vidéo(s) trouvée(s):')
		for i, video in enumerate(videos):
			if i > 10:
				messageStack.append('    ...')
				break
			else:
				messageStack.append(f'    . {video.author} - {video.title}')

		self.urlMessageLine.setText('\n'.join(messageStack))

	def download(self):
		# get videos
		url = self.urlLine.text()
		videos = getVideos(url)

		# download
		chosenFormat = self.formatCombo.currentText()
		destination = self.destinationLine.text()
		for i, video in enumerate(videos):
			try:
				downloadVideo(video, destination, chosenFormat)
			except Exception as e:
				print(e)
				print(traceback.format_exc())
"""


class OperationEditor(QWidget):

	def __init__(self):
		super().__init__()

		self.operation = None
		self.accounts = list()

		self.account_combo = QComboBox()

		self.date_line = QLineEdit()

		self.label_text = QTextEdit()

		self.amount_spin = QDoubleSpinBox()
		self.amount_spin.setMinimum(-1_000_000)
		self.amount_spin.setMaximum(1_000_000)

		self.category_line = QLineEdit()

		attribute_layout = QFormLayout()
		attribute_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
		attribute_layout.addRow('Account', self.account_combo)
		attribute_layout.addRow('Date', self.date_line)
		attribute_layout.addRow('Label', self.label_text)
		attribute_layout.addRow('Amount', self.amount_spin)
		attribute_layout.addRow('Category', self.category_line)
		attribute_layout.addItem(
			QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
		)

		main_layout = QVBoxLayout()
		main_layout.addLayout(attribute_layout)
		self.setLayout(main_layout)

		self.reload()

	def reload(self):
		# accounts
		self.account_combo.clear()

		if self.operation is None:
			state = False

			label = ''
			date = ''
			account = ''
			amount = Amount()
		else:
			for account in self.accounts:
				self.account_combo.addItem(account)

			state = True

			label = self.operation.label
			date = self.operation.date
			account = self.operation.account
			amount = self.operation.amount

		self.label_text.setText(label)
		self.date_line.setText(date)
		self.account_combo.setCurrentText(account)

		amount_in_money = int(amount) / 100
		self.amount_spin.setValue(amount_in_money)

		currency_symbol = CURRENCIES.SYMBOLS.get(amount.currency)
		self.amount_spin.setSuffix(f' {currency_symbol}')

		self.account_combo.setEnabled(state)
		self.date_line.setEnabled(state)
		self.label_text.setEnabled(state)
		self.amount_spin.setEnabled(state)
		self.category_line.setEnabled(state)

class OperationTreeItem(QTreeWidgetItem):

	HEADERS_LABEL = 'date', 'label', 'amount'
	HEADERS_WIDTH = None, 500, None

	def __init__(self):
		super().__init__()

		self.operation = Operation()

		for index in range(len(self.HEADERS_LABEL)):
			self.setSizeHint(index, QSize(0, 50))

	def reload(self):
		self.setText(0, self.operation.date)

		category = '😍'
		label = get_one_liner_text(self.operation.label)
		text = f'{category} {label}'

		self.setText(1, text)
		self.setText(2, str(self.operation.amount))

		# category_icon = os.path.join(CATEGORIES_ICON_FOLDER, 'ic_coffe.png')
		# self.setIcon(1, QIcon(category_icon))

		self.setToolTip(1, self.operation.label)


class OperationsTree(QTreeWidget):

	def __init__(self):
		super().__init__()

		self.setHeaderLabels(OperationTreeItem.HEADERS_LABEL)
		self.setAlternatingRowColors(True)
		self.setSelectionMode(self.SelectionMode.ExtendedSelection)

		for index, width in enumerate(OperationTreeItem.HEADERS_WIDTH):
			if width is None:
				continue
			self.setColumnWidth(index, width)

		self.operations = Operations()


	def reload(self):
		self.clear()

		for operation in self.operations.operations:
			tree_item = OperationTreeItem()
			tree_item.operation = operation
			tree_item.reload()

			self.addTopLevelItem(tree_item)

class ComptesWid(QWidget):

	def __init__(self):
		super().__init__()

		self.file = r'G:\Mon Drive\workspace\mes_comptes\operations_ca2.csv'

		self.operations = Operations()

		"""series = QLineSeries()
		series.append(0, 'plop')
		series.append(2, 'plip')

		chartView = QChartView()

		chart = chartView.chart()
		chart.addSeries(series)
		chart.createDefaultAxes()"""

		# account_combo
		self.account_combo = QComboBox()
		self.account_combo.currentTextChanged.connect(self.account_combo_text_changes)

		# info
		self.account_info_label = QLabel()
		self.selection_info_label = QLabel()
		self.selection_info_label.setAlignment(Qt.AlignmentFlag.AlignRight)

		info_layout = QHBoxLayout()
		info_layout.addWidget(self.account_info_label)
		info_layout.addStretch()
		info_layout.addWidget(self.selection_info_label)

		# account layout
		account_layout = QVBoxLayout()
		account_layout.addWidget(self.account_combo)
		account_layout.addLayout(info_layout)

		# operations_tree
		self.operations_tree = OperationsTree()
		self.operations_tree.itemSelectionChanged.connect(self.selected_operations_changes)

		left_panel_layout = QVBoxLayout()
		left_panel_layout.addLayout(account_layout)
		left_panel_layout.addWidget(self.operations_tree)

		left_panel_layout_w = QWidget()
		left_panel_layout_w.setLayout(left_panel_layout)

		# attribute editor
		self.operation_editor = OperationEditor()

		splitter = QSplitter(Qt.Orientation.Horizontal)
		splitter.addWidget(left_panel_layout_w)
		splitter.addWidget(self.operation_editor)

		splitter.setSizes((400, 100))

		main_layout = QHBoxLayout()
		main_layout.addWidget(splitter)

		self.setLayout(main_layout)

	def selected_operations_changes(self):
		selected_items = self.operations_tree.selectedItems()

		n_selected = len(selected_items)

		# operation
		if n_selected == 1:
			self.operation_editor.operation = selected_items[0].operation
		else:
			self.operation_editor.operation = None

		self.operation_editor.reload()

		# selection info
		sum_amount = 0
		average_amount = 0
		min_amount = 0
		max_amount = 0
		label = (f'Selected Operations: {n_selected}\n'
				 f'Sum: {sum_amount} | '
				 f'Average: {average_amount} | '
				 f'Min: {min_amount} | '
				 f'Max: {max_amount}')
		self.selection_info_label.setText(label)

	def account_combo_text_changes(self, account):
		account_operations = self.operations.get_account_operations(account)

		# operations tree
		self.operations_tree.operations = account_operations
		self.operations_tree.reload()

		# account balance
		account_balance = account_operations.get_balance()
		account_operations_number = len(account_operations.operations)

		label = f'Balance: {account_balance}\nOperations: {account_operations_number}'
		self.account_info_label.setText(label)

	def reload(self):
		self.operations = Operations.from_credit_agricole_csv(self.file)

		# accounts
		accounts = self.operations.get_accounts()

		self.account_combo.clear()
		for account in accounts:
			self.account_combo.addItem(account)

		self.operation_editor.accounts = accounts

		self.selected_operations_changes()



def open_comptes():
	app = QApplication()

	w = ComptesWid()
	w.reload()

	ui = QMainWindow()
	# ui.setWindowIcon(QIcon(os.path.join(ICON_FOLDER, 'youtube.png')))
	ui.setWindowTitle('Comptes')
	ui.setCentralWidget(w)
	ui.showMaximized()

	app.exec_()