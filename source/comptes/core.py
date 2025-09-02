import csv
import re

class CURRENCIES:
    EUR = 0
    USD = 1

    EUR_SYMBOL = '€'
    USD_SYMBOL = '$'

    SYMBOLS = {
        EUR: EUR_SYMBOL,
        USD: USD_SYMBOL,
    }

class Amount:

    def __init__(self, in_cents=0, currency=CURRENCIES.EUR, seperator=','):
        self.in_cents = in_cents
        self.currency = currency
        self.seperator = seperator

    def __int__(self):
        return self.in_cents

    def __str__(self):
        in_cents_str = f'{self.in_cents:03d}'
        cents_str = in_cents_str[-2:]
        money_str = in_cents_str[:-2]

        currency_symbol = CURRENCIES.SYMBOLS.get(self.currency)

        s = f'{money_str}{self.seperator}{cents_str} {currency_symbol}'
        return s

    def __add__(self, other):
        return self.operation(other, '+')

    def __sub__(self, other):
        return self.operation(other, '-')

    def __mul__(self, other):
        return self.operation(other, '*')

    def __truediv__(self, other):
        return self.operation(other, '/')

    def operation(self, other, operator):
        amount = self.__class__()
        amount.in_cents = eval(f'self.in_cents {operator} other.in_cents')
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
            sign, money, cents = match.groups()

            if sign is None:
                sign = ''

            if money is None:
                money = '0'

            if cents is None:
                cents = '00'
            else:
                cents_int = int(cents)
                cents = f'{cents_int:02d}'

            in_cents_str = f'{sign}{money}{cents}'
            in_cents = int(in_cents_str)
        else:
            raise Exception(f'Text {text!r} does not match pattern {pattern!r}')

        amount = cls(in_cents, currency, seperator)
        return amount

class Operations:
    def __init__(self):
        self.operations = list()

    def get_account_operations(self, account):
        account_operations = Operations()

        for operation in self.operations:
            if operation.account != account:
                continue

            account_operations.operations.append(operation)

        return account_operations

    def get_accounts(self):
        accounts = list()

        for operation in self.operations:
            account = operation.account

            if account not in accounts:
                accounts.append(account)

        return accounts

    def get_balance(self):
        balance = 0

        for operation in self.operations:
            balance += int(operation.amount)

        amount = Amount()
        amount.in_cents = balance

        return amount

    @classmethod
    def from_ugly_csv(cls, file):
        with open(file, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)

            next(csv_reader)
            all_values = list(csv_reader)

        operations = cls()
        for values in all_values:
            operation = Operation()
            operation.label = values[0]
            operation.date = values[1]

            amount = Amount.from_text(values[3])
            operation.amount = amount

            operation.account = values[4]
            operation.category = values[6]
            operation.type = values[7]
            operation.note = values[8]

            operations.operations.append(operation)

        return operations

    @classmethod
    def from_credit_agricole_csv(cls, file):
        operations = cls()

        with open(file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')

            lines = list(csv_reader)

        account = None

        for line in lines:
            if not line:
                continue

            first_item = line[0]
            if first_item.startswith(('Compte', 'Livret')):
                account = first_item
                continue

            date_match = re.match(r'\d{2}/\d{2}/\d{4}', first_item)

            if date_match:
                date, label, amount_taken, amount_given, _ = line

                if amount_taken:
                    amount = Amount.from_text(f'-{amount_taken}')
                elif amount_given:
                    amount = Amount.from_text(amount_given)
                else:
                    raise Exception(f'Neither amount taken nor amount taken found for line {line!r}')

                operation = Operation()
                operation.label = label.strip()
                operation.date = date
                operation.amount = amount
                operation.account = account

                operations.operations.append(operation)

        return operations

    @classmethod
    def from_project_csv(cls, file):
        operations = cls()
        return operations

class Operation:
    def __init__(self):
        self.account = None

        self.label = None
        self.amount = None
        self.category = None
        self.date = None

        self.type = None
        self.note = None

    def get_data(self):
        data = dict()

        data['account'] = self.account

        data['label'] = self.label

        data['amount'] = self.amount
        data['category'] = self.category
        data['date'] = self.date

        data['type'] = self.type
        data['note'] = self.note

        return data

def get_one_liner_text(text):
    text = text.replace('\n', ' ')
    text = re.sub(' +', ' ', text)
    return text
