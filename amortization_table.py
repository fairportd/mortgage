#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 15:42:13 2018

amortization_table.py
@author: david

# source for Mortgage class
# https://github.com/jbmohler/mortgage/blob/master/mortgage.py
"""
import decimal

MONTHS_IN_YEAR = 12
DOLLAR_QUANTIZE = decimal.Decimal('.01')

def dollar(f, round=decimal.ROUND_CEILING):
    '''
    Round the passed float to two decimal places
    '''
    if not isinstance(f, decimal.Decimal):
        f = decimal.Decimal(str(f)) # force f into decimal
    return f.quantize(DOLLAR_QUANTIZE, rounding=round)


class Mortgage:
    def __init__(self):
        self._amount = 200000
        self._rate = 0.05
        self._term = 30
        self._add_pmt = 0
        self._first_payment = '1/1/2018' # future update
        self._pay_freq = 'Monthly' # only option for now
        self._compound_freq = 'Monthly' # only option for now
        self._pay_type = 'End of Period' # only option for now

        
    def rate(self):
        return self._rate
    
    def monthly_growth(self):
        return 1.0 + self._rate / MONTHS_IN_YEAR
    
    def loan_years(self):
        return self._term
    
    def loan_months(self):
        return self._term * MONTHS_IN_YEAR
    
    def amount(self):
        return self._amount

    def additional_pmt(self):
        return self._add_pmt
    
    def monthly_payment(self):
        pmt = (self.amount() * self.rate()) / (MONTHS_IN_YEAR * (1.0-(1.0/self.monthly_growth()) ** self.loan_months()))
        return pmt

    def annual_payment(self):
        return self.monthly_payment() * MONTHS_IN_YEAR

    def total_payment(self):
        return self.monthly_payment() * self.loan_months()

    def monthly_payment_schedule(self):
        monthly = float(dollar(self.monthly_payment()))
        additional = float(dollar(self.additional_pmt()))
        balance = float(dollar(self.amount()))
        end_balance = float(dollar(balance))
        rate = float(decimal.Decimal(str(self.rate())).quantize(decimal.Decimal('.000001')))
        while True:
            interest_unrounded = balance * rate * float(decimal.Decimal(1) / MONTHS_IN_YEAR)
            interest = float(dollar(interest_unrounded, round=decimal.ROUND_HALF_UP))

            if monthly >= balance + interest:  # check if payment exceeds remaining due
                # last pmt
                additional = 0.0
                principal = float(dollar(end_balance))
                end_balance -= float(dollar(principal + additional))
                yield float(dollar(balance)), float(dollar((principal + interest))), additional, interest, principal, float(dollar(end_balance))
                break
            elif (monthly + additional) >= balance + interest: # check if pmt + add exceeds remaining due
                principal = float(dollar(monthly - interest))
                additional = (balance + interest) - monthly
                end_balance -= float(dollar(principal + additional))
                yield float(dollar(balance)), float(dollar((principal + interest))), additional, interest, principal, float(dollar(end_balance))
                break

            principal = float(dollar(monthly - interest))
            end_balance -= (principal + additional)
            yield float(dollar(balance)), monthly, additional, interest, principal, float(dollar(end_balance))
            balance = end_balance

    def print_monthly_payment_schedule(self):
        for index, payment in enumerate(self.monthly_payment_schedule()):
            print(index + 1, payment[0], payment[1], payment[2], payment[3], payment[4], payment[5])

    def main(self):
        print(self.rate())
        print(self.monthly_growth())
        print(self.loan_years())
        print(self.loan_months())
        print(dollar(self.amount()))
        print(dollar(self.monthly_payment()))
        print(dollar(self.annual_payment()))
        print(dollar(self.total_payment()))
        self.print_monthly_payment_schedule()


def test_Mortgage():
    test = Mortgage()
    test.main()
    
if __name__ == '__main__':
    test_Mortgage()