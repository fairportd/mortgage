#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 20:06:10 2018

taxes.py

Calculate taxes for a given house value by town
@author: david
"""

import pandas as pd
from taxes_dict import tax_dict


def tax_county_town(df, town):
    ''' Get county and town tax rates '''
    df = df[0]
    town = town.upper()
    df_county_town = df['Municipality'] == town
    tax_county = df[df_county_town]['Net County Rate'].values + df[df_county_town]['County Services'].values
    tax_town = df[df_county_town]['Net Town Rate'].values
    
    return tax_county[0], tax_town[0]

def tax_school_library(df, town, school):
    ''' Get the combined school and library tax rates '''
    df = df[2]
    town = str(town).title()
    school = str(school).title()
    df = df.fillna(method='ffill')
    df_school = df['Town'] == school
    df_town = df['District'] == town
    return df[df_school & df_town].head(1)['Total'].values[0]

def tax_special(df, districts, price_000):
    ''' Pass in list of applicable special districts'''
    df = df[1]
    district_taxes = []
    for district in districts:
        df_special = df['Code'] == district
        district_taxes.append(df[df_special])

    tax_dollars = []
    for d in district_taxes:
        if d['Unnamed: 8'].values[0] == '/1000':
            tr = d['Tax Rate'].values[0]
            tax_dollars.append(tr * price_000)
        elif d['Unnamed: 8'].values[0] == '/ Unit':
            ur = d['Tax Rate'].values[0]
            tax_dollars.append(ur * 1)

    return tax_dollars

def tax_calc(df, price=200000, municipality='Fairport', town='Perinton', school='Fairport (Village)', school_town='Fairport', districts=['PR104','PR110','PR701-B']):
    price_000 = price / 1000
    total_taxes = 0
    # calc the different types of taxes
    c, t = tax_county_town(df, town)
    total_taxes += (c * price_000 + t * price_000)
    s = tax_school_library(df, school_town, school)
    total_taxes += (s * price_000 * 0.90) #assessed against 90% of house value
    d = tax_special(df, districts, price_000)
    for tax in d:
        total_taxes += tax

    return (municipality + ' Taxes: ${0:,.0f}  {1:.1f}%'.format(total_taxes, total_taxes / price * 100))

url = 'https://www2.monroecounty.gov/property-taxrates.php'
df = pd.read_html(url, header=0)
price = 175000

for k,v in tax_dict.items():
    municipality = k
    town = v['town']
    school = v['school']
    school_town = v['school_town']
    districts = v['districts']
    
    print(tax_calc(df, price=price, municipality=municipality, town=town, school=school, school_town=school_town, districts=districts))


