import csv
from datetime import datetime
import re
import os
from PySide6.QtCore import *
from .utils import random_id, create_category_pixmap, create_category_icon, json_dump, json_load


__dir__ = os.path.dirname(__file__)


class COLORS:

    RED = (200, 0, 0)
    GREEN = (0, 200, 0)
    ORANGE = (255, 128, 0)
    YELLOW = (255, 255, 0)
    GREY = (128, 128, 128)
    LIGHT_GREY = (170, 170, 170)


class CURRENCIES:
    EUR = 0
    USD = 1

    EUR_SYMBOL = '€'
    USD_SYMBOL = '$'

    SYMBOLS = {
        EUR: EUR_SYMBOL,
        USD: USD_SYMBOL,
    }

    PATTERN = {
        EUR: '{unit}{seperator}{cents} {symbol}'
    }


class REPEAT_MODE:

    NO_REPETITION = 0
    WEEKLY = 1
    MONTHLY = 2
    QUARTERLY = 3
    ANNUALLY = 4


class Project:

    def __init__(self):
        self.accounts = list()
        self.operations = list()
        self.categories = list()
        self.category_groups = list()

        self.undefined_category = Category()
        self.undefined_category.name = 'Undefined'
        self.undefined_category.emoji = '❔'
        self.undefined_category.color = (100, 100, 100)

        self.version = '1'

    def safe_delete_operation(self, operation):
        self.operations.remove(operation)

    def get_data(self):
        data = {
            'operations': self.operations,
            'accounts': self.accounts,
            'categories': self.categories,
            'category_groups': self.category_groups,
            'version': self.version,
        }

        return data

    def set_data(self, data):
        accounts_map = dict()
        for account_data in data['accounts']:
            account_id = account_data['id']

            account = Account()
            account.id = account_id
            account.name = account_data['name']
            account.number = account_data['number']

            accounts_map[account_id] = account

        category_groups_map = dict()
        for category_group_data in data['category_groups']:
            category_group_id = category_group_data['id']

            category_group = CategoryGroup()
            category_group.id = category_group_id
            category_group.name = category_group_data['name']
            category_group.color = category_group_data['color']
            category_group.emoji = category_group_data.get('emoji', '')

            category_groups_map[category_group_id] = category_group

        for category_group_data in data['category_groups']:
            parent_category_group_id = category_group_data.get('parent_category_group.id')
            parent_category_group = category_groups_map.get(parent_category_group_id)

            category_group_data_id = category_group_data['id']
            category_group = category_groups_map[category_group_data_id]

            category_group.parent_category_group = parent_category_group


        categories_map = dict()
        for category_data in data['categories']:
            category_group_id = category_data['category_group.id']
            category_group = category_groups_map[category_group_id]

            category_id = category_data['id']

            category = Category()
            category.id = category_id
            category.name = category_data['name']
            category.emoji = category_data['emoji']
            category.category_group = category_group
            category.keywords = category_data.get('keywords', list())

            categories_map[category_id] = category

        operations = list()
        for operation_data in data['operations']:
            account_id = operation_data['account.id']
            account = accounts_map[account_id]

            amount_txt = operation_data['amount']
            amount = Amount.from_string(amount_txt)

            category_id = operation_data['category.id']
            category = categories_map.get(category_id)

            operation_id = operation_data.get('id')

            date = operation_data['date']
            date = Date.from_string(date)

            operation = Operation()
            if operation_id:
                operation.id = operation_id
            operation.account = account
            operation.label = operation_data['label']
            operation.amount = amount
            operation.category = category
            operation.date = date
            operation.note = operation_data['note']
            operation.is_budget = operation_data.get('is_budget', False)

            operations.append(operation)

        self.accounts = list(accounts_map.values())
        self.operations = operations
        self.category_groups = list(category_groups_map.values())
        self.categories = list(categories_map.values())

    def get_years(self):
        years = list()

        for operation in self.operations:
            operation_year = str(operation.date.year())

            if operation_year not in years:
                years.append(operation_year)

        years.sort()
        years.reverse()
        return years

    def get_account_operations(self, account):
        account_operations = list()

        for operation in self.operations:
            if operation.account is account:
                account_operations.append(operation)

        return account_operations

    def get_year_account_operations(self, account, year):
        account_operations = self.get_account_operations(account)

        year_account_operation = list()
        for account_operation in account_operations:
            operation_year = account_operation.date.year()

            if operation_year == int(year):
                year_account_operation.append(account_operation)

        return year_account_operation

    def get_month_account_operations(self, account, year, month):
        year_account_operations = self.get_year_account_operations(account, year)

        month_account_operation = list()
        for account_operation in year_account_operations:
            operation_month = account_operation.date.month()

            if operation_month == int(month):
                month_account_operation.append(account_operation)

        return month_account_operation

    def get_balance(self, account, date=None):
        balance = Amount()

        if date is not None:
            date = Date.from_string(date)

        account_operations = self.get_account_operations(account)
        for operation in account_operations:

            if date is None or operation.date <= date:
                balance += operation.amount

        return balance
    #
    # def get_year_summary(self, account, year):
    #     months_data = dict()
    #
    #     year_expenses = Amount()
    #     year_income = Amount()
    #     year_total = Amount()
    #
    #     for index in range(12):
    #         month = f'{index + 1:02d}'
    #
    #         month_operations = self.get_month_account_operations(account, year, month)
    #
    #         if month_operations:
    #             last_day_month = get_number_of_days(month, year)
    #             month_balance = self.get_balance(account, f'{last_day_month}/{month}/{year}')
    #
    #             month_expenses = Amount()
    #             month_income = Amount()
    #             month_total = Amount()
    #             for operation in month_operations:
    #                 month_total.int += operation.amount.int
    #                 year_total.int += operation.amount.int
    #
    #                 if operation.amount.int <= 0:
    #                     month_expenses.int += operation.amount.int
    #                     year_expenses.int += operation.amount.int
    #
    #                 elif operation.amount.int > 0:
    #                     month_income.int += operation.amount.int
    #                     year_income.int += operation.amount.int
    #
    #         else:
    #             month_expenses = None
    #             month_income = None
    #             month_total = None
    #             month_balance = None
    #
    #         months_data[month] = {
    #             'expenses': month_expenses,
    #             'income': month_income,
    #             'total': month_total,
    #             'balance': month_balance,
    #         }
    #
    #     year_data = {
    #         'expenses': year_expenses,
    #         'income': year_income,
    #         'total': year_total,
    #         'balance': None,
    #     }
    #     return months_data, year_data

    def save(self, file):
        json_dump(self, file)

    @classmethod
    def open(cls, file):
        data = json_load(file)

        version = data.get('version', None)
        print('version', version)

        project = cls()
        project.set_data(data)

        return project

    @classmethod
    def new(cls):
        file = os.path.join(__dir__, 'data', 'new_project.json')
        project = cls.open(file)
        return project

    def import_credit_agricole_csv(self, file, account):
        with open(file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            lines = [x for x in list(csv_reader) if x]

        # operations
        operations = list()
        for line in lines:
            first_item = line[0]

            date_match = re.match(r'\d{2}/\d{2}/\d{4}', first_item)

            if date_match:
                date, label, amount_taken, amount_given, _ = line

                if amount_taken:
                    amount_text = f'-{amount_taken}'
                elif amount_given:
                    amount_text = amount_given
                else:
                    raise Exception(f'Neither amount taken nor amount taken found for line {line!r}')

                amount = Amount.from_string(amount_text)

                operation = Operation()
                operation.label = label.strip()
                operation.date = Date.from_string(date)
                operation.amount = amount
                operation.account = account

                operations.append(operation)

        self.operations += operations

    def get_categories(self, category_group):
        categories = list()

        for category in self.categories:
            category_parents = get_category_parents(category)

            if category_group in category_parents:
                categories.append(category)

        return categories


class Operation:

    def __init__(self):
        self.id = random_id()
        self.account = Account()
        self.label = str()
        self.amount = Amount()
        self.category = None
        self.date = Date()
        self.note = str()
        self.is_budget = False
        self.linked_operation = None

    def get_copy(self):
        operation = self.__class__()

        operation.id = self.id
        operation.account = self.account
        operation.label = self.label
        operation.amount = self.amount
        operation.category = self.category
        operation.date = self.date
        operation.note = self.note
        operation.is_budget = self.is_budget
        operation.linked_operation = self.linked_operation

        return operation

    def get_data(self):
        category = self.category
        if category is None:
            category_id = None
        else:
            category_id = category.id

        linked_operation = self.linked_operation
        if linked_operation is None:
            linked_operation_id = None
        else:
            linked_operation_id = linked_operation.id

        data = {
            'id': self.id,
            'date': str(self.date),
            'amount': self.amount,
            'label': self.label,
            'note': self.note,
            'account.id': self.account.id,
            'category.id': category_id,
            'linked_operation.id': linked_operation_id,
            'is_budget': self.is_budget,
        }
        return data


class Operations:

    def __init__(self):
        self.operations = list()

    def get_categories(self):
        categories = list()

        for operation in self.operations:
            category = operation.category

            if category not in categories:
                categories.append(category)

        return categories

    def get_year_total(self):
        total = Amount()
        for operation in self.operations:
            total += operation.amount
        return total

    def get_months(self):
        months = list()

        for operation in self.operations:
            month_name = operation.date.get_month_name()
            if month_name not in months:
                months.append(month_name)

        return months

    def get_month_total(self):
        month_map = {x: Amount() for x in Date.month_labels}

        for operation in self.operations:
            month_name = operation.date.get_month_name()
            month_map[month_name] += operation.amount

        return month_map

    def get_month_average(self):
        return self.get_year_total() / 12

    def get_operations_average(self):
        operations = self.operations
        if operations:
            return self.get_year_total() / len(operations)
        else:
            return Amount()


class BudgetOperation:

    def __init__(self):
        self.id = random_id()
        self.account = None
        self.label = str()
        self.amount = Amount()
        self.category = None
        self.start_date = None
        self.end_date = None
        self.note = str()
        self.is_budget = False
        self.repeat_mode = REPEAT_MODE.NO_REPETITION

    def get_data(self):
        data = {
            'id': self.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'amount': self.amount,
            'label': self.label,
            'note': self.note,
            'account.id': self.account.id,
            'category.id': self.category.getattr('id', None),
            'is_budget': self.is_budget,
            'repeat_mode': self.repeat_mode,
        }
        return data


class CategoryGroup:

    def __init__(self):
        self.id = random_id()
        self.name = str()
        self.emoji = str()
        self.color = 0, 0, 0
        self.parent_category_group = None

    def __str__(self):
        return self.name

    def get_data(self):
        parent_category_group = self.parent_category_group
        if parent_category_group:
            parent_category_group_id = parent_category_group.id
        else:
            parent_category_group_id = None

        data = {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'emoji': self.emoji,
            'parent_category_group.id': parent_category_group_id,
        }
        return data

    def get_pixmap(self, radius):
        pixmap = create_category_pixmap(
            text='',
            color=self.color,
            radius=radius
        )
        return pixmap

    def get_icon(self, radius):
        icon = create_category_icon(
            text=self.emoji,
            color=self.color,
            radius=radius
        )
        return icon

    def get_color(self):
        return self.color


class Category:

    default_color = [100, 100, 100]

    def __init__(self):
        self.id = random_id()
        self.name = str()
        self.emoji = str()
        self.category_group = None
        self.keywords = list()

    def __str__(self):
        return self.name

    def get_color(self):
        if self.category_group:
            return self.category_group.get_color()
        else:
            return self.default_color

    def get_data(self):
        data = {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji,
            'category_group.id': self.category_group.id,
            'keywords': self.keywords,
        }
        return data

    def get_pixmap(self, radius):
        pixmap = create_category_pixmap(
            text=self.emoji,
            color=self.get_color(),
            radius=radius
        )
        return pixmap

    def get_icon(self, radius):
        icon = create_category_icon(
            text=self.emoji,
            color=self.get_color(),
            radius=radius
        )
        return icon


class Date(QDate):

    month_labels = (
        'january',
        'february',
        'march',
        'april',
        'may',
        'june',
        'july',
        'august',
        'september',
        'october',
        'november',
        'december',
    )

    def __str__(self):
        return self.toString('dd/MM/yyyy')

    @classmethod
    def from_string(cls, s):
        return cls(datetime.strptime(s, '%d/%m/%Y'))

    def get_month_name(self):
        return self.toString('MMMM').lower()


# class Amount:
#
#     def __init__(self, int_=0, currency=CURRENCIES.EUR, seperator=','):
#         self.int = int_
#         self.currency = currency
#         self.seperator = seperator
#
#     def __str__(self):
#         return self.as_string()
#
#     def __int__(self):
#         return self.int
#
#     def as_string(self):
#         int_str = f'{self.int:03d}'
#         cents_str = int_str[-2:]
#         unit_str = int_str[:-2]
#
#         unit_str_formatted = ''
#         for index, character in enumerate(unit_str[::-1]):
#             if index % 3 == 0 and character != '-' and index != 0:
#                 unit_str_formatted += ' '
#             unit_str_formatted += character
#         unit_str_formatted = unit_str_formatted[::-1]
#
#         symbol = CURRENCIES.SYMBOLS.get(self.currency)
#         pattern = CURRENCIES.PATTERN.get(self.currency)
#
#         s = pattern.format(
#             unit=unit_str_formatted,
#             seperator=self.seperator,
#             cents=cents_str,
#             symbol=symbol,
#         )
#         return s
#
#     def as_unit(self):
#         return self.int / 100
#
#     @classmethod
#     def from_float(cls, float_, currency=CURRENCIES.EUR, seperator=','):
#         int_ = int(float_ * 100)
#         amount = cls(int_, currency, seperator)
#         return amount
#
#     @classmethod
#     def from_text(cls, text, currency=CURRENCIES.EUR, seperator=','):
#         # remove space characters
#         space_characters = '\u202f', '\xa0', ' '
#         for x in space_characters:
#             text = text.replace(x, '')
#
#         pattern = r'(-?)(\d*)' + seperator + r'(\d*)'
#
#         match = re.match(pattern, text)
#         if match:
#             sign, unit, cents = match.groups()
#
#             if sign is None:
#                 sign = ''
#
#             if unit is None:
#                 unit = '0'
#
#             if cents is None:
#                 cents = '00'
#             else:
#                 cents_int = int(cents)
#                 cents = f'{cents_int:02d}'
#
#             int_str = f'{sign}{unit}{cents}'
#             int_ = int(int_str)
#         else:
#             raise Exception(f'Text {text!r} does not match pattern {pattern!r}')
#
#         amount = cls(int_, currency, seperator)
#         return amount


class Amount:

    def __init__(self, cents:int=0):
        self.cents = cents
        self.symbol = '€'
        self.separator = ','
        self.units_separator = ' '
        self.pattern_with_cents = '{units}{separator}{cents:02d} {symbol}'
        self.pattern_without_cents = '{units} {symbol}'

    def __eq__(self, other):
        if isinstance(other, Amount):
            is_equal = self.cents == other.cents
        else:
            raise TypeError(f'{type(other)} type is not supported')

        return is_equal

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, Amount):
            is_greater_than = self.cents > other.cents
        else:
            raise TypeError(f'{type(other)} type is not supported')

        return is_greater_than

    def __lt__(self, other):
        return not self.__gt__(other)

    def __str__(self):
        return self.as_string_with_cents()

    def __add__(self, other):
        if isinstance(other, Amount):
            cents = self.cents + other.cents
        else:
            raise TypeError(f'{type(other)} type is not supported')

        new_amount = Amount(cents)
        return new_amount

    def __sub__(self, other):
        if isinstance(other, Amount):
            cents = self.cents - other.cents
        else:
            raise TypeError(f'{type(other)} type is not supported')

        new_amount = Amount(cents)
        return new_amount

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            cents = self.cents / other
            cents = int(cents)
        else:
            raise TypeError(f'{type(other)} type is not supported')

        new_amount = Amount(cents)
        return new_amount

    @classmethod
    def from_string(cls, s):
        amount = cls()

        space_characters = '\u202f', '\xa0', ' '
        for x in space_characters:
            s = s.replace(x, '') # remove space characters from string

        pattern = r'(-?)(\d*)' + amount.separator + r'(\d*)'

        match = re.match(pattern, s)
        if match:
            sign, units, cents = match.groups()

            if units:
                amount.cents += int(units) * 100

            if cents:
                amount.cents += int(cents)

            if sign is '-':
                amount.cents *= -1

        else:
            raise Exception(f'String {s!r} does not match pattern {pattern!r}')

        return amount

    @classmethod
    def from_units(cls, units):
        amount = cls()
        amount.cents = int(units * 100)
        return amount

    def as_units_and_cents(self):
        units, cents = divmod(abs(self.cents), 100)
        sign = '-' if self.cents < 0 else ''
        return sign, units, cents

    def as_units(self):
        return self.cents / 100

    @staticmethod
    def get_formatted_string_units(sign, units):
        units_str = ''

        count = 0
        for x in reversed(str(units)):
            if count == 3:
                count = 0
                units_str += ' '

            count += 1
            units_str += x


        units_str = sign + units_str[::-1]
        return units_str

    def as_string_with_cents(self):
        sign, units, cents = self.as_units_and_cents()
        units_str = self.get_formatted_string_units(sign, units)

        s = self.pattern_with_cents.format(
            units=units_str,
            cents=abs(cents),
            symbol=self.symbol,
            separator=self.separator,
        )
        return s

    def as_string_without_cents(self):
        sign, units, cents = self.as_units_and_cents()
        units_str = self.get_formatted_string_units(sign, units)

        s = self.pattern_without_cents.format(
            units=units_str,
            symbol=self.symbol,
        )
        return s


class Account:

    def __init__(self):
        self.id = random_id()
        self.name = str()
        self.number = str()

    def __str__(self):
        s = self.name
        if self.number:
            s += f' (n°{self.number})'
        return s

    def get_data(self):
        data = {
            'id': self.id,
            'name': self.name,
            'number': self.number,
        }
        return data


class Settings:

    def __init__(self):
        self.file = None
        self.recent_files = list()
        self.recent_files_limit = 10

    def reload(self):
        if not os.path.isfile(self.file):
            return

        data = json_load(self.file)

        self.recent_files = data['recent_files']

    def save(self):
        if self.file is None:
            raise Exception('No file registered')

        directory = os.path.dirname(self.file)
        if not os.path.exists(directory):
            os.makedirs(directory)

        json_dump(self, self.file)
        print(f'Settings saved at {self.file!r}')

    def add_current_file(self, file):
        if file not in self.recent_files:
            self.recent_files.append(file)

        if len(self.recent_files) > self.recent_files_limit:
            self.recent_files = self.recent_files[:self.recent_files_limit]

    def get_data(self):
        data = {
            'recent_files': self.recent_files,
            'recent_files_limit': self.recent_files_limit,
        }
        return data


def get_category_parents(item, data=None):
    if data is None:
        data = list()

    if isinstance(item, Category):
        parent = item.category_group
    elif isinstance(item, CategoryGroup):
        parent = item.parent_category_group
    else:
        raise Exception(f'Item type {type(item)} not supported')

    if parent:
        data.append(parent)
        get_category_parents(parent, data=data)

    return data
