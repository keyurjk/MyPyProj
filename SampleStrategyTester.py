'''
First sample code on Jupyter Notebook to test a trading strategy
Strategy is to Go long at open PP (intraday trade) if overnight gap is b/w -1% to -2%. (YC-Today Op PP).
There is no SL, Exit EOD at Close PP. Compute the returns.
Data imported from csv file of USDINR future from NSE for 2020 year

'''

# import other libraries

import pandas as pd

print('Hello World!')

# Get the data, read CSV or from other source

#reset the index to Trade Date

# Plot the Close Price

# Import matplotlib
import matplotlib.pyplot as plt
%matplotlib inline

# Call the plot method
data['Close Price'].plot(figsize=(10, 7), grid=True)
plt.show()

# Compute the percentage change

# Previous day close to today's open 
# % check on 1 paise for Forex data

data['overnight_gap'] = (
    data['Open Price']-data['Close Price'].shift(1))/0.1000

# Open to Close
data['intraday_returns'] = (data['Close Price']-data['Open Price'])/data['Open Price']

data.head(3)

# Define your conditions on which you want to trade
cond_1 = data.overnight_gap < -1.0
cond_2 = data.overnight_gap > -2.0

# Store it in the signal columns of dataframe data
data['signal'] = np.where(cond_1 & cond_2, 1, 0)

data.head()

#display the signal data
data.loc[data.signal==1].head()

#describe the data showing mean and other details.
data.loc[data.signal==1].describe()

# Compute the strategy returns
strategy_returns = data.signal * data.intraday_returns

# Plot the cumulative strategy returns
(strategy_returns+1).cumprod().plot(figsize=(10, 7), grid=True)
plt.xlabel('Month')
plt.ylabel('Cumulative Strategy Returns')
plt.show()

# Detailed performance analysis (this requires installation as !pip install pyfolio
import pyfolio as pf
pf.create_simple_tear_sheet(strategy_returns)
