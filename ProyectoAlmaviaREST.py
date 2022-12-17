#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 11:59:54 2022

@author: mery
"""


#connection through rest
import pyRofex as pr
import yfinance as yf
import numpy as np
import datetime
import unittest

rofex_user = "mhlissarrague7682"
rofex_password = "objxhQ1#"
rofex_account = "REM7682"


instruments = {"YPFD.BA":"YPFD/FEB23", "GGAL.BA": "GGAL/FEB23",
                "PAMP.BA": "PAMP/FEB23","ARS=X" : "DLR/FEB23"}



class Implied_rates:
    def __init__(self, fut_price, spot_price, tte):
        self.future_price = fut_price
        self.spot_price = spot_price
        self.tte = tte
    def calc_rate(self):
        x = self.future_price/self.spot_price
        y = 1/self.tte
        implied_rate = np.power(x,y) - 1 
        return implied_rate


class TestCalcImpliedRates(unittest.TestCase):
    def runTest(self):
        ImpRate = Implied_rates(50,40,1)
        self.assertEqual(ImpRate.calc_rate(), 0.25, "incorrect value")

unittest.main()


if __name__ == '__main__' :
    
    pr.initialize(user = rofex_user, password = rofex_password,
                    account=rofex_account,environment=pr.Environment.REMARKET)  
    
    instrument_info = {}
    
    for i,j in instruments.items():
        
        fut_info = pr.get_market_data(ticker = j)

        mat_date = datetime.datetime.strptime(pr.get_instrument_details(ticker = j)
                                        ["instrument"]["maturityDate"], "%Y%m%d").date()
    
        stock_info = yf.Ticker(i)
         
        stock_price_init = stock_info.info['regularMarketPrice']
        
        data = {"FutName" : j, "MatDate" : mat_date,"StockPrice" : stock_price_init }
        
        instrument_info[ i ] = data

    
    while True:
        
        for i in instrument_info.keys():
                
            asset_data = instrument_info [ i ]
            
            try:
                stock_info_now = yf.Ticker(i)
                stock_price_curr = stock_info_now.info['regularMarketPrice']

                try:
                    if stock_price_curr != asset_data["StockPrice"]:
                        
                        today = datetime.datetime.today()
                        
                        tte = (asset_data["MatDate"] - today.date()).days/365
                    
                        fut_info_now = pr.get_market_data(ticker=asset_data["FutName"])
                

                        fut_price_bid = fut_info_now["marketData"]["BI"][0]["price"]
                        fut_price_ask = fut_info_now["marketData"]["OF"][0]["price"]
                
                        imp_rate_bid = Implied_rates(fut_price_bid, stock_price_curr, tte).calc_rate()
                        imp_rate_ask = Implied_rates(fut_price_ask, stock_price_curr, tte).calc_rate()
            
                        print (i + " Spot Price Change")
                        print ("Bid Implied Rate: " + str (round(imp_rate_bid*100,3)) + " %")
                        print ("Ask Implied Rate: " + str (round(imp_rate_ask*100,3)) + " %")
                        
                        if imp_rate_ask < imp_rate_bid:
                            print(" THERE IS ARBITRAGE OPPORTUNITY")
            
                        asset_data ["StockPrice"] = stock_price_curr
                except:
                    pass 
            except:
                pass
            
            print(".")
            
 
