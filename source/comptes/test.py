from .core import Amount

def run_test():
    amount2_test()

def amount2_test():

    amountA = Amount(15000)
    amountB = Amount(20000)
    amountC = amountA - amountB
    amountD = amountA + amountB
    amountE = Amount(1234567890)
    amountF = Amount(-1)

    print('amountA', amountA, '150 €')
    print('amountB', amountB, '200 €')
    print('amountC', amountC, 'A - B')
    print('amountD', amountD, 'A + B')
    print('amountE', amountE, '12 345 678,90 €')
    print('amountF', amountF, '-0,01 €')

    print('amountA', amountA.as_units_and_cents())
    print('amountB', amountB.as_units_and_cents())
    print('amountC', amountC.as_units_and_cents())
    print('amountD', amountD.as_units_and_cents())

    print('amountA', amountA.as_string_without_cents())
    print('amountB', amountB.as_string_without_cents())
    print('amountC', amountC.as_string_without_cents())
    print('amountD', amountD.as_string_without_cents())
