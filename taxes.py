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

_URL = 'https://www2.monroecounty.gov/property-taxrates.php'
_DF = pd.read_html(_URL, header=0)

def tax_county_town(df, town):
    """Returns county and town tax rates per $1,000 of value"""
    df = df[0]
    town = town.upper()
    df_county_town = df['Municipality'] == town
    tax_county = df[df_county_town]['Net County Rate'].values + df[df_county_town]['County Services'].values
    tax_town = df[df_county_town]['Net Town Rate'].values
    
    return tax_county[0], tax_town[0]

def tax_school_library(df, town, school):
    """Returns combined school and library tax rate per $1,000"""
    df = df[2]
    town = str(town).title()
    school = str(school).title()
    df = df.fillna(method='ffill')
    df_school = df['Town'] == school
    df_town = df['District'] == town
    return df[df_school & df_town].head(1)['Total'].values[0]

def tax_special(df, districts, price_000):
    """Returns special district tax bill in $"""
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

def tax_calc(df=_DF, price=200000, municipality='Fairport', town='Perinton', school='Fairport (Village)', school_town='Fairport', districts=['PR104','PR110','PR701-B']):
    """Returns string with the tax bill and tax % given the price and home location"""
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

def tax_rate(df=_DF, price=200000, municipality='Fairport', town='Perinton', school='Fairport (Village)', school_town='Fairport', districts=['PR104','PR110','PR701-B']):
    """Returns tax rate given the price and home location"""
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

    return total_taxes / price

def get_all_town_taxes():
    """Calls tax_calc on each town in tax_dict"""
    town_taxes = []
    for k,v in tax_dict.items():
        price = 200000
        municipality = k
        town = v['town']
        school = v['school']
        school_town = v['school_town']
        districts = v['districts']
        town_taxes.append(tax_calc(_DF, price=price, municipality=municipality, town=town, school=school, school_town=school_town, districts=districts))
    return town_taxes

def get_town_tax(town_name='Fairport'):
    """Calls tax_calc on the town given"""
    v = tax_dict[town_name]
    municipality = town_name
    town = v['town']
    school = v['school']
    school_town = v['school_town']
    districts = v['districts']
    return tax_calc(_DF, price=200000, municipality=municipality, town=town, school=school, school_town=school_town, districts=districts)

def get_town_tax_rate(town_name='Fairport'):
    """Calls tax_rate on the town given"""
    v = tax_dict[town_name]
    municipality = town_name
    town = v['town']
    school = v['school']
    school_town = v['school_town']
    districts = v['districts']
    return tax_rate(_DF, price=200000, municipality=municipality, town=town, school=school, school_town=school_town, districts=districts)
