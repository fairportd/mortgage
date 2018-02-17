#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 15:42:13 2018

amortization_table.py
@author: david

# source for most of Mortgage class
# https://github.com/jbmohler/mortgage/blob/master/mortgage.py
"""

MONTHS_IN_YEAR = 12

class Mortgage:
    def __init__(self):
        self._amount = 100000.0
        self._rate = 0.05
        self._term = 30.0
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
        return self._term * 12
    
    def amount(self):
        return self._amount
    
    def monthly_payment(self):
        pmt = (self.amount() * self.rate()) / (MONTHS_IN_YEAR * (1.0-(1.0/self.monthly_growth()) ** self.loan_months()))
        return pmt
        
    def main(self):
        print(self.rate())
        print(self.monthly_growth())
        print(self.loan_years())
        print(self.loan_months())
        print(self.amount())
        print(self.monthly_payment())
 
        
        
def test():
    test = Mortgage()
    test.main()
    
if __name__ == '__main__':
    test()