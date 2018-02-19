#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 15:42:13 2018

mortgage_rates.py
@author: david

"""
import requests
import pandas as pd
from bs4 import BeautifulSoup


class Rates:
    def __init__(self):
        self.var = 0

    def get_website_content(self, url):
        r = requests.get(url)
        if r.status_code != 200:
            print('There was an error, code ' + str(r.status_code))

        soup = BeautifulSoup(r.content, "html5lib")
        return soup

    def rates_mandtbank(self):
        rate_dict = {}
        counter = 0
        url = 'https://onlinemortgage.mtb.com/LoansAndRates/GetRates'
        site = self.get_website_content(url)
        tbodies = site.find_all('tbody')
        for tbody in tbodies:
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                loan_type = str.strip(cells[0].contents[0])
                rate = cells[1].contents[1].contents[0]
                apr = cells[2].contents[1].contents[0]
                points = str.strip(cells[3].contents[0])
                rate_dict[counter] = [loan_type, rate, apr, points]
                counter+=1
        # convert to df
        names = ['loan type', 'rate', 'apr', 'points']
        df = pd.DataFrame.from_dict(rate_dict, orient='index')
        df.columns = names
        #print(df)
        return df

    def main(self):
        self.rates_mandtbank()
        print('ok')

def test():
    rates = Rates()
    rates.main()

if __name__ == "__main__":
    test()