#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 20:06:10 2018

mortgage.py

User interface for the mortgage program
@author: david
"""

import os
import amortization_table as amort
import pandas as pd

def sensitivity(amount, rate, term):
    '''
    Generate set of loan summaries based on a base case
    '''
    a = float(amount)
    r = float(rate) / 100
    t = float(term)

    amounts = [a, a + 25000, a + 50000]
    rates = [r, r + .0075, r + .0150]

    s_dict = {}
    for amount in amounts:
        s_list = []
        for rate in rates:
            m = amort.Mortgage(amount, rate, 30)
            m.amortization_table()
            x = m.monthly_payment()
            s_list.append(x)
        s_dict[amount] = s_list

    df = pd.DataFrame.from_dict(s_dict, orient='index')
    df.columns = rates
    print(df)

sensitivity(150000, 4.5, 30)