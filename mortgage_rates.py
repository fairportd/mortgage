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
        '''
        Get mortgage rates from m&t bank
        '''
        #TODO Create inner functions to get specific mortgage types

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
        # filter 30 year conventional rates
        mask_30yrcon = df['loan type'] == '30 Year Fixed Rate'
        df_30yrcon = df[mask_30yrcon]
        mask_30yr_rate = df_30yrcon['rate'] == max(df_30yrcon['rate'].values)
        con30 = df_30yrcon[mask_30yr_rate]
        con30 = (con30["loan type"].values[0],
                 con30['rate'].values[0],
                 con30['apr'].values[0],
                 con30['points'].values[0]
                 )
        # filter 30 year va rates
        mask_30yrva = df['loan type'] == 'VA 30 Year Fixed Rate'
        df_30yrva = df[mask_30yrva]
        mask_30yrva_rate = df_30yrva['rate'] == max(df_30yrva['rate'].values)
        va30 = df_30yrva[mask_30yrva_rate]
        va30 = (va30['loan type'].values[0],
                va30['rate'].values[0],
                va30['apr'].values[0],
                va30['points'].values[0]
                )

        return df, con30, va30

    def rates_esl(self):
        '''
        Work in progress
        '''
        rate_dict = {}
        counter = 0
        url = 'https://www.esl.org/personal/resources-tools/rates/mortgages-fixed-rates'
        site = self.get_website_content(url)
        divs = site.find_all('div', {'class':'list-to-table rates-table with-footnote'})
        for div in divs:
            print(div.name)

    def main(self):
        mtb_rates, mtb_con30, mtb_va30 = self.rates_mandtbank()
        print(mtb_con30)
        print(mtb_va30)

def test():
    rates = Rates()
    rates.main()

if __name__ == "__main__":
    test()