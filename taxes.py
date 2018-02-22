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
from bs4 import BeautifulSoup

url = 'https://www2.monroecounty.gov/property-taxrates.php'
r = requests.get(url)
soup = BeautifulSoup(r.content, "html.parser")
tables = soup.find_all('table')
for table in tables:
    rows = table.find_all('tr')
    for row in rows:
        print(row.contents)