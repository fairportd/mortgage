#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 15:42:13 2018

amortization_table.py
@author: david

# source for most of Mortgage class
# https://github.com/jbmohler/mortgage/blob/master/mortgage.py
"""
import decimal
import pandas as pd
import numpy as np
import datetime as dt

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
        self._amount = 160000
        self._rate = float(0.05)
        self._term = 30
        self._add_pmt = 1000
        self._total_combined_payments = float(0)
        self._payment_months = float(0)
        self._inflation = float(0.03)
        self._pv_payments = float(0)
        self._pv_combined_payments = float(0)
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

    def amortization_dict(self):
        amort_dict = {}
        for index, payment in enumerate(self.monthly_payment_schedule()):
            amort_dict[index + 1] = [payment[0], payment[1], payment[2], payment[3], payment[4], payment[5]]
        return amort_dict

    def amortization_table(self):
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
        now = dt.datetime.today()
        date = str(now.year) + str(now.month) + str(now.day) + '_' + str(now.hour) + str(now.minute)
        self.amortization_table().to_csv('/home/david/git_repos/mortgage/output/' + date + '.csv')

    def print_summary(self):
        '''
        Print out summary of information on the mortgage.
        '''
        print('Mortgage Summary')
        print('-' * 75)
        print('{0:>30s}: ${1:>11,.0f}'.format('Loan Amount', self.amount()))
        print('{0:>30s}: {1:>12.0f}'.format('Term (years)', self.loan_years()))
        print('{0:>30s}: {1:>12.2f}%'.format('Rate', self.rate()*100))
        print('{0:>30s}: ${1:>11,.0f}'.format('Monthly Mortgage Payment', self.monthly_payment()))
        print('{0:>30s}: ${1:>11,.0f}'.format('Annual Mortgage Payment', self.annual_payment()))
        print('{0:>30s}: ${1:>11,.0f}'.format('Total Mortgage Payment', self.total_payment()))
        print('{0:>30s}: ${1:>11,.0f}'.format('Total PV of Payments', self._pv_payments))
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
        # re-reference totals to include additional payments (new function needed)
        # pv of payments

    def main(self):
        # self.print_monthly_payment_schedule()
        self.amortization_table() # print [0] for the table
        # self.amort_table_to_csv()
        self.print_summary()


def test_Mortgage():
    test = Mortgage()
    test.main()
    
if __name__ == '__main__':
    test_Mortgage()