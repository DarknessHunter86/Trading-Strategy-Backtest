import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import matplotlib.pyplot as plt

st.title("📈 Live Updating Stock Price Chart")

# refresh every 5 seconds
st_autorefresh(interval=5000, key="chart_refresh")

symbol = st.text_input("Enter Stock Symbol", "AAPL")

# get last 1 day with 1-minute interval
data = yf.download(symbol, period="1d", interval="1m")

# extract price series
prices = data["Close"]

# create matplotlib figure
fig, ax = plt.subplots()

ax.plot(prices.index, prices.values)
ax.set_title(f"{symbol} Live Price")
ax.set_xlabel("Time")
ax.set_ylabel("Price")

st.pyplot(fig)
