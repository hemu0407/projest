import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np

# Alpha Vantage API Key
API_KEY = "FG9COB3AYV3V9FVK"

# List of companies and their stock symbols
companies = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
    "Meta (META)": "META",
    "Netflix (NFLX)": "NFLX",
    "Nvidia (NVDA)": "NVDA",
    "IBM (IBM)": "IBM",
    "Intel (INTC)": "INTC"
}

# Streamlit UI
st.title("📈 Stock Market Prediction & Analysis")

# Dropdown for company selection
selected_company = st.selectbox("Select a Company", list(companies.keys()))

# Fetch stock data function
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data

# Button to fetch data
if st.button("Fetch Stock Data"):
    symbol = companies[selected_company]
    stock_data = get_stock_data(symbol)

    if "Time Series (5min)" in stock_data:
        df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index")
        df = df.astype(float)  # Convert values to float
        df.index = pd.to_datetime(df.index)  # Convert index to datetime
        df = df.sort_index()  # Sort the data

        # Rename columns
        df.columns = ["Open", "High", "Low", "Close", "Volume"]

        # Extract key values
        starting_price = df.iloc[0]["Open"]
        current_price = df.iloc[-1]["Close"]
        highest_price = df["High"].max()

        # Display key prices
        st.metric(label="📌 Starting Price", value=f"${starting_price:.2f}")
        st.metric(label="📌 Current Price", value=f"${current_price:.2f}")
        st.metric(label="📌 Highest Price", value=f"${highest_price:.2f}")

        # Moving Average for Trend Prediction
        df["SMA_10"] = df["Close"].rolling(window=10).mean()  # 10-period Simple Moving Average

        # Plot stock trend
        fig = px.line(df, x=df.index, y=["Close", "SMA_10"], title=f"{selected_company} Stock Trends",
                      labels={"value": "Stock Price", "index": "Date"},
                      template="plotly_dark")
        st.plotly_chart(fig)

        # Simple Investment Advice
        if df["SMA_10"].iloc[-1] > df["SMA_10"].iloc[-2]:  # If SMA is rising
            st.success("📊 The trend is **upward** 📈. It **might be a good time to invest**!")
        else:
            st.warning("📉 The trend is **downward**. Consider waiting before investing.")

    else:
        st.error("⚠️ Could not fetch stock data. API limit may have been reached!")
