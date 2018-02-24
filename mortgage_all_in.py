#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
mortgage_all_in.py

Estimate the all-in costs of a mortgage (PITI) as a % of sale price.

'''
import numpy as np



def rate_table(rates):
    for rate in rates:
            all_in_m = (np.pmt(rate / 100 / 12, 360, -100000) * 12) / 100000
            tandi = 0.043 # assumes 3.3% tax and 1% insurance
            total = all_in_m + tandi
            print('{0:.2f}%  {1:.2f}%  {2:.2f}x  {3:.2f}%  {4:.2f}x'.format(rate, all_in_m*100, all_in_m*100 / (rate), (total)*100, (total)*100 / (rate) ))

# calc current rent equivelant in terms of house price

def rent_eqv(rent):
    a_rent = rent * 12 # annualize rent payments
    cap_rate = .1003 # all in PITI % at 4% for 30, with 3% in T & I
    eqv_loan = a_rent / cap_rate # calc pv of loan with total payments equal to rent payment
    price = eqv_loan / 0.80 # assume 20% down payment (80% LTV)
    print("You're current rent of ${0:,.0f} is equivelant to PITI payments on a ${1:,.0f} house.".format(rent, price))

def afford(income, dti):
    a_pmts = income * dti/100
    cap_rate = .1003 # all in rate at 4% for 30 with 3.6% fairport taxes and 1% insurance
    value = a_pmts / cap_rate
    print('With an income of ${0:,.0f} you can afford a ${1:,.0f} house with a {2:.0f}% DTI ratio'.format(income, value, dti))


rates = [4.0, 4.5, 5.0, 5.5, 6.0]
rents = [800, 1000, 1200, 1400, 1600]
incomes = [60000, 65000, 70000]
rate_table(rates)
for rent in rents:
    rent_eqv(rent)

for income in incomes:
    afford(income, 20)

actual_rent = 1035
rent_eqv(actual_rent)