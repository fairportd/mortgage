#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
mortgage_all_in.py

Estimate the all-in costs of a mortgage (PITI) as a % of sale price.

'''
import numpy as np
import taxes as tax

def rate_table(rates):
    t = tax.get_town_tax_rate()
    i = 1000 / 200000
    tandi = t + i
    for rate in rates:
            all_in_m = (np.pmt(rate / 100 / 12, 360, -200000) * 12) / 200000
            total = all_in_m + tandi
            print('{0:.2f}%  {1:.2f}%  {2:.2f}x  {3:.2f}%  {4:.2f}x'.format(rate, all_in_m*100, all_in_m*100 / (rate), (total)*100, (total)*100 / (rate) ))

# calc current rent equivelant in terms of house price

def rent_eqv(rent):
    a_rent = rent * 12 # annualize rent payments
    cap_rate = .0956 # all in PITI % at 4% for 30, with 3.83% in T & I
    eqv_loan = a_rent / cap_rate # calc pv of loan with total payments equal to rent payment
    price = eqv_loan / 0.80 # assume 20% down payment (80% LTV)
    print("You're current rent of ${0:,.0f} is equivelant to PITI payments on a ${1:,.0f} house.".format(rent, price))

def afford(income, dti, dp=20):
    a_pmts = income * dti/100
    cap_rate = .0956 # all in PITI % at 4% for 30, with 3.83% in T & I
    value = a_pmts / cap_rate # loan value
    house = value/(1-(dp/100))# calc the house price based on loan value
    print('With an income of ${0:,.0f} and a {1:,.0f}% down payment you can afford a ${2:,.0f} house with a {3:.0f}% DTI ratio. Monthly payments = ${4:,.0f}. Down payment = ${5:,.0f}'.format(income, dp, house, dti, a_pmts/12, house/5))

rate_table([4.0])
rent_eqv(1035)
dtis = range(20,31,5)
dps = range(10,21,5)
for i in dtis:
    for j in dps:
        afford(65000, i, j)