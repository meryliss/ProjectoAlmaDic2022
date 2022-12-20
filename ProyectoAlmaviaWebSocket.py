#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 17:17:29 2022

@author: mery
"""
import time
import datetime
import pyRofex as pr
import numpy as np
import unittest
import sys

#Instruments to test given as a dictionary
#Key is the ROFEX Ticker of the underlying instrument
#Value is the ROFEX ticker of the future contract to be tested

instruments = {"MERV - XMEV - YPFD - 48hs":"YPFD/FEB23",
               "MERV - XMEV - GGAL - 48hs":"GGAL/FEB23",
               "MERV - XMEV - PAMP - 48hs":"PAMP/FEB23",
               "MERV - XMEV - DOLAR - 7D":"DLR/FEB23"} 

#Remarkets account credentials
remarkets_user = "mhlissarrague7682"
remarkets_password = "objxhQ1#"
remarkets_account = "REM7682" 
    
#Time to keep code running in seconds
keep_code_running = 120

class Implied_rates:
    def __init__(self, fut_price, spot_price,currency, tte):
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
        ImpRate = Implied_rates(50,40,"ARS",1)
        self.assertEqual(ImpRate.calc_rate(), 0.25, "incorrect value")

unittest.main()

# Defines the handlers that will process the messages from WebSocket relative 
# to the nstruments.
def market_data_handler(message):
    # processes WebSocket succesful messages. 
    # Checks for arbitrage opportunities if information regarding to future bid/ask 
    # and spot price is complete
    
    instr = message["instrumentId"]["symbol"]
    today = datetime.datetime.today()
    
    # Identifies the instrument to which the message corresponds
    # Depending on the intrument type (future or underlying) gets the information 
    # of the other one. 
    if instr in instruments.keys():
        print("Price change in: " + instr)
        spot= message["marketData"]["LA"]
        fut_info_now = pr.get_market_data(ticker = instruments [instr], 
                                               entries = [pr.MarketDataEntry.BIDS,
                                                         pr.MarketDataEntry.OFFERS])
        bid = fut_info_now["marketData"]["BI"]
        ask = fut_info_now["marketData"]["OF"]
        mat_date = datetime.datetime.strptime(pr.get_instrument_details(ticker = instruments [instr])
                                        ["instrument"]["maturityDate"], "%Y%m%d").date()                    
    
    if instr in instruments.values():
        print("Price change in: " + instr)
        bid = message["marketData"]["BI"]
        ask = message["marketData"]["OF"]

        und = [k for k, v in instruments.items() if v == instr]
        und_info_now = pr.get_market_data(ticker = und[0], 
                                                entries =[pr.MarketDataEntry.LAST])
        spot = und_info_now["marketData"]["LA"]
        mat_date = datetime.datetime.strptime(pr.get_instrument_details(ticker = instr)
                                        ["instrument"]["maturityDate"], "%Y%m%d").date()
    # if information for Future bid and ask price as well as spot, s available
    # system calculates the implied bid-ask rates and checks for arbitrage opportunity
    if bid and ask and spot:
        bid_price = bid [0]["price"]
        ask_price = ask [0]["price"]
        spot_price = spot ["price"]
        tte = (mat_date - today.date()).days/365
        imp_rate_bid = Implied_rates(bid_price, spot_price, tte).calc_rate()
        imp_rate_ask = Implied_rates(ask_price, spot_price, tte).calc_rate()

        print ("Bid Implied Rate: " + str (round(imp_rate_bid*100,3)) + " %")
        print ("Ask Implied Rate: " + str (round(imp_rate_ask*100,3)) + " %")
                        
        if imp_rate_ask < imp_rate_bid:
            print("THERE IS ARBITRAGE OPPORTUNITY")
        else:
            print("NO ARBITRAGE OPPORTUNITY")
        
    else:
        # if information is not complete it returns message indicating this issue
        print("Missing values. Not able to calculate Implied rate")
                
def error_handler(message):
    # proccess error messages received and instrucks to ckeck tickers.
    # forces exit as there is most probaly an error relative to tickers
    print("Error Message Received: {0}".format(message))
    print("Check tickers")
    global error
    error = True
    sys.exit()

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))


if __name__ == "__main__":
     
    error = False
        
    pr.initialize(user = remarkets_user, password = remarkets_password,
                    account=remarkets_account,environment=pr.Environment.REMARKET)


    # Initialize Websocket Connection with the handlers 
    pr.init_websocket_connection(market_data_handler = market_data_handler,
                                  error_handler = error_handler,
                                  exception_handler = exception_handler)

    # Subscribes for Market Data which will send messages every time there is a change in
    # Market Data relative to the selected tickers
    
    # for the Underlying we request for LAST price change
    pr.market_data_subscription(tickers = instruments.keys(), entries = [pr.MarketDataEntry.LAST])
    
    # for Futures we request for BID and ASK prices change
    pr.market_data_subscription(tickers = instruments.values(),
                                          entries=[pr.MarketDataEntry.BIDS,
                                                  pr.MarketDataEntry.OFFERS])

    time.sleep(1)
    
    if error == True:
        sys.exit()
    else:  
        time.sleep(keep_code_running)
        print("Closing WebSocket Connection")
        pr.close_websocket_connection()
