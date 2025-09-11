import os

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from .core import *
from .utils import print_json, get_one_liner_text

__folder__ = os.path.dirname(__file__)
ICON_FOLDER = os.path.join(__folder__, 'icon')
CATEGORIES_ICON_FOLDER = os.path.join(ICON_FOLDER, 'categories')


class AccountEditor(QDialog):

	def __init__(self, parent):
		super().__init__(parent)

		self.account = Account()

		self.setWindowTitle('Account')
		self.resize(300, 300)

		self.account_name_line = QLineEdit()
		self.account_name_line.textChanged.connect(lambda x: setattr(self.account, 'name', x))

		self.account_number_line = QLineEdit()
		self.account_name_line.textChanged.connect(lambda x: setattr(self.account, 'number', x))

		form_layout = QFormLayout()
		form_layout.addRow('Name', self.account_name_line)
		form_layout.addRow('Number', self.account_number_line)

		ok_btn = QPushButton('Ok')
		ok_btn.clicked.connect(self.accept)

		cancel_btn = QPushButton('Cancel')
		cancel_btn.clicked.connect(self.reject)

		button_layout = QHBoxLayout()
		button_layout.addStretch()
		button_layout.addWidget(cancel_btn)
		button_layout.addWidget(ok_btn)

		main_layout = QVBoxLayout()
		main_layout.addLayout(form_layout)
		main_layout.addLayout(button_layout)

		self.setLayout(main_layout)


class OperationEditor(QDialog):

	def __init__(self, parent):
		super().__init__(parent)

		self.setWindowTitle('Operation')
		self.resize(300, 300)

		self.operation = Operation()
		self.accounts = list()
		self.categories = list()

		self.account_combo = QComboBox()
		self.account_combo.currentIndexChanged.connect(
			lambda x:
				setattr(
					self.operation,
					'account',
					self.account_combo.currentData(Qt.ItemDataRole.UserRole)
				)
		)

		self.date_line = QLineEdit()
		self.date_line.textChanged.connect(lambda x: setattr(self.operation, 'date', x))

		self.label_line = QTextEdit()
		self.label_line.textChanged.connect(lambda: setattr(self.operation, 'label', self.label_line.toPlainText()))

		self.amount_spin = QDoubleSpinBox()
		self.amount_spin.setMinimum(-1_000_000)
		self.amount_spin.setMaximum(1_000_000)
		self.amount_spin.valueChanged.connect(lambda x: setattr(self.operation, 'amount', Amount.from_float(x)))

		self.category_line = QLineEdit()

		form_layout = QFormLayout()
		form_layout.addRow('Account', self.account_combo)
		form_layout.addRow('Date', self.date_line)
		form_layout.addRow('Label', self.label_line)
		form_layout.addRow('Amount', self.amount_spin)
		form_layout.addRow('Category', self.category_line)

		ok_btn = QPushButton('Ok')
		ok_btn.clicked.connect(self.accept)

		cancel_btn = QPushButton('Cancel')
		cancel_btn.clicked.connect(self.reject)

		button_layout = QHBoxLayout()
		button_layout.addStretch()
		button_layout.addWidget(cancel_btn)
		button_layout.addWidget(ok_btn)

		main_layout = QVBoxLayout()
		main_layout.addLayout(form_layout)
		main_layout.addLayout(button_layout)

		self.setLayout(main_layout)

	def reload(self):
		# accounts
		self.account_combo.clear()

		for account in self.accounts:
			self.account_combo.addItem(str(account), userData=account)


class MonthlyTable(QTableWidget):

	def __init__(self):
		super().__init__()

		self.project = Project()

		self.selected_year = None
		self.selected_account = None

		# table
		self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

		# headers
		self.h_headers = (
			'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
			'September', 'October', 'November', 'December', 'Year'
		)

		self.v_headers = (
			'Income',
			'Expenses',
			'Total',
			'Balance'
		)

		# columns / rows
		self.setColumnCount(len(self.h_headers))
		self.setRowCount(len(self.v_headers))

		for index in range(len(self.h_headers)):
			self.setColumnWidth(index, 80)


	def set_header_labels(self):
		self.setVerticalHeaderLabels(self.v_headers)
		self.setHorizontalHeaderLabels(self.h_headers)

	def reload(self):
		self.clear()

		self.set_header_labels()

		months_stats, year_stats = self.project.get_year_summary(self.selected_account, self.selected_year)

		expenses = list()
		income = list()
		total = list()
		balance = list()
		for month, data in months_stats.items():
			expenses.append(data['expenses'])
			income.append(data['income'])
			total.append(data['total'])
			balance.append(data['balance'])

		expenses.append(year_stats['expenses'])
		income.append(year_stats['income'])
		total.append(year_stats['total'])
		balance.append(year_stats['balance'])

		table = income, expenses, total, balance
		for row_index, values in enumerate(table):
			for column_index, value in enumerate(values):
				if value is None:
					continue
				item = QTableWidgetItem(str(value))
				self.setItem(row_index, column_index, item)


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

		self.project = Project()

		self.selected_account = None
		self.selected_year = None

		self.setHeaderLabels(OperationTreeItem.HEADERS_LABEL)
		self.setAlternatingRowColors(True)
		self.setSelectionMode(self.SelectionMode.ExtendedSelection)
		# self.setSortingEnabled(True)

		for index, width in enumerate(OperationTreeItem.HEADERS_WIDTH):
			if width is None:
				continue
			self.setColumnWidth(index, width)

	def reload(self):
		self.clear()

		for operation in self.project.operations:
			date = split_date(operation.date)

			if date['year'] != self.selected_year:
				continue

			tree_item = OperationTreeItem()
			tree_item.operation = operation
			tree_item.reload()

			self.addTopLevelItem(tree_item)


class ComptesWidget(QWidget):

	def __init__(self):
		super().__init__()

		self.project = Project()

		self.selected_account = None
		self.selected_year = None

		# account_combo
		self.account_combo = QComboBox()
		self.account_combo.setPlaceholderText('account')
		self.account_combo.currentTextChanged.connect(self.reload_children)

		# years_combo
		self.years_combo = QComboBox()
		self.years_combo.setPlaceholderText('year')
		self.years_combo.currentTextChanged.connect(self.reload_children)

		# monthly table
		self.monthly_table = MonthlyTable()

		# info
		self.account_info_label = QLabel()

		self.selection_info_label = QLabel()
		self.selection_info_label.setAlignment(Qt.AlignmentFlag.AlignRight)

		operations_info_layout = QHBoxLayout()
		operations_info_layout.addWidget(self.account_info_label)
		operations_info_layout.addStretch()
		operations_info_layout.addWidget(self.selection_info_label)

		# operations_tree
		self.operations_tree = OperationsTree()
		# self.operations_tree.itemSelectionChanged.connect(self.selected_operations_changes)

		# main_layout
		main_layout = QVBoxLayout()
		main_layout.addWidget(self.account_combo)
		main_layout.addWidget(self.years_combo)
		main_layout.addWidget(self.monthly_table)
		main_layout.addLayout(operations_info_layout)
		main_layout.addWidget(self.operations_tree)

		self.setLayout(main_layout)

	def save_as(self):
		path, flt = QFileDialog.getSaveFileName(self)

		if not path:
			print('Operation canceled')
			return

		save_project(self.project, path)
		print(f'File saved at {path!r}')

	def get_menu_bar(self):
		save_as_project_action = QAction('Save as', self)
		save_as_project_action.triggered.connect(self.save_as)

		open_project_action = QAction('Open', self)
		new_project_action = QAction('New', self)

		project_menu = QMenu('Project', self)
		project_menu.addAction(open_project_action)
		project_menu.addAction(save_as_project_action)
		project_menu.addAction(new_project_action)

		import_ca_action = QAction('Crédit Agricole (.csv)', self)

		import_menu = QMenu('Import')
		import_menu.addAction(import_ca_action)

		file_menu = QMenu('File')
		file_menu.addMenu(project_menu)
		file_menu.addMenu(import_menu)

		edit_menu = QMenu('Edit')

		create_account_act = QAction('Create Account', self)
		create_account_act.triggered.connect(self.create_account)

		create_operation_act = QAction('Create Operation', self)
		create_operation_act.triggered.connect(self.create_operation)

		create_menu = QMenu('Create')
		create_menu.addAction(create_operation_act)
		create_menu.addAction(create_account_act)

		menu_bar = QMenuBar()
		menu_bar.addMenu(file_menu)
		menu_bar.addMenu(edit_menu)
		menu_bar.addMenu(create_menu)

		return menu_bar

	def create_operation(self):
		operation_editor = OperationEditor(self)
		operation_editor.accounts = self.project.accounts
		operation_editor.categories = self.project.categories
		operation_editor.reload()

		proceed = operation_editor.exec()

		if not proceed:
			print('Operation Canceled')
			return

		self.project.operations.append(operation_editor.operation)

		self.reload()

	def create_account(self):
		account_editor = AccountEditor(self)
		proceed = account_editor.exec()

		if not proceed:
			print('Operation Canceled')
			return

		self.project.accounts.append(account_editor.account)

		self.reload()

	def reload_children(self):
		self.selected_account = self.account_combo.currentData(Qt.ItemDataRole.UserRole)
		self.selected_year = self.years_combo.currentText()

		self.reload_monthly_table()
		self.reload_operations_tree()

	def reload_monthly_table(self):
		self.monthly_table.project = self.project
		self.monthly_table.selected_account = self.selected_account
		self.monthly_table.selected_year = self.selected_year

		self.monthly_table.reload()

	def reload_operations_tree(self):
		self.operations_tree.project = self.project
		self.operations_tree.selected_account = self.selected_account
		self.operations_tree.selected_year = self.selected_year

		self.operations_tree.reload()

	# def selected_operations_changes(self):
	# 	selected_items = self.operations_tree.selectedItems()
	#
	# 	n_selected = len(selected_items)
	#
	# 	# selection info
	# 	sum_amount = 0
	# 	average_amount = 0
	# 	min_amount = 0
	# 	max_amount = 0
	# 	label = (f'Selected Operations: {n_selected}\n'
	# 			 f'Sum: {sum_amount} | '
	# 			 f'Average: {average_amount} | '
	# 			 f'Min: {min_amount} | '
	# 			 f'Max: {max_amount}')
	# 	self.selection_info_label.setText(label)
	#
	# def reload_children(self):
	# 	year = self.years_combo.currentText()
	#
	# 	self.operations_tree.year = year
	# 	self.operations_tree.reload()
	#
	# 	self.monthly_table.year = year
	# 	self.monthly_table.reload()
	#
	# 	account = self.account_combo.currentText()
	#
	# 	if account:
	# 		account_operations = self.project.operations.get_account_operations(account)
	#
	# 		# operations tree
	# 		self.operations_tree.operations = account_operations
	# 		self.operations_tree.reload()
	#
	# 		# monthly table
	# 		self.monthly_table.operations = account_operations
	# 		self.monthly_table.reload()
	#
	# 		# account balance
	# 		account_balance = account_operations.get_balance()
	# 		account_operations_number = len(account_operations)
	# 	else:
	# 		account_balance = Amount()
	# 		account_operations_number = 0
	#
	# 	label = f'Balance: {account_balance}\nOperations: {account_operations_number}'
	# 	self.account_info_label.setText(label)

	def reload_accounts_combo(self):
		accounts = self.project.accounts

		self.account_combo.clear()
		for account in accounts:
			self.account_combo.addItem(str(account), userData=account)

	def reload_years_combo(self):
		years = self.project.get_years()

		self.years_combo.clear()
		for year in years:
			self.years_combo.addItem(year)

	def reload(self):
		self.reload_accounts_combo()
		self.reload_years_combo()


def open_comptes():
	app = QApplication()

	account = Account()
	account.name = 'Compte Chèque'
	account.number = '123456'

	operation1 = Operation()
	operation1.date = '02/01/2025'
	operation1.label = 'plip plop ploup'
	operation1.account = account
	operation1.amount = Amount(-15000)

	operation2 = Operation()
	operation2.date = '01/01/2025'
	operation2.label = 'bim bam boom'
	operation2.account = account
	operation2.amount = Amount(10000)

	project = Project()
	project.accounts.append(account)
	project.operations.append(operation1)
	project.operations.append(operation2)

	w = ComptesWidget()
	w.project = project
	w.reload()

	ui = QMainWindow()
	# ui.setWindowIcon(QIcon(os.path.join(ICON_FOLDER, 'youtube.png')))
	ui.setWindowTitle('Comptes')
	ui.setCentralWidget(w)
	ui.showMaximized()
	ui.setMenuBar(w.get_menu_bar())

	app.exec_()