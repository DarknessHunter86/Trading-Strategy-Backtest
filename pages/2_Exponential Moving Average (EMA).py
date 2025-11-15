import streamlit as st #run with " streamlit run streamlit_EMA_Backtest.py "
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.title("Trading Strategy Backtest --  Exponential Moving Average (EMA)")


#Upload a csv file and put in the uploaded sectiob.
uploaded = st.file_uploader("Upload CSV", type="csv")


if uploaded:



    #Read the files using pandas
    dataframe_unrestrained = pd.read_csv(uploaded)
    dataframe_unrestrained['Date'] = pd.to_datetime(dataframe_unrestrained['Date']) #Transfers date column to datetime
    dataframe_unrestrained = dataframe_unrestrained.set_index('Date') #turns dates to index.

    #All User inputs
    #Use date_input for dates.

    #min_date and max_date for which dates can be chosen (within the file).

    min_date = dataframe_unrestrained.index.min().date()
    max_date = dataframe_unrestrained.index.max().date()

    startdate = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    enddate = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
    initial_balance = st.number_input("Initial Balance", 1, 100000, 1000)
    induced_cost = st.number_input("Transaction cost (%)", 0, 100, 1) / 100
    short_EMA = st.number_input("Short EMA", 1, 200, 12)
    long_EMA  = st.number_input("Long EMA", 1, 500, 26)


    # Convert to datetime for comparison
    startdate = pd.to_datetime(startdate)
    enddate = pd.to_datetime(enddate)


    # Filter between startdate and enddate
    dataframe = dataframe_unrestrained.loc[startdate:enddate]


    year = round((len(dataframe) / 365.25),2) #dataframe is now an index, with a length


    #Define a new column, Daily Return, defined as the % change daily, shift(1) meaning data from the previous day.
    dataframe['Daily_Return'] = (dataframe['Close'] / dataframe['Close'].shift(1))

    #Set initial Daily Return at first row to be 0. .loc(Row,Column) --> BY LABEL
    dataframe.loc[dataframe.index[0], 'Daily_Return'] = 1

    #Define the balance if stayed for the entire duration (base case).
    dataframe['Stay_Balance'] = initial_balance * dataframe['Daily_Return'].cumprod()
    #Define the Peak Price as the highest stock price by that point; 
    #Define DrawDown (negative) as the maximum % decrease in price compared to the peak price
    dataframe['Peak_Price_Stay'] = dataframe['Stay_Balance'].cummax()
    dataframe['DrawDown'] = ((dataframe['Stay_Balance']) - (dataframe['Peak_Price_Stay'])) / (dataframe['Peak_Price_Stay'])


    #Define annual_return as the annual % change in balance, averaged throughout 10 years. iloc[rows_index,col_index] --> BY NUMBER
    #Round to 2 decimal places using round()
    annual_return_stay_balance = round(((((dataframe['Stay_Balance'].iloc[-1])/(dataframe['Stay_Balance'].iloc[0]))**(1/year) - 1) * 100),2)
    maximum_drawdown_stay_balance = round(dataframe['DrawDown'].min() * 100,2)


    #Code the EMA Crossover strategy.
    #Alpha presents how weight is distibuted.

    #EMA_today = Price_today * alpha + EMA_yesterday * (1-alpha)
    #Use a function to define any recursive relationships.

    def ema_generator(series, n):
        
        if len(series) < n: #Prevents breaking due to lower no. of terms than long/short_EMA.
             return [np.nan] * len(series)
    
        alpha = 2 / (n + 1)
        ema_values = [np.nan] * len(series) # creates a list of nan values with len(series) rows.

        # Seed with SMA of first n price
    
        ema_values[n-1] = series.iloc[:n].mean() #define ema_values(n-1) as the mean of the first n-1 prices.

        for i in range(n, len(series)): #for all terms after the first n, calculate normally (given ema_values(n-1) which is the initial condition).
            ema_values[i] = alpha * series.iloc[i] + (1 - alpha) * ema_values[i-1]

        return ema_values

    #Define Long_EMA and Short_EMA similarly.
    #For some reason dataframe['Close'] is a dataframe not a series, so use squeeze() to turn into series to make it comparable with dataframe['Long_EMA'] etc.


    dataframe['Long_EMA'] = ema_generator(dataframe['Close'].squeeze(), long_EMA) 
    dataframe['Short_EMA'] = ema_generator(dataframe['Close'].squeeze(), short_EMA)



    #Define Buy_in as a boolean expression indicating if the short-term MA is performing better than the long-term MA.
    dataframe['Buy_in'] = dataframe['Short_EMA'] > dataframe['Long_EMA']


    #Transaction costs are induced if entering/exiting a trade. If Buy_in state is different from yesterday a buy/sell has occurred.
    dataframe['Transaction_Cost'] = np.where(dataframe['Buy_in'] != dataframe['Buy_in'].shift(1), 1, 0)


    #Define the strategy by entering the market on the next day if the day previously satisfies the Buy_in / Transaction_cost condition.
    #Else doesn't go in , daily return = 1. 
    dataframe['Strategy_Daily_Return'] = np.where((dataframe['Buy_in'].shift(1) == True), dataframe['Daily_Return'] * (1 - dataframe['Transaction_Cost'] * (induced_cost)), 1)

    #Define the total balance as time progresses similarly to Stay_Balance. 
    dataframe['Strategy_Balance'] = initial_balance * dataframe['Strategy_Daily_Return'].cumprod()

    dataframe['Peak_Price_Strategy'] = dataframe['Strategy_Balance'].cummax()

    dataframe['DrawDown_Strategy_Balance'] = ((dataframe['Strategy_Balance']) - (dataframe['Peak_Price_Strategy'])) / (dataframe['Peak_Price_Strategy'])

    annual_return_strategy_balance = round(((((dataframe['Strategy_Balance'].iloc[-1])/(dataframe['Strategy_Balance'].iloc[0]))**(1/year) - 1) * 100),2)
    maximum_drawdown_strategy_balance = round(dataframe['DrawDown_Strategy_Balance'].min() * 100,2)



    #Figure of EMA strategy vs Stay_Balance strategy.
    fig1, ax = plt.subplots()

    ax.plot(dataframe['Strategy_Balance'], label="EMA Strategy")
    ax.plot(dataframe['Stay_Balance'], label="Buy & Hold")
    ax.set_title("EMA Strategy vs Buy and Hold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance")
    ax.legend()  # <-- Add legend
    st.pyplot(fig1)
 
    st.write(f'The annual return of Buy & Hold over {year} years is {annual_return_stay_balance}%.')
    st.write(f'The annual return of EMA Strategy over {year} years is {annual_return_strategy_balance}%.')
    st.write(f'The Highest Drawdown of Buy & Hold over {year} years is {maximum_drawdown_stay_balance}%.')
    st.write(f'The Highest Drawdown of EMA Strategy over {year} years is {maximum_drawdown_strategy_balance}%.')
    
    #Figure of MAs compared with Close. 
    fig, ax = plt.subplots()
    ax.plot(dataframe['Close'], label='Close')
    ax.plot(dataframe['Short_EMA'], label='Short_EMA')
    ax.plot(dataframe['Long_EMA'], label='Long_EMA')
    ax.set_title("Close, Short_EMA and Long_EMA")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    st.pyplot(fig)


    #Show dataframe
    st.dataframe(dataframe)

else:
    st.info("Upload CSV to begin.")
