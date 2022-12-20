# ProjectoAlmaDic2022
### Check for IR arbitrage opportunities

#### The idea behind this project is to check for arbitrage opportunities by comparing Bid/Ask implied rates in ROFEX future contracts.

#### While the functon for calculating implied rates is the same,two methodologies were implemented for getting price information: The first one by constatly checking for price changes via REST and the second one by stablishing WebSocket connecting and receiving information every time there is a price change.
#### To run these codes you need yFinance and pyRofex packages. In order to install them use:
#### - pip install yfinance
#### - pip install pyRofex
#### Additionally you need to create a REMARKETS account in https://remarkets.primary.ventures/. The user, password and account provided will be used as inputs for the code.
### Via REST
#### When using this approach instruments are given in a dictionary in which the keys are the yFinance tickers for the underlyers and the values are the Rofex futures to be tested.
#### Initially, the code generates a dicctionary that stores the initial stock price, bid and ask prices for the future. Then it constantly monitors the thre prices and checks for changes. If there is a change in the values it calculates the implied retes and checks for arbitrage opportunities. 
#### Code keeps running until we decide to interrupt price monitoring.
#### Via WebSocket
#### When using this approach instruments are given in a dictionary in which the keys are the Rofex tickers for the underlyers and the values are the Rofex futures to be tested. In this case, it is necessary to establish a time lapse in which we can to keep the code running before closing WebSocket connection (i.e. receiving messages with market data changes).
#### Initially, WebSocket connection is established and the system receives messages when there are changes in the specified intruments (both futures and underlyings). Messages are precesaed and information related to the corresponding underlying/future is requested (i.e. if there is a change in underlyer price there is an additinal request for informating regarding the future). Implied rates are calulated and tested for arbitrage opportunities. 
