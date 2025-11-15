import streamlit as st


st.title('Welcome to the Trading Strategy Backtest App!')

st.write('This app uses Python and external libraries (including pandas, numpy...) to provide **SMA** and **EMA** backtests!')

st.write('Please use the nagivation bar on the left to head to **SMA** and **EMA**, respectively.')

st.image("output.png", caption="MA performed on Microsoft, 2015-2025", use_container_width=True) #Import an image locally saved in the folder.

st.subheader("Important:")

st.write('The app will require **pre-downloaded CSV files** from your local file and upload them to the app.')
st.write('Make sure the first index of the stock price is labelled **"date"** and the price of interest is labelled **"close"**, which is commonly the case for most data')





