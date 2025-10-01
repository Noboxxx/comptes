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


class CategoryItem(QTreeWidgetItem):

    def __init__(self, category):
        super().__init__()
        self.category = category
        self.setSizeHint(0, QSize(0, 50))

        self.reload()

    def reload(self):
        icon = self.category.get_icon(32)
        self.setText(0, str(self.category))

        self.setIcon(0, icon)


class CategoryGroupItem(QTreeWidgetItem):

    def __init__(self, category_group):
        super().__init__()
        self.category_group = category_group
        self.setSizeHint(0, QSize(0, 50))

        self.reload()

    def reload(self):
        icon = self.category_group.get_icon(32)

        self.setText(0, str(self.category_group))
        self.setIcon(0, icon)


class CategoryGroupPicker(QLineEdit):

    def __init__(self):
        super().__init__()

        self.project = None
        self.selected_category_group = None

        self.setReadOnly(True)

        self.menu = QMenu()

    def set_category_group_selected(self, category_group):
        if category_group is None:
            label = ''
        else:
            label = category_group.name

        self.setText(label)
        self.selected_category_group = category_group

    def reload(self):
        self.menu = QMenu()

        reset_action = QAction(self)
        reset_action.setText('None')
        reset_action.triggered.connect(
            partial(
                self.set_category_group_selected,
                None
            )
        )
        self.menu.addAction(reset_action)

        for category_group in self.project.category_groups:
            category_group_action = QAction(self)
            category_group_action.setIcon(category_group.get_icon(16))
            category_group_action.setText(category_group.name)
            category_group_action.triggered.connect(
                partial(
                    self.set_category_group_selected,
                    category_group
                )
            )

            self.menu.addAction(category_group_action)


    def mousePressEvent(self, event):
        local_point = QPoint(0, self.height())
        world_point = self.mapToGlobal(local_point)
        self.menu.exec_(world_point)


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
            icon = category_group.get_icon(16)

            category_group_menu = QMenu(str(category_group))
            category_group_menu.setIcon(icon)

            category_groups_map[category_group.id] = category_group_menu
            self.menu.addMenu(category_group_menu)

        for category in self.project.categories:
            icon = category.get_icon(16)

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

        self.project = None
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

        self.parent_category_group_picker = CategoryGroupPicker()

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
        form_layout.addRow('Parent', self.parent_category_group_picker)

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
        self.category_group.parent_category_group = self.parent_category_group_picker.selected_category_group
        print(self.category_group.parent_category_group)

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
        category_group = self.category_group.parent_category_group

        self.name_line.setText(name)

        self.parent_category_group_picker.project = self.project
        self.parent_category_group_picker.set_category_group_selected(category_group)
        self.parent_category_group_picker.reload()

        self.r_spin.setValue(r)
        self.g_spin.setValue(g)
        self.b_spin.setValue(b)

        self.reload_color_preview()


class CategoryEditor(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.category = Category()
        self.project = None

        self.setWindowTitle('Category Editor')
        self.resize(300, 300)

        self.name_line = QLineEdit()
        self.name_line.setPlaceholderText('default')

        self.category_group_combo = QComboBox()

        self.emoji_line = QLineEdit()

        self.keywords_text = QTextEdit()
        self.keywords_text.setPlaceholderText('keyword1\nkeyword2\nkeyword3\n...')

        form_layout = QFormLayout()
        form_layout.addRow('Name', self.name_line)
        form_layout.addRow('Emoji', self.emoji_line)
        form_layout.addRow('Category Group', self.category_group_combo)
        form_layout.addRow('Keywords', self.keywords_text)

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

        keywords_text = self.keywords_text.toPlainText()
        keywords = [x for x in keywords_text.strip().split('\n') if x]

        self.category.name = name
        self.category.emoji = emoji
        self.category.category_group = category_group
        self.category.keywords = keywords

        self.accept()

    def reload(self):
        name = self.category.name
        emoji = self.category.emoji
        category_group = self.category.category_group

        keywords_text = self.category.keywords
        keywords = '\n'.join(keywords_text)

        self.name_line.setText(name)
        self.emoji_line.setText(emoji)
        self.keywords_text.setText(keywords)

        selected_index = -1
        self.category_group_combo.clear()
        for index, cat_grp in enumerate(self.project.category_groups):
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

        self.category_tree = QTreeWidget()
        self.category_tree.setIconSize(QSize(32, 32))
        self.category_tree.setHeaderHidden(True)

        tree_layout = QHBoxLayout()
        tree_layout.addWidget(self.category_tree)

        edit_selected_category_group_action = QAction('Edit Selected Item', self)
        edit_selected_category_group_action.triggered.connect(self.edit_selected_item)

        create_category_group_action = QAction('Create Category Group', self)
        create_category_group_action.triggered.connect(self.create_category_group)

        create_category_action = QAction('Create Category', self)
        create_category_action.triggered.connect(self.create_category)

        edit_menu = QMenu('Edit')
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

    def get_selected_category(self):
        selected_items = self.category_tree.selectedItems()

        if not selected_items:
            return None

        selected_item = selected_items[0]

        if not isinstance(selected_item, CategoryItem):
            return None

        category = selected_item.category
        return category

    def edit_selected_item(self):
        selected_items = self.category_tree.selectedItems()

        if not selected_items:
            raise Exception('No item selected')

        selected_item = selected_items[0]

        if isinstance(selected_item, CategoryItem):
            editor = CategoryEditor(self)
            editor.project = self.project
            editor.category = selected_item.category
            editor.reload()
        elif isinstance(selected_item, CategoryGroupItem):
            editor = CategoryGroupEditor(self)
            editor.project = self.project
            editor.category_group = selected_item.category_group
            editor.reload()
        else:
            raise Exception('Invalid selection')

        proceed = editor.exec()

        if not proceed:
            print('Operation Canceled')
            return

        self.reload()

    def create_category_group(self):
        editor = CategoryGroupEditor(self)
        editor.project = self.project
        editor.reload()

        proceed = editor.exec()

        if not proceed:
            print('Operation Canceled')
            return

        self.project.category_groups.append(editor.category_group)

        self.reload()

    def create_category(self):
        editor = CategoryEditor(self)
        editor.project = self.project
        editor.reload()

        proceed = editor.exec()

        if not proceed:
            print('Operation Canceled')
            return

        self.project.categories.append(editor.category)

        self.reload()

    def reload(self):
        self.category_tree.clear()

        category_group_items_map = dict()
        for category_group in self.project.category_groups:
            item = CategoryGroupItem(category_group)
            category_group_items_map[category_group.id] = item

        for category_group in self.project.category_groups:
            category_group_item = category_group_items_map[category_group.id]
            parent_category_group = category_group.parent_category_group

            if not parent_category_group:
                self.category_tree.addTopLevelItem(category_group_item)
            else:
                parent_category_group_item = category_group_items_map[parent_category_group.id]
                parent_category_group_item.addChild(category_group_item)

        for category in self.project.categories:
            item = CategoryItem(category)

            category_group_id = category.category_group.id

            category_group_item = category_group_items_map[category_group_id]
            category_group_item.addChild(item)


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


class OperationItem(QTreeWidgetItem):

    def __init__(self):
        super().__init__()

        self.operation = Operation()

        for index in range(len(OperationsTree.HEADERS_LABEL)):
            self.setSizeHint(index, QSize(0, 50))

    def reload(self):
        # date
        self.setText(1, self.operation.date)

        # label
        label = get_one_liner_text(self.operation.label)
        self.setText(3, label)
        self.setToolTip(3, self.operation.label)

        # category
        category = self.operation.category
        if isinstance(category, Category):
            category_icon = category.get_icon(16)
            category_name = category.name
        else:
            category_icon = create_category_icon(
                text='❔',
                color=(100, 100, 100),
                radius=16,
            )
            category_name = 'undefined'

        self.setIcon(0, category_icon)
        self.setText(0, category_name)

        # amount
        self.setText(2, str(self.operation.amount))


class OperationsTree(QTreeWidget):

    HEADERS_LABEL = 'category', 'date', 'amount', 'label'
    HEADERS_WIDTH = 200, None, None, None

    def __init__(self):
        super().__init__()

        self.project = Project()

        self.selected_account = None
        self.selected_year = None

        self.setHeaderLabels(self.HEADERS_LABEL)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(self.SelectionMode.ExtendedSelection)
        # self.setSortingEnabled(True)
        self.setIconSize(QSize(22, 22))

        for index, width in enumerate(self.HEADERS_WIDTH):
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

            tree_item = OperationItem()
            tree_item.operation = operation
            tree_item.reload()

            self.addTopLevelItem(tree_item)


class CategorySummaryItem(QTreeWidgetItem):

    def __init__(self):
        super().__init__()

        self.operations = list()

    def reload(self):
        year_sum = Amount()
        for index in range(12):
            month = index + 1
            month_formatted = f'{month:02d}'

            month_operations = self.operations
            month_operations = [x for x in month_operations if split_date(x.date)['month'] == month_formatted]

            # amount
            month_amount = Amount()
            for operation in month_operations:
                month_amount.int += operation.amount.int

            year_sum.int += month_amount.int

            self.setText(month, str(month_amount))

            # color
            if month_amount.int > 0:
                color = Qt.GlobalColor.darkGreen
            elif month_amount.int < 0:
                color = None
            else:
                color = Qt.GlobalColor.lightGray

            if color:
                self.setForeground(month, QColor(color))

        # year
        self.setText(13, str(year_sum))

        # color
        if year_sum.int > 0:
            color = Qt.GlobalColor.darkGreen
        elif year_sum.int < 0:
            color = None
        else:
            color = Qt.GlobalColor.lightGray

        if color:
            self.setForeground(13, QColor(color))


class CategorySummaryTree(QTreeWidget):

    HEADERS_MAP = {
        'Category': 150,
        'January': None,
        'February': None,
        'March': None,
        'April': None,
        'May': None,
        'June': None,
        'July': None,
        'August': None,
        'September': None,
        'October': None,
        'November': None,
        'December': None,
        'Year': None
    }

    def __init__(self):
        super().__init__()

        self.project = None
        self.selected_account = None
        self.selected_year = None

        self.setAlternatingRowColors(True)

        headers = list(self.HEADERS_MAP.keys())
        self.setHeaderLabels(headers)

        for index, width in enumerate(self.HEADERS_MAP.values()):
            if width is None:
                continue

            self.setColumnWidth(index, width)

    def reload(self):
        self.clear()

        if self.project is None:
            print('No project found')
            return

        account_operations = [x for x in self.project.operations if x.account is self.selected_account]
        year_operations = [x for x in account_operations if split_date(x.date)['year'] == self.selected_year]

        balance_item = CategorySummaryItem()
        balance_item.setText(0, 'Balance')
        balance_item.operations = year_operations
        balance_item.reload()
        self.addTopLevelItem(balance_item)

        category_group_item_map = dict()
        for category_group in self.project.category_groups:
            category_group_operations = [x for x in year_operations if x.category and x.category.category_group is category_group]

            category_group_item = CategorySummaryItem()
            category_group_item.setText(0, category_group.name)
            category_group_item.setIcon(0, category_group.get_icon(16))

            category_group_item.operations = category_group_operations
            category_group_item.reload()

            category_group_item_map[category_group.id] = category_group_item

            self.addTopLevelItem(category_group_item)

        for category in self.project.categories:
            category_operations = [x for x in year_operations if x.category is category]

            category_item = CategorySummaryItem()
            category_item.setText(0, category.name)
            category_item.setIcon(0, category.get_icon(16))

            category_item.operations = category_operations
            category_item.reload()

            category_group_item = category_group_item_map[category.category_group.id]
            category_group_item.addChild(category_item)


class ComptesWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.project = None
        self.current_file = None

        # open recent
        self.open_recent_projects_menu = QMenu('Open Recent')

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

        # category_tree
        self.category_summary_tree = CategorySummaryTree()

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

        tab = QTabWidget()
        tab.addTab(self.category_summary_tree, 'Categories')
        tab.addTab(self.monthly_table, 'Summary')
        tab.addTab(self.operations_tree, 'Operations')

        # main_layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.account_combo)
        main_layout.addWidget(self.years_combo)
        main_layout.addWidget(tab)

        self.setLayout(main_layout)

        # new project
        self.new_project()

    def ask_save_project(self):
        if not self.current_file:
            self.ask_save_as_project()
        else:
            file = self.current_file
            self.save_project(file)

    def ask_save_as_project(self):
        file, flt = QFileDialog.getSaveFileName(self)

        if not file:
            print('Operation canceled')
            return

        self.save_project(file)

    def save_project(self, file):
        self.project.save(file)
        self.current_file = file
        self.reload()
        print(f'File saved at {file!r}')

    def ask_new_project(self):
        proceed = QMessageBox.question(
            self,
            'New Project',
            'This is not undoable. Are you sure?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if proceed != QMessageBox.StandardButton.Yes:
            print('Operation Canceled')
            return
        
        self.new_project()
        
    def new_project(self):
        self.project = Project.new()
        self.current_file = None
        self.reload()
    
    def ask_open_recent_project(self, file):
        proceed = QMessageBox.question(
            self,
            'Open Project',
            'This is not undoable. Are you sure?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if proceed != QMessageBox.StandardButton.Yes:
            print('Operation Canceled')
            return

        self.open_project(file)
    
    def reload_window_title(self):
        s = 'Comptes'
        if self.current_file is None:
            s += ' - New Project'
        else:
            s+= f' - {self.current_file}'
            
        self.setWindowTitle(s)
    
    def open_project(self, file):
        self.project = Project.open(file)
        self.current_file = file
        self.reload()
    
    def ask_open_project(self):
        file, flt = QFileDialog.getOpenFileName(self)

        if not file:
            print('Operation canceled')
            return

        self.open_project(file)

    def import_credit_agricole_csv(self):
        account = self.account_combo.currentData(Qt.ItemDataRole.UserRole)

        if account is None:
            raise Exception('No account selected')

        path, flt = QFileDialog.getOpenFileName(self)

        if not path:
            print('Operation canceled')
            return

        self.project.import_credit_agricole_csv(path, account)

        self.reload()

    def print_project(self):
        print_json(self.project)

    def get_menu_bar(self):
        ask_save_as_project_action = QAction('Save as', self)
        ask_save_as_project_action.setShortcut('Ctrl+Shift+S')
        ask_save_as_project_action.triggered.connect(self.ask_save_as_project)

        ask_save_project_action = QAction('Save', self)
        ask_save_project_action.setShortcut('Ctrl+S')
        ask_save_project_action.triggered.connect(self.ask_save_project)

        ask_open_project_action = QAction('Open', self)
        ask_open_project_action.setShortcut('Ctrl+O')
        ask_open_project_action.triggered.connect(self.ask_open_project)

        ask_new_project_action = QAction('New', self)
        ask_new_project_action.setShortcut('Ctrl+N')
        ask_new_project_action.triggered.connect(self.ask_new_project)

        print_project_action = QAction('Print', self)
        print_project_action.triggered.connect(self.print_project)

        import_ca_action = QAction('Crédit Agricole (.csv)', self)
        import_ca_action.triggered.connect(self.import_credit_agricole_csv)

        import_menu = QMenu('Import')
        import_menu.addAction(import_ca_action)

        file_menu = QMenu('File')
        file_menu.addAction(ask_new_project_action)
        file_menu.addSeparator()

        file_menu.addAction(ask_save_project_action)
        file_menu.addAction(ask_save_as_project_action)
        file_menu.addSeparator()

        file_menu.addAction(ask_open_project_action)
        file_menu.addMenu(self.open_recent_projects_menu)
        file_menu.addMenu(import_menu)
        file_menu.addSeparator()

        file_menu.addAction(print_project_action)

        guess_category_on_selected_operations_act = QAction('Guess Category on Selected Operations', self)
        guess_category_on_selected_operations_act.triggered.connect(self.guess_category_on_selected_operations)

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
        edit_menu.addSeparator()
        edit_menu.addAction(guess_category_on_selected_operations_act)

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

    def guess_category_on_selected_operations(self):
        selected_operations = self.operations_tree.get_selected_operations()

        for operation in selected_operations:
            operation_label_lower = operation.label.lower()

            new_category = None
            for category in self.project.categories:
                if new_category:
                    break

                for keyword in category.keywords:
                    keyword_lower = keyword.lower()

                    if keyword_lower in operation_label_lower:
                        new_category = category
                        break

            if new_category:
                operation.category = new_category

        self.reload()

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
        self.reload_window_title()
        self.reload_category_summary_tree()
        self.reload_monthly_table()
        self.reload_operations_tree()
        self.reload_selection_info_label()
        self.reload_account_info_label()
        self.reload_recent_projects()

    def reload_recent_projects(self):
        self.open_recent_projects_menu.clear()

        files = [
            r'G:\Mon Drive\work\mes_comptes\test\mes_comptes.007.project.json',
            r'G:\Mon Drive\work\mes_comptes\test\mes_comptes.006.project.json'
        ]

        for file in files:
            file_name = os.path.basename(file)
            
            file_action = QAction(self)
            file_action.setText(file_name)
            file_action.triggered.connect(
                partial(
                    self.ask_open_recent_project,
                    file)
            )
            self.open_recent_projects_menu.addAction(file_action)

    def reload_category_summary_tree(self):
        self.category_summary_tree.project = self.project
        self.category_summary_tree.selected_account = self.account_combo.currentData(Qt.ItemDataRole.UserRole)
        self.category_summary_tree.selected_year = self.years_combo.currentText()

        self.category_summary_tree.reload()

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

    w = ComptesWidget()
    w.reload()
    
    ui = QMainWindow()
    ui.setCentralWidget(w)
    ui.showMaximized()
    ui.setMenuBar(w.get_menu_bar())

    w.windowTitleChanged.connect(ui.setWindowTitle)
    w.windowTitleChanged.emit(w.windowTitle())

    app.exec_()