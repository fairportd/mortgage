#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 15:42:13 2018

amortization_table.py
@author: david

# source for most of Mortgage class' basic functions
# https://github.com/jbmohler/mortgage/blob/master/mortgage.py
"""
import argparse
import decimal
import os
import pandas as pd
import numpy as np
import datetime as dt

class Mortgage:
    """Contains properties of a mortgage given user inputs
        Args:
            _amount (float): Loan amount
            _price(float): Price of house
            _rate (float): Interest rate as a decimal i.e. 0.05
            _term (int): Length of the loan in years
            _taxes (float): Annual tax bill
            _insurance (float): Annual insurance bill
            _additional (float): Extra payment in each month that goes toward principal
            
    """
    def __init__(self, amount, price, rate, term, taxes, insurance, additional=0):
        """init function for Mortgage class"""
        self._amount = amount
        self._price = price
        self._rate = rate
        self._term = term
        self._taxes = taxes
        self._insurance = insurance
        self._add_pmt = additional
        self._total_combined_payments = float(0)
        self._payment_months = float(0)
        self._inflation = float(0.03)
        self._pv_payments = float(0)
        self._pv_combined_payments = float(0)
        self._per = np.arange(term*12) + 1 # array of numbered months
        self._first_payment = '1/1/2018' # future update
        self._pay_freq = 'Monthly' # only option for now
        self._compound_freq = 'Monthly' # only option for now
        self._pay_type = 'End of Period' # only option for now
        self.MONTHS_IN_YEAR = 12
        self.DOLLAR_QUANTIZE = decimal.Decimal('.01')


    def dollar(self, f, round=decimal.ROUND_CEILING):
        """Returns the passed float rounded to two decimal places"""
        if not isinstance(f, decimal.Decimal):
            f = decimal.Decimal(str(f))  # force f into decimal
        return f.quantize(self.DOLLAR_QUANTIZE, rounding=round)

    def rate(self):
        """Returns the interest rate of the loan"""
        return self._rate
    
    def monthly_growth(self):
        """Returns the monthly interest accrual of the loan"""
        return 1.0 + self._rate / self.MONTHS_IN_YEAR
    
    def loan_years(self):
        """Returns the term, in years, of the loan"""
        return self._term
    
    def loan_months(self):
        """Returns the term, in months, of the loan"""
        return self._term * self.MONTHS_IN_YEAR

    def price(self):
        """Returns the house price"""
        return self._price
    
    def amount(self):
        """Returns the amount of the loan"""
        return self._amount

    def additional_pmt(self):
        """Returns the additional monthly principal payment"""
        return self._add_pmt

    def taxes(self):
        """Returns the annual taxes due"""
        return self._taxes

    def monthly_taxes(self):
        """Returns the monthly taxes due"""
        return self._taxes / self.MONTHS_IN_YEAR

    def insurance(self):
        """Returns the annual insurance amount due"""
        return self._insurance * self.price()

    def monthly_insurance(self):
        """Returns the monthly insurance due"""
        return self.insurance() / self.MONTHS_IN_YEAR
    
    def monthly_payment(self):
        """Returns the monthly payment for the loan"""
        pmt = np.pmt(self.rate()/self.MONTHS_IN_YEAR, self.loan_months(), -self.amount())
        return np.round(pmt, 2)

    def interest_pmt(self):
        """Returns array with the interest payment for each month"""
        ipmt = np.ipmt(self.rate()/self.MONTHS_IN_YEAR, self._per, self.loan_months(),-self.amount())
        return np.round(ipmt, 2)

    def principal_pmt(self):
        """Returns array with the principal payment for each month"""
        ppmt = np.ppmt(self.rate()/self.MONTHS_IN_YEAR, self._per, self.loan_months(),-self.amount())
        return np.round(ppmt, 2)

    def beg_balance(self):
        """Returns array with the beginning balance for each month"""
        beg_balance = []
        balance = self.amount()
        for i in range(self.loan_months()):
            beg_balance.append(balance)
            balance -= self.principal_pmt()[i]
        arr_balance = np.array(beg_balance)
        return np.round(arr_balance, 2)

    def end_balance(self):
        """Returns array with the ending balance for each month"""
        end_balance = self.beg_balance() - self.principal_pmt()
        return end_balance

    def pv_factor(self):
        """Returns array with PV factors for each month"""
        list_inflation = []
        for month in range(self.loan_months()):
            list_inflation.append((1 + self._inflation/12) ** month)
        arr_inflation = np.array(list_inflation)
        return arr_inflation

    def annual_payment(self):
        """Returns the total payments during the year for the loan"""
        return self.monthly_payment() * self.MONTHS_IN_YEAR

    def total_payment(self):
        """Returns the total cost of the loan"""
        return self.monthly_payment() * self.loan_months()

    def total_interest(self):
        """Returns the total interest paid over the course of the loan"""
        return np.sum(self.interest_pmt())

    def piti(self):
        """Returns the monthly PITI"""
        return self.monthly_payment() + self.monthly_taxes() + self.monthly_insurance()

    def amortization_table2(self):
        """Returns a dataframe with the amortization table in it"""
        index = self._per - 1
        df = pd.DataFrame(self._per)
        df.columns = ['Month']
        df['Beg. Balance'] = self.beg_balance()
        df['Monthly Payment'] = self.monthly_payment()
        df['Interest'] = self.interest_pmt()
        df['Principal'] = self.principal_pmt()
        df['End Balance'] = self.end_balance()
        df['PV of Combined'] = df['Monthly Payment'] / self.pv_factor()

        # summary stats
        self._total_combined_payments = sum(df['Monthly Payment'].values)
        self._pv_payments = sum(df['PV of Combined'].values)

        return df   

    def amort_table_to_csv(self):
        """Outputs the amortization table to a .csv file"""
        now = dt.datetime.today()
        date = str(now.year) + str(now.month) + str(now.day) + '_' + str(now.hour) + str(now.minute)
        self.amortization_table2().to_csv('/home/david/git_repos/mortgage/output/' + date + '.csv')

    def print_summary(self):
        """Prints out a summary of the given mortgage"""
        print('Mortgage Summary')
        print('-' * 75)
        print('{0:>30s}: ${1:>11,.0f}'.format('House Price', self.price()))
        print('')
        print('{0:>30s}: ${1:>11,.0f}'.format('Loan Amount', self.amount()))
        print('{0:>30s}: {1:>12.0f}'.format('Term (years)', self.loan_years()))
        print('{0:>30s}: {1:>12.2f}%'.format('Rate', self.rate()*100))
        print('{0:>30s}: ${1:>11,.0f}'.format('Monthly Mortgage Payment', self.monthly_payment()))
        print('{0:>30s}: ${1:>11,.0f}'.format('Annual Mortgage Payment', self.annual_payment()))
        print('{0:>30s}: ${1:>11,.0f}'.format('Total Mortgage Payment', self.total_payment()))
        print('{0:>30s}: ${1:>11,.0f}'.format('Total PV of Payments', self._pv_payments))
        print('')
        print('{0:>30s}: ${1:>11,.0f}'.format('Annual Taxes', self.taxes()))
        print('{0:>30s}: ${1:>11,.0f}'.format('Annual Insurance', self.insurance()))
        print('')
        print('{0:>30s}: ${1:>11,.0f}'.format('Monthly PITI', self.piti()))
        print('-' * 75)
        # re-reference totals to include additional payments (new function needed)
        # pv of payments

    def main(self, csv=False):
        """Generates an amortization table and prints the summary"""
        print(self.amortization_table2()) # print [0] for the table # need to run to get summary stats
        self.amortization_table2()
        if csv == True:
            self.amort_table_to_csv() #optional, use if want to export
        self.print_summary()
        
def main():
    parser = argparse.ArgumentParser(description='Mortgage Tools')
    parser.add_argument('-r', '--interest', default=4.25, dest='interest')
    parser.add_argument('-y', '--loan-years', default=30, dest='years')
    parser.add_argument('-p', '--price', default=205000, dest='price')
    parser.add_argument('-a', '--amount', default=164000, dest='amount')
    parser.add_argument('-t', '--taxes', default=7300, dest ='taxes')
    parser.add_argument('-i', '--insurance', default=0.0035, dest='insurance')
    parser.add_argument('-e', '--extra payment', default=None, dest='extra')
    args = parser.parse_args() 

    if args.extra:
        m = Mortgage(float(args.amount), float(args.price), float(args.interest) / 100.0, int(args.years), float(args.taxes), float(args.insurance), float(args.extra))
    else:
        m = Mortgage(float(args.amount), float(args.price), float(args.interest) / 100.0, int(args.years), float(args.taxes), float(args.insurance))
    m.main()
    
if __name__ == '__main__':
    main()
