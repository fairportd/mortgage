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
        return pmt

    def annual_payment(self):
        """Returns the total payments during the year for the loan"""
        return self.monthly_payment() * self.MONTHS_IN_YEAR

    def total_payment(self):
        """Returns the total cost of the loan"""
        return self.monthly_payment() * self.loan_months()

    def piti(self):
        """Returns the monthly PITI"""
        return self.monthly_payment() + self.monthly_taxes() + self.monthly_insurance()

    def monthly_payment_schedule(self):
        """Yields amortization schedule for the given loan"""
        monthly = float(self.dollar(self.monthly_payment()))
        additional = float(self.dollar(self.additional_pmt()))
        balance = float(self.dollar(self.amount()))
        end_balance = float(self.dollar(balance))
        rate = float(decimal.Decimal(str(self.rate())).quantize(decimal.Decimal('.000001')))
        while True:
            interest_unrounded = balance * rate * float(decimal.Decimal(1) / self.MONTHS_IN_YEAR)
            interest = float(self.dollar(interest_unrounded, round=decimal.ROUND_HALF_UP))

            if monthly >= balance + interest:  # check if payment exceeds remaining due
                # last pmt
                additional = 0.0
                principal = float(self.dollar(end_balance))
                end_balance -= float(self.dollar(principal + additional))
                yield float(self.dollar(balance)), float(self.dollar((principal + interest))), additional, interest, principal, float(self.dollar(end_balance))
                break
            elif (monthly + additional) >= balance + interest: # check if pmt + add exceeds remaining due
                principal = float(self.dollar(monthly - interest))
                additional = (balance + interest) - monthly
                end_balance -= float(self.dollar(principal + additional))
                yield float(self.dollar(balance)), float(self.dollar((principal + interest))), additional, interest, principal, float(self.dollar(end_balance))
                break

            principal = float(self.dollar(monthly - interest))
            end_balance -= (principal + additional)
            yield float(self.dollar(balance)), monthly, additional, interest, principal, float(self.dollar(end_balance))
            balance = end_balance

    def print_monthly_payment_schedule(self):
        """Prints out the monthly payment schedule"""
        for index, payment in enumerate(self.monthly_payment_schedule()):
            print(index + 1, payment[0], payment[1], payment[2], payment[3], payment[4], payment[5])

    def amortization_dict(self):
        """Returns a dictionary with the payment schedule"""
        amort_dict = {}
        for index, payment in enumerate(self.monthly_payment_schedule()):
            amort_dict[index + 1] = [payment[0], payment[1], payment[2], payment[3], payment[4], payment[5]]
        return amort_dict

    def amortization_table(self):
        """Returns a dataframe with the amortization table in it"""
        names = ['Beg. Balance', 'Monthly Payment', 'Additional Payment',
                 'Interest', 'Principal', 'End Balance']
        df = pd.DataFrame.from_dict(self.amortization_dict(), orient='index')
        df.columns = names
        monthly_inflation = self._inflation / 12
        if sum(df['Additional Payment'].values) != 0: #check if there are additional payments
            df['Total Payment'] = df['Monthly Payment'] + df['Additional Payment']
            self._total_combined_payments = sum(df['Total Payment'].values)
            self._payment_months = df.shape[0]
            # calc PV of original terms
            arr_months = np.array(range(self.loan_years() * 12))
            arr_m_payment = np.array(self.monthly_payment())
            list_inflation = []
            for month in arr_months:
                list_inflation.append((1 + monthly_inflation) ** month)
            arr_inflation = np.array(list_inflation)
            arr_pv_payments = np.divide(arr_m_payment, arr_inflation)
            self._pv_payments = sum(arr_pv_payments)

            # add combined PV factor
            arr_c_months = np.array(range(self._payment_months))
            list_c_inflation = []
            for month in arr_c_months:
                list_c_inflation.append((1 + monthly_inflation) ** month)
            arr_c_inflation = np.array(list_c_inflation)
            df['PV of Combined Payment'] = (df['Monthly Payment'] + df['Additional Payment']) / arr_c_inflation
            self._pv_combined_payments = sum(df['PV of Combined Payment'].values)
            return df
        else:
            # add PV factor
            arr_months = np.array(range(self.loan_months()))
            list_inflation = []
            for month in arr_months:
                list_inflation.append((1 + monthly_inflation) ** month)
            arr_inflation = np.array(list_inflation)
            df['PV of Payment'] = df['Monthly Payment'] / arr_inflation
            self._pv_payments = sum(df['PV of Payment'].values)
            return df

    def amort_table_to_csv(self):
        """Outputs the amortization table to a .csv file"""
        now = dt.datetime.today()
        date = str(now.year) + str(now.month) + str(now.day) + '_' + str(now.hour) + str(now.minute)
        self.amortization_table().to_csv('/home/david/git_repos/mortgage/output/' + date + '.csv')

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
        if self._total_combined_payments != 0:
            new_monthly = self._total_combined_payments / self._payment_months
            new_annual = self._total_combined_payments / self._payment_months * 12
            change_months = self._payment_months - self.loan_months()
            change_monthly = new_monthly - self.monthly_payment()
            change_annual = new_annual - self.annual_payment()
            change_total = self._total_combined_payments - self.total_payment()
            change_pv = self._pv_combined_payments - self._pv_payments
            print('Effect of paying an additional ${0:,.0f} each month:'.format(self.additional_pmt()))
            print("")
            print('{0:>30s}: {1:>12.1f}     {2:>10.1f} years'.format('Term (years)', self._payment_months/12.0, change_months/12.0))
            print('{0:>30s}: ${1:>11,.0f}    ${2:>10,.0f}'.format('Monthly Mortgage Payment', new_monthly, change_monthly))
            print('{0:>30s}: ${1:>11,.0f}    ${2:>10,.0f}'.format('Annual Mortgage Payment', new_annual, change_annual))
            print('{0:>30s}: ${1:>11,.0f}    ${2:>10,.0f}'.format('Total Mortgage Payment', self._total_combined_payments, change_total))
            print('{0:>30s}: ${1:>11,.0f}    ${2:>10,.0f}'.format('PV of Combined Payments', self._pv_combined_payments, change_pv))
            print('')
            print('{0:>30s}: ${1:>11,.0f}'.format('Annual Taxes', self.taxes()))
            print('{0:>30s}: ${1:>11,.0f}'.format('Annual Insurance', self.insurance()))
            print('')
            print('{0:>30s}: ${1:>11,.0f}'.format('Monthly PITI', new_monthly + self.monthly_taxes() + self.monthly_insurance()))
            print('-' * 75)
        # re-reference totals to include additional payments (new function needed)
        # pv of payments

    def main(self, csv=False):
        """Generates an amortization table and prints the summary"""
        self.amortization_table() # print [0] for the table # need to run to get summary stats
        if csv == True:
            self.amort_table_to_csv() #optional, use if want to export
        self.print_summary()


def main():
    parser = argparse.ArgumentParser(description='Mortgage Tools')
    parser.add_argument('-r', '--interest', default=5, dest='interest')
    parser.add_argument('-y', '--loan-years', default=30, dest='years')
    parser.add_argument('-p', '--price', default=250000, dest='price')
    parser.add_argument('-a', '--amount', default=200000, dest='amount')
    parser.add_argument('-t', '--taxes', default=7000, dest ='taxes')
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
