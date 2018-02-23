#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 20:06:10 2018

taxes.py

Try to parse town tax rolls
@author: david
"""

'''
Tax instructions for Perinton:



    Go to the Monroe County home page by clicking the above link
    From Top Online Services (right side of homepage), click on View/Pay Taxes Online,
    Agree to the Real Property Portal disclaimer by selecting I Agree
    Enter your house number & street name (select from pulldown menu if similar addresses 
    appear), click on Search; your property will appear on new screen w/aerial view.
    Select Pay Property Taxes (green icon, upper right) to view property tax information

From here, you can view or print tax info (select from the 4 icons at top of page): 

    School Tax Statement – most current school tax bill (same as mailed bill)
    Combined Town/County Tax Statement – most current Town/Cty tax bill (same as mailed bill)
    Duplicate School Statement – indicates payments & current balance
    Duplicate Combined Statement – indicates payments & current balance


'''
import requests
import pandas as pd
from bs4 import BeautifulSoup

'''
How property taxes are calculated

You can calculate the amount you pay in property taxes by multiplying

your property's taxable assessment (your assessment minus any exemptions)

                                              X

the tax rates for school districts, municipalities, counties and special districts.

Tax Owed = taxable assessment x tax rate

Tax rates are calculated by local jurisdictions

There are several steps involved in determining tax rates:

    Taxing jurisdiction (school district, municipality, county, special district) develops and adopts a budget.
    Taxing jurisdiction determines revenue from all sources other than the property tax (state aid, sales tax revenue, user fees, etc.).
    Revenues are subtracted from the budget and the remainder becomes the tax levy. The tax levy is the amount of the tax levy that is raised through the property tax.

    Tax levy = budget - revenues
    To determine the tax rate, the taxing jurisdiction divides the tax levy by the total taxable assessed value of all property in the jurisdiction.
    Because tax rates are generally expressed as "per $1,000 of taxable assessed value," the product is multiplied by 1,000.

Tax rate per thousand (tax levy ÷ total of all taxable assessments in jurisdiction) x 1,000

For example:

    Town A's tax levy = $2,000,000
    Town's total taxable assessed value = $40,000,000
    Tax rate = $50 per $1,000 of taxable assessed value
    Tax bill for property with a taxable assessment of $150,000 = $7,500

To calculate tax rates for counties and school districts that cross over municipal boundaries equalization rates are necessary.
'''

#County 7.705588  0.663173 services df[0]
#Town(Perinton) 2.244207 df[0]
#School (Fairport) 23.029677 df[2]
#Library (Fairport) 0.794601 df[2]
#PR104 Bushnell Basin Fire 0.845769 df[1]
#PR110 Perinton Ambulance 0.04341 df[1]
#PR701 Perinton Consl Sewer 80.000258 per unit df[1]



url = 'https://www2.monroecounty.gov/property-taxrates.php'
df = pd.read_html(url, header=0)
'''
print(len(df)) # count how many tables have been found
df_special = df[1]
# special district filters
pr104 = df_special['Code'] == 'PR104'
pr110 = df_special['Code'] == 'PR110'
pr701 = df_special['Code'] == 'PR701-B'
print(df_special[pr104])
print(df_special[pr110])
print(df_special[pr701])
'''


county_monroe = 7.705588 + 0.663173
town_perinton = 2.244207
school_fairport = 23.029677 
library_fairport = 0.794601
fire_bushbasin = 0.845769
ambulance_perinton = 0.04341
sewer_perinton = 80.000258

sum_mill_rates = county_monroe + town_perinton + school_fairport + library_fairport + fire_bushbasin + ambulance_perinton

def taxes(assessed_values):
    for assessed_value in assessed_values:
        tax = assessed_value/1000 * sum_mill_rates + sewer_perinton # sewer is assessed per unit, typically one per house
        print('The total taxes on a ${0:,.0f} house are ${1:,.0f}, or {2:.1f}% of the total value.'.format(assessed_value, tax, tax/assessed_value*100))

assessed_values = [150000, 175000, 200000, 225000, 250000]
taxes(assessed_values)