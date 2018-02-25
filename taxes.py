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
    #print(town, school)
    df = df.fillna(method='ffill')
    df_school = df['Town'] == school
    df_town = df['District'] == town
    # print(df)
    return df[df_school & df_town].head(1)['Total'].values[0]

def tax_special(df, districts):
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
    

############################################################
url = 'https://www2.monroecounty.gov/property-taxrates.php'
df = pd.read_html(url, header=0)
town = 'Perinton'
school = 'Fairport (Village)' # matches 'Town'
school_town = 'Fairport' # matches 'District'
districts = ['PR104','PR110','PR701-B']
price = 200000
price_000 = price / 1000

total_taxes = 0
c, t = tax_county_town(df, town)
total_taxes += (c * price_000 + t * price_000)
s = tax_school_library(df, school_town, school)
total_taxes += (s * price_000 * 0.90) #assessed against 90% of house value
d = tax_special(df, districts)
for tax in d:
    total_taxes += tax
print('${0:,.0f}  {1:.1f}%'.format(total_taxes, total_taxes / price * 100))