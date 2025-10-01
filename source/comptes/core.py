import csv
import json
from datetime import datetime, timedelta
import re
import os

from .utils import get_number_of_days, json_dumps, random_id, split_date, create_category_pixmap, create_category_icon


__dir__ = os.path.dirname(__file__)

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

class Project:

    def __init__(self):
        self.accounts = list()
        self.operations = list()
        self.categories = list()
        self.category_groups = list()

        self.version = '1'

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
            amount = Amount.from_text(amount_txt)

            category_id = operation_data['category.id']
            category = categories_map.get(category_id)

            operation_id = operation_data.get('id')

            operation = Operation()
            if operation_id:
                operation.id = operation_id
            operation.account = account
            operation.label = operation_data['label']
            operation.amount = amount
            operation.category = category
            operation.date = operation_data['date']
            operation.note = operation_data['note']

            operations.append(operation)

        self.accounts = list(accounts_map.values())
        self.operations = operations
        self.category_groups = list(category_groups_map.values())
        self.categories = list(categories_map.values())

    def get_years(self):
        years = list()

        for operation in self.operations:
            operation_day, operation_year, operation_year = operation.date.split('/')

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
            operation_date = split_date(account_operation.date)

            if operation_date['year'] == year:
                year_account_operation.append(account_operation)

        return year_account_operation

    def get_month_account_operations(self, account, year, month):
        year_account_operations = self.get_year_account_operations(account, year)

        month_account_operation = list()
        for account_operation in year_account_operations:
            operation_date = split_date(account_operation.date)

            if operation_date['month'] == month:
                month_account_operation.append(account_operation)

        return month_account_operation

    def get_balance(self, account, date=None):
        balance = Amount()

        if date is not None:
            date = datetime.strptime(date, "%d/%m/%Y")

        account_operations = self.get_account_operations(account)
        for operation in account_operations:
            operation_date = datetime.strptime(operation.date, "%d/%m/%Y")

            if date is None or operation_date <= date:
                balance.int += operation.amount.int

        return balance

    def get_year_summary(self, account, year):
        months_data = dict()

        year_expenses = Amount()
        year_income = Amount()
        year_total = Amount()

        for index in range(12):
            month = f'{index + 1:02d}'

            month_operations = self.get_month_account_operations(account, year, month)

            if month_operations:
                last_day_month = get_number_of_days(month, year)
                month_balance = self.get_balance(account, f'{last_day_month}/{month}/{year}')

                month_expenses = Amount()
                month_income = Amount()
                month_total = Amount()
                for operation in month_operations:
                    month_total.int += operation.amount.int
                    year_total.int += operation.amount.int

                    if operation.amount.int <= 0:
                        month_expenses.int += operation.amount.int
                        year_expenses.int += operation.amount.int

                    elif operation.amount.int > 0:
                        month_income.int += operation.amount.int
                        year_income.int += operation.amount.int

            else:
                month_expenses = None
                month_income = None
                month_total = None
                month_balance = None

            months_data[month] = {
                'expenses': month_expenses,
                'income': month_income,
                'total': month_total,
                'balance': month_balance,
            }

        year_data = {
            'expenses': year_expenses,
            'income': year_income,
            'total': year_total,
            'balance': None,
        }
        return months_data, year_data

    def save(self, file):
        s = json_dumps(self)

        with open(file, 'w', encoding='utf-8') as f:
            f.write(s)

    @classmethod
    def open(cls, file):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        version = data.get('version', None)
        print('version', version)

        project = cls()
        project.set_data(data)

        return project

    @classmethod
    def new(cls):
        file = os.path.join(__dir__, 'data', 'new_project.json')
        print(file)
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

                amount = Amount.from_text(amount_text)

                operation = Operation()
                operation.label = label.strip()
                operation.date = date
                operation.amount = amount
                operation.account = account

                operations.append(operation)

        self.operations += operations

class Date:

    def __init__(self):
        self.day = 1
        self.month = 1
        self.year = 2025
        self.pattern = '{day:02d}/{month:02d}/{year:04d}'

    def __str__(self):
        s = self.pattern.format(
            day=self.day,
            month=self.month,
            year=self.year,
        )
        return s

    def get_day(self):
        pass

    def get_month(self):
        pass

    def get_year(self):
        pass

    @classmethod
    def from_str(cls, str_):
        day_str, month_str, year_str = str_.split('/')

        date = cls()
        date.day = int(day_str)
        date.month = int(month_str)
        date.year = int(year_str)

        return date

class CategoryGroup:

    def __init__(self):
        self.id = random_id()
        self.name = str()
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
            text='',
            color=self.color,
            radius=radius
        )
        return icon

class Category:

    def __init__(self):
        self.id = random_id()
        self.name = str()
        self.emoji = str()
        self.category_group = None
        self.keywords = list()

    def __str__(self):
        return self.name

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
            color=self.category_group.color,
            radius=radius
        )
        return pixmap

    def get_icon(self, radius):
        icon = create_category_icon(
            text=self.emoji,
            color=self.category_group.color,
            radius=radius
        )
        return icon

class Amount:

    def __init__(self, int_=0, currency=CURRENCIES.EUR, seperator=','):
        self.int = int_
        self.currency = currency
        self.seperator = seperator

    def __str__(self):
        int_str = f'{self.int:03d}'
        cents_str = int_str[-2:]
        unit_str = int_str[:-2]

        unit_str_formatted = ''
        for index, character in enumerate(unit_str[::-1]):
            if index % 3 == 0 and character != '-' and index != 0:
                unit_str_formatted += ' '
            unit_str_formatted += character
        unit_str_formatted = unit_str_formatted[::-1]

        symbol = CURRENCIES.SYMBOLS.get(self.currency)
        pattern = CURRENCIES.PATTERN.get(self.currency)

        s = pattern.format(
            unit=unit_str_formatted,
            seperator=self.seperator,
            cents=cents_str,
            symbol=symbol,
        )
        return s

    def __int__(self):
        return self.int

    def as_unit(self):
        return self.int / 100

    @classmethod
    def from_float(cls, float_, currency=CURRENCIES.EUR, seperator=','):
        int_ = int(float_ * 100)
        amount = cls(int_, currency, seperator)
        return amount

    @classmethod
    def from_text(cls, text, currency=CURRENCIES.EUR, seperator=','):
        # remove space characters
        space_characters = '\u202f', '\xa0', ' '
        for x in space_characters:
            text = text.replace(x, '')

        pattern = r'(-?)(\d*)' + seperator + r'(\d*)'

        match = re.match(pattern, text)
        if match:
            sign, unit, cents = match.groups()

            if sign is None:
                sign = ''

            if unit is None:
                unit = '0'

            if cents is None:
                cents = '00'
            else:
                cents_int = int(cents)
                cents = f'{cents_int:02d}'

            int_str = f'{sign}{unit}{cents}'
            int_ = int(int_str)
        else:
            raise Exception(f'Text {text!r} does not match pattern {pattern!r}')

        amount = cls(int_, currency, seperator)
        return amount

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

class Operation:

    def __init__(self):
        self.id = random_id()
        self.account = Account()
        self.label = str()
        self.amount = Amount()
        self.category = None
        self.date = str()
        self.note = str()
        self.ticked = True
        self.linked_operation = None

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
            'date': self.date,
            'amount': self.amount,
            'label': self.label,
            'note': self.note,
            'account.id': self.account.id,
            'category.id': category_id,
            'linked_operation.id': linked_operation_id,
        }
        return data
