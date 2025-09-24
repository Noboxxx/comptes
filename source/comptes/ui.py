import os
from functools import partial

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from .core import *
from .utils import print_json, get_one_liner_text, create_category_icon, create_category_pixmap

__folder__ = os.path.dirname(__file__)
ICON_FOLDER = os.path.join(__folder__, 'icon')
CATEGORIES_ICON_FOLDER = os.path.join(ICON_FOLDER, 'categories')


class CategoryPicker(QLineEdit):

	def __init__(self):
		super().__init__()
		self.project = Project()

		self.selected_category = Category()

		self.setReadOnly(True)

		self.menu = QMenu()

	def reload(self):
		print('CategoryPicker.reload')

		self.menu = QMenu()

		category_groups_map = dict()

		for category_group in self.project.category_groups:
			icon = create_category_icon(
				'',
				category_group.color,
				16
			)

			category_group_menu = QMenu(str(category_group))
			category_group_menu.setIcon(icon)

			category_groups_map[category_group.id] = category_group_menu
			self.menu.addMenu(category_group_menu)

		for category in self.project.categories:
			icon = create_category_icon(
				category.emoji,
				category.category_group.color,
				16
			)

			category_action = QAction(str(category), self)
			category_action.triggered.connect(
				partial(
					self.set_category_selected,
					category
				)
			)
			category_action.setIcon(icon)

			menu = category_groups_map[category.category_group.id]
			menu.addAction(category_action)

	def set_category_selected(self, category):
		if category is None:
			category_label = ''
		else:
			category_label = str(category)

		print('category', category, type(category))

		self.setText(category_label)
		self.selected_category = category

	def mousePressEvent(self, event):
		local_point = QPoint(0, self.height())
		world_point = self.mapToGlobal(local_point)
		self.menu.exec_(world_point)


class CategoryGroupEditor(QDialog):
	def __init__(self, parent):
		super().__init__(parent)

		self.category_group = CategoryGroup()

		self.setWindowTitle('Category Group Editor')
		self.resize(300, 300)
		
		self.r_spin = QSpinBox()
		self.r_spin.valueChanged.connect(self.reload_color_preview)
		self.r_spin.setMaximum(255)

		self.g_spin = QSpinBox()
		self.g_spin.valueChanged.connect(self.reload_color_preview)
		self.g_spin.setMaximum(255)

		self.b_spin = QSpinBox()
		self.b_spin.valueChanged.connect(self.reload_color_preview)
		self.b_spin.setMaximum(255)
		
		self.color_preview = QLabel()

		color_layout = QHBoxLayout()
		color_layout.addWidget(self.color_preview)
		color_layout.addWidget(self.r_spin)
		color_layout.addWidget(self.g_spin)
		color_layout.addWidget(self.b_spin)

		self.name_line = QLineEdit()
		self.name_line.setPlaceholderText('default')

		form_layout = QFormLayout()
		form_layout.addRow('Name', self.name_line)
		form_layout.addRow('Color', color_layout)

		ok_btn = QPushButton('Ok')
		ok_btn.clicked.connect(self.validate)

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

	def validate(self):
		name = self.name_line.text() or self.name_line.placeholderText()
		
		r = self.r_spin.value()
		g = self.g_spin.value()
		b = self.b_spin.value()

		self.category_group.name = name
		self.category_group.color = r, g, b

		self.accept()

	def reload_color_preview(self):
		r = self.r_spin.value()
		g = self.g_spin.value()
		b = self.b_spin.value()

		color = r, g, b

		pixmap = create_category_pixmap(str(), color, 12)
		self.color_preview.setPixmap(pixmap)

	def reload(self):
		name = self.category_group.name
		r, g, b = self.category_group.color

		self.name_line.setText(name)
		
		self.r_spin.setValue(r)
		self.g_spin.setValue(g)
		self.b_spin.setValue(b)

		self.reload_color_preview()


class CategoryEditor(QDialog):
	def __init__(self, parent):
		super().__init__(parent)

		self.category = Category()
		self.category_groups = list()

		self.setWindowTitle('Category Editor')
		self.resize(300, 300)

		self.name_line = QLineEdit()
		self.name_line.setPlaceholderText('default')

		self.category_group_combo = QComboBox()

		self.emoji_line = QLineEdit()
		self.emoji_line.setPlaceholderText('🪙')

		form_layout = QFormLayout()
		form_layout.addRow('Name', self.name_line)
		form_layout.addRow('Emoji', self.emoji_line)
		form_layout.addRow('Category Group', self.category_group_combo)

		ok_btn = QPushButton('Ok')
		ok_btn.clicked.connect(self.validate)

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

	def validate(self):
		name = self.name_line.text() or self.name_line.placeholderText()
		emoji = self.emoji_line.text() or self.emoji_line.placeholderText()
		category_group = self.category_group_combo.currentData(Qt.ItemDataRole.UserRole)

		self.category.name = name
		self.category.emoji = emoji
		self.category.category_group = category_group

		self.accept()

	def reload(self):
		name = self.category.name
		emoji = self.category.emoji
		category_group = self.category.category_group

		self.name_line.setText(name)
		self.emoji_line.setText(emoji)

		selected_index = -1
		self.category_group_combo.clear()
		for index, cat_grp in enumerate(self.category_groups):
			if category_group is cat_grp:
				selected_index = index
			self.category_group_combo.addItem(str(cat_grp), userData=cat_grp)
		self.category_group_combo.setCurrentIndex(selected_index)


class CategoryView(QDialog):

	def __init__(self, parent):
		super().__init__(parent)

		self.project = Project()

		self.setWindowTitle('Category View')
		self.resize(600, 600)

		self.category_group_tree = QTreeWidget()
		self.category_group_tree.setIconSize(QSize(32, 32))
		self.category_group_tree.setHeaderLabel('Category Group')

		self.category_tree = QTreeWidget()
		self.category_tree.setIconSize(QSize(32, 32))
		self.category_tree.setHeaderLabel('Category')

		tree_layout = QHBoxLayout()
		tree_layout.addWidget(self.category_group_tree)
		tree_layout.addWidget(self.category_tree)

		edit_selected_category_group_action = QAction('Edit Selected Category Group', self)
		edit_selected_category_action = QAction('Edit Selected Category', self)

		create_category_group_action = QAction('Create Category Group', self)
		create_category_group_action.triggered.connect(self.create_category_group)

		create_category_action = QAction('Create Category', self)
		create_category_action.triggered.connect(self.create_category)

		edit_menu = QMenu('Edit')
		edit_menu.addAction(edit_selected_category_action)
		edit_menu.addAction(edit_selected_category_group_action)

		create_menu = QMenu('Create')
		create_menu.addAction(create_category_action)
		create_menu.addAction(create_category_group_action)

		menu_bar = QMenuBar()
		menu_bar.addMenu(edit_menu)
		menu_bar.addMenu(create_menu)

		main_layout = QVBoxLayout(self)
		main_layout.setMenuBar(menu_bar)
		main_layout.addLayout(tree_layout)

	def create_category_group(self):
		editor = CategoryGroupEditor(self)
		editor.reload()

		proceed = editor.exec()

		if not proceed:
			print('Operation Canceled')
			return

		self.project.category_groups.append(editor.category_group)

		self.reload()

	def create_category(self):
		editor = CategoryEditor(self)
		editor.category_groups = self.project.category_groups
		editor.reload()

		proceed = editor.exec()

		if not proceed:
			print('Operation Canceled')
			return

		self.project.categories.append(editor.category)

		self.reload()

	def reload(self):
		self.category_group_tree.clear()
		for category_group in self.project.category_groups:
			icon = create_category_icon(
				text='',
				color=category_group.color,
				radius=32,
			)

			item = QTreeWidgetItem()
			item.setSizeHint(0, QSize(0, 50))
			item.setText(0, str(category_group))
			item.setIcon(0, icon)

			self.category_group_tree.addTopLevelItem(item)

		self.category_tree.clear()
		for category in self.project.categories:
			icon = create_category_icon(
				text=category.emoji,
				color=category.category_group.color,
				radius=32,
			)

			item = QTreeWidgetItem()
			item.setSizeHint(0, QSize(0, 50))
			item.setText(0, str(category))
			item.setIcon(0, icon)

			self.category_tree.addTopLevelItem(item)


class AccountEditor(QDialog):

	def __init__(self, parent):
		super().__init__(parent)

		self.account = Account()

		self.setWindowTitle('Account Editor')
		self.resize(300, 300)

		self.account_name_line = QLineEdit()
		self.account_number_line = QLineEdit()

		form_layout = QFormLayout()
		form_layout.addRow('Name', self.account_name_line)
		form_layout.addRow('Number', self.account_number_line)

		ok_btn = QPushButton('Ok')
		ok_btn.clicked.connect(self.validate)

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

	def validate(self):
		name = self.account_name_line.text()
		number = self.account_number_line.text()

		self.account.name = name
		self.account.number = number

		self.accept()

	def reload(self):
		name = self.account.name
		number = self.account.number

		self.account_name_line.setText(name)
		self.account_number_line.setText(number)


class OperationEditor(QDialog):

	def __init__(self, parent):
		super().__init__(parent)

		self.setWindowTitle('Operation Editor')
		self.resize(300, 300)

		self.operation = Operation()
		self.project = Project()

		self.account_combo = QComboBox()
		self.date_line = QLineEdit()

		self.label_line = QTextEdit()

		self.amount_spin = QDoubleSpinBox()
		self.amount_spin.setMinimum(-1_000_000)
		self.amount_spin.setMaximum(1_000_000)

		self.category_picker = CategoryPicker()

		form_layout = QFormLayout()
		form_layout.addRow('Account', self.account_combo)
		form_layout.addRow('Date', self.date_line)
		form_layout.addRow('Label', self.label_line)
		form_layout.addRow('Amount', self.amount_spin)
		form_layout.addRow('Category', self.category_picker)

		ok_btn = QPushButton('Ok')
		ok_btn.clicked.connect(self.validate)

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

	def validate(self):
		account = self.account_combo.currentData(Qt.ItemDataRole.UserRole)
		label = self.label_line.toPlainText()
		amount = Amount.from_float(self.amount_spin.value())
		category = self.category_picker.selected_category
		print('validate → category', category, type(category))

		date = self.date_line.text()
		note = ''

		self.operation.account = account
		self.operation.label = label
		self.operation.amount = amount
		self.operation.category = category
		self.operation.date = date
		self.operation.note = note

		self.accept()

	def reload(self):
		account = self.operation.account
		label = self.operation.label
		amount = self.operation.amount
		category = self.operation.category
		date = self.operation.date
		note = self.operation.note

		selected_index = -1
		self.account_combo.clear()
		for index, acc in enumerate(self.project.accounts):
			if account is acc:
				selected_index = index
			self.account_combo.addItem(str(acc), userData=acc)
		self.account_combo.setCurrentIndex(selected_index)

		self.category_picker.project = self.project
		self.category_picker.set_category_selected(category)
		self.category_picker.reload()

		self.label_line.setText(label)
		self.amount_spin.setValue(amount.as_unit())
		self.date_line.setText(date)


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

		header = self.horizontalHeader()
		header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

		vheader = self.verticalHeader()
		vheader.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


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

	def get_selected_operations(self):
		selected_items = self.selectedItems()

		selected_operations = list()
		for item in selected_items:
			if hasattr(item, 'operation'):
				operation = item.operation
				selected_operations.append(operation)

		return selected_operations

	def reload(self):
		self.clear()

		for operation in self.project.operations:
			date = split_date(operation.date)

			if date['year'] != self.selected_year:
				continue

			if operation.account is not self.selected_account:
				continue

			tree_item = OperationTreeItem()
			tree_item.operation = operation
			tree_item.reload()

			self.addTopLevelItem(tree_item)


class ComptesWidget(QWidget):

	def __init__(self):
		super().__init__()

		self.project = Project()

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
		self.operations_tree.itemSelectionChanged.connect(self.reload_selection_info_label)

		top_layout = QVBoxLayout()
		top_layout.addWidget(self.account_combo)
		top_layout.addWidget(self.years_combo)
		top_layout.addWidget(self.monthly_table)

		bot_layout = QVBoxLayout()
		bot_layout.addLayout(operations_info_layout)
		bot_layout.addWidget(self.operations_tree)

		# splitter
		splitter = QSplitter(Qt.Orientation.Vertical)

		layouts = top_layout, bot_layout
		for layout in layouts:
			w = QWidget()
			w.setLayout(layout)
			splitter.addWidget(w)

		sizes = 100, 250
		splitter.setSizes(sizes)

		# main_layout
		main_layout = QVBoxLayout()
		main_layout.addWidget(splitter)

		self.setLayout(main_layout)

	def save_as_project(self):
		path, flt = QFileDialog.getSaveFileName(self)

		if not path:
			print('Operation canceled')
			return

		self.project.save(path)
		print(f'File saved at {path!r}')

	def new_project(self):
		reply = QMessageBox.question(
			self,
			'New Project',
			'This is not undoable. Are you sure?',
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
		)

		if reply != QMessageBox.StandardButton.Yes:
			print('Operation Canceled')
			return

		self.project = Project()

		self.reload()

	def open_project(self):
		path, flt = QFileDialog.getOpenFileName(self)

		if not path:
			print('Operation canceled')
			return

		self.project = Project.open(path)

		self.reload()

	def import_credit_agricole_csv(self):
		account = self.account_combo.currentData(Qt.ItemDataRole.UserRole)

		path, flt = QFileDialog.getOpenFileName(self)

		if not path:
			print('Operation canceled')
			return

		self.project.import_credit_agricole_csv(path, account)

		self.reload()

	def print_project(self):
		print_json(self.project)

	def get_menu_bar(self):
		save_as_project_action = QAction('Save as', self)
		save_as_project_action.setShortcut('Ctrl+S')
		save_as_project_action.triggered.connect(self.save_as_project)

		open_project_action = QAction('Open', self)
		open_project_action.setShortcut('Ctrl+O')
		open_project_action.triggered.connect(self.open_project)

		new_project_action = QAction('New', self)
		new_project_action.setShortcut('Ctrl+N')
		new_project_action.triggered.connect(self.new_project)

		print_project_action = QAction('Print', self)
		print_project_action.triggered.connect(self.print_project)

		# project_menu = QMenu('Project', self)
		# project_menu.addAction(open_project_action)
		# project_menu.addAction(save_as_project_action)
		# project_menu.addAction(new_project_action)
		# project_menu.addSeparator()
		# project_menu.addAction(print_project_action)

		import_ca_action = QAction('Crédit Agricole (.csv)', self)
		import_ca_action.triggered.connect(self.import_credit_agricole_csv)

		import_menu = QMenu('Import')
		import_menu.addAction(import_ca_action)

		file_menu = QMenu('File')
		file_menu.addAction(open_project_action)
		file_menu.addAction(save_as_project_action)
		file_menu.addAction(new_project_action)
		file_menu.addSeparator()
		file_menu.addMenu(import_menu)
		file_menu.addSeparator()
		file_menu.addAction(print_project_action)

		edit_account_act = QAction('Edit Current Account', self)
		edit_account_act.triggered.connect(self.edit_account)

		edit_operation_act = QAction('Edit Selected Operation', self)
		edit_operation_act.triggered.connect(self.edit_operation)

		edit_categories_act = QAction('Edit Categories', self)
		edit_categories_act.triggered.connect(self.edit_categories)

		edit_menu = QMenu('Edit')
		edit_menu.addAction(edit_operation_act)
		edit_menu.addAction(edit_categories_act)
		edit_menu.addAction(edit_account_act)

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

	def edit_categories(self):
		category_view = CategoryView(self)
		category_view.project = self.project
		category_view.reload()
		category_view.show()

		proceed = category_view.exec()

		if not proceed:
			print('Operation Canceled')
			return

		self.reload()

	def edit_operation(self):
		selected_operations = self.operations_tree.get_selected_operations()

		if not selected_operations:
			raise Exception('No operation selected')

		selected_operation = selected_operations[0]

		operation_editor = OperationEditor(self)
		operation_editor.project = self.project
		operation_editor.operation = selected_operation
		operation_editor.reload()

		proceed = operation_editor.exec()

		if not proceed:
			print('Operation Canceled')
			return

		self.reload()

	def edit_account(self):
		selected_account = self.account_combo.currentData(Qt.ItemDataRole.UserRole)

		if not selected_account:
			raise Exception('No account selected')

		account_editor = AccountEditor(self)
		account_editor.account = selected_account
		account_editor.reload()

		proceed = account_editor.exec()

		if not proceed:
			print('Operation Canceled')
			return

		self.reload()

	def create_operation(self):
		operation_editor = OperationEditor(self)
		operation_editor.project = self.project
		operation_editor.reload()

		proceed = operation_editor.exec()

		if not proceed:
			print('Operation Canceled')
			return

		self.project.operations.append(operation_editor.operation)

		self.reload()

	def create_account(self):
		account_editor = AccountEditor(self)
		account_editor.reload()

		proceed = account_editor.exec()

		if not proceed:
			print('Operation Canceled')
			return

		self.project.accounts.append(account_editor.account)

		self.reload()

	def reload_children(self):
		self.reload_monthly_table()
		self.reload_operations_tree()
		self.reload_selection_info_label()
		self.reload_account_info_label()

	def reload_monthly_table(self):
		self.monthly_table.project = self.project
		self.monthly_table.selected_account = self.account_combo.currentData(Qt.ItemDataRole.UserRole)
		self.monthly_table.selected_year = self.years_combo.currentText()

		self.monthly_table.reload()

	def reload_operations_tree(self):
		self.operations_tree.project = self.project
		self.operations_tree.selected_account = self.account_combo.currentData(Qt.ItemDataRole.UserRole)
		self.operations_tree.selected_year = self.years_combo.currentText()

		self.operations_tree.reload()

	def reload_selection_info_label(self):
		selected_items = self.operations_tree.selectedItems()

		n_selected = len(selected_items)

		# selection info
		sum_amount = 0
		average_amount = 0
		min_amount = 0
		max_amount = 0
		label = (
			f'Selected Operations: {n_selected}\n'
			 f'Sum: {sum_amount} | '
			 f'Average: {average_amount} | '
			 f'Min: {min_amount} | '
			 f'Max: {max_amount}'
		)
		self.selection_info_label.setText(label)

	def reload_account_info_label(self):
		account = self.account_combo.currentData(Qt.ItemDataRole.UserRole)

		if account:
			account_operations = self.project.get_account_operations(account)

			account_balance = self.project.get_balance(account_operations)
			account_operations_number = len(account_operations)
		else:
			account_balance = Amount()
			account_operations_number = 0

		label = f'Balance: {account_balance}\nOperations: {account_operations_number}'
		self.account_info_label.setText(label)

	def reload_accounts_combo(self):
		accounts = self.project.accounts

		current_index = self.account_combo.currentIndex()

		self.account_combo.clear()
		for account in accounts:
			self.account_combo.addItem(str(account), userData=account)

		if not accounts:
			return

		if current_index == -1:
			current_index = 0

		self.account_combo.setCurrentIndex(current_index)

	def reload_years_combo(self):
		years = self.project.get_years()

		current_index = self.years_combo.currentIndex()

		self.years_combo.clear()
		for year in years:
			self.years_combo.addItem(year)

		if not years:
			return

		if current_index == -1:
			current_index = 0

		self.years_combo.setCurrentIndex(current_index)

	def reload(self):
		self.reload_accounts_combo()
		self.reload_years_combo()
		self.reload_children()


def open_comptes():
	app = QApplication()

	# account = Account()
	# account.name = 'Compte Chèque'
	# account.number = '123456'
	#
	# operation1 = Operation()
	# operation1.date = '02/01/2025'
	# operation1.label = 'plip plop ploup'
	# operation1.account = account
	# operation1.amount = Amount(-15000)
	#
	# operation2 = Operation()
	# operation2.date = '01/01/2025'
	# operation2.label = 'bim bam boom'
	# operation2.account = account
	# operation2.amount = Amount(10000)
	#
	# project = Project()
	# project.accounts.append(account)
	# project.operations.append(operation1)
	# project.operations.append(operation2)

	w = ComptesWidget()
	# w.project = project
	w.reload()

	ui = QMainWindow()
	# ui.setWindowIcon(QIcon(os.path.join(ICON_FOLDER, 'youtube.png')))
	ui.setWindowTitle('Comptes')
	ui.setCentralWidget(w)
	ui.showMaximized()
	ui.setMenuBar(w.get_menu_bar())

	app.exec_()