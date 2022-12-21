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
import sys

#Instruments to test given as a dictionary
#Key is the Yahoo Finance Ticker
#Value is the ROFEX ticker of the future contract to be tested


#-----------------------Parameters to be changed--------------
instruments = {"YPFD.BA" : "YPFD/FEB23","GGAL.BA" : "GGAL/FEB23",
               "PAMP.BA" : "PAMP/FEB23","ARS=X" : "DLR/FEB23",}
    
#Remarkets account credentials
remarkets_user = "mhlissarrague7682"
remarkets_password = "objxhQ1#"
remarkets_account = "REM7682"    

#-----------------------Functions used within the code---------   
class Implied_rates:
    def __init__(self, fut_price, spot_price, currency,tte):
        #Object that contains the impormation for calculating implied rate
        #Parameters
        #fut_price : Price of the future intrument (float)
        #spo_price : Spot price of the underlying (float)
        #currency : currency in which both spot and future price is given (str)
        #tte : Time to expiry of the future instrument in fraction of years (float)
        self.future_price = fut_price
        self.spot_price = spot_price
        self.currency = currency
        self.tte = tte
    def calc_rate(self):
        #returns implied rate in relative value
        x = self.future_price/self.spot_price
        y = 1/self.tte
        implied_rate = np.power(x,y) - 1 
        return implied_rate


class TestCalcImpliedRates(unittest.TestCase):
    #checks wether the implied rate is calculated corrctly
    def runTest(self):
        ImpRate = Implied_rates(50,40,"ARS", 1)
        self.assertEqual(ImpRate.calc_rate(), 0.25, "incorrect value")

unittest.main()


if __name__ == '__main__' :

    # Initialize Remarket account
    pr.initialize(user = remarkets_user, password = remarkets_password,
                    account=remarkets_account,environment=pr.Environment.REMARKET)  
    
    # Get and store the initial prices for future intruments and the corresponding underlyers in 
    # order to check for future changes in prices.
    # If there is no initial information for the selected instruments the code exits and indicates 
    # the absence of information.
    
    instrument_info = {}
    
    for i,j in instruments.items():
        
        fut_info = pr.get_market_data(ticker = j)

        mat_date = datetime.datetime.strptime(pr.get_instrument_details(ticker = j)
                                        ["instrument"]["maturityDate"], "%Y%m%d").date()
    
        try:
            fut_price_bid_init = fut_info["marketData"]["BI"][0]["price"]
        
            fut_price_ask_init = fut_info["marketData"]["OF"][0]["price"]
        except:
            print("No available initial bid/ask for " + j)
            
            fut_price_bid_init = None
            
            fut_price_ask_init = None
            
        stock_info = yf.Ticker(i)
         
        stock_price_init = stock_info.info['regularMarketPrice']
            
        if stock_price_init == None:
            print("No initial spot price value for " + i)

        
        data = {"FutName" : j, "FutBidPrice" :fut_price_bid_init, "FutAskPrice" :fut_price_ask_init,
                "MatDate" : mat_date,"StockPrice" : stock_price_init }
            
        instrument_info[ i ] = data

    print(instrument_info)

    while True:
        
        for i in instrument_info.keys():
                
            asset_data = instrument_info [ i ]
            
            try:
                
                # for each of the listed instruments system gets the current price
                stock_info_now = yf.Ticker(i)
                
                stock_price_curr = stock_info_now.info['regularMarketPrice']
                
                fut_info_now = pr.get_market_data(ticker=asset_data["FutName"])
                
                fut_price_bid = fut_info_now["marketData"]["BI"][0]["price"]
                
                fut_price_ask = fut_info_now["marketData"]["OF"][0]["price"]
                
                #compares current price with the one currently stored, if there is a price change

                try:
                    #compares current price with the one currently stored
                    
                    if stock_price_curr != asset_data["StockPrice"] or fut_price_bid != asset_data["FutBidPrice"] or fut_price_ask!= asset_data["FutAskPrice"] :
                        
                        #if there is price change, system calculates implied rates
                        
                        today = datetime.datetime.today()
                        
                        tte = (asset_data["MatDate"] - today.date()).days/365
                
                        imp_rate_bid = Implied_rates(fut_price_bid, stock_price_curr, "ARS", tte).calc_rate()
                        
                        imp_rate_ask = Implied_rates(fut_price_ask, stock_price_curr, "ARS", tte).calc_rate()
            
                        print (i + " Spot Price Change")
                        print ("Bid Implied Rate: " + str (round(imp_rate_bid*100,3)) + " %")
                        print ("Ask Implied Rate: " + str (round(imp_rate_ask*100,3)) + " %")
                        
                        #system check for arbitrage by comapring bid/ask implied rates
                        
                        if imp_rate_ask < imp_rate_bid:
                            print(" THERE IS ARBITRAGE OPPORTUNITY")
                        else:
                            print("NO ARBITRAGE OPPORTUNITY")
                        
                        #update prices for comparison
            
                        asset_data ["StockPrice"] = stock_price_curr
                        asset_data ["FutBidPrice"] = fut_price_bid
                        asset_data ["FutAskPrice"] = fut_price_ask
                except:
                    if KeyboardInterrupt():
                        sys.exit()
                    else:
                        pass 
            except:
                if KeyboardInterrupt():
                    sys.exit()
                else:
                    pass
            
            print(".")
            
 
