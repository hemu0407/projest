import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np

# Alpha Vantage API Key
API_KEY = "QVQRLHHR3IS7BLSS"

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

# Dark/Light Mode Toggle
theme = st.radio("Select Theme", ["Dark Mode", "Light Mode"], index=0)
theme_template = "plotly_dark" if theme == "Dark Mode" else "plotly_white"

# Multi-select dropdown for company selection
selected_companies = st.multiselect("Select Companies", list(companies.keys()), default=["Apple (AAPL)", "Microsoft (MSFT)"])

# Fetch stock data function
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data

# Button to fetch data
if st.button("Fetch Stock Data"):
    all_stock_data = {}

    for company in selected_companies:
        symbol = companies[company]
        stock_data = get_stock_data(symbol)

        if "Time Series (5min)" in stock_data:
            df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index")
            df = df.astype(float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ["Open", "High", "Low", "Close", "Volume"]
            df["Company"] = company
            df["SMA_10"] = df["Close"].rolling(window=10).mean()
            all_stock_data[company] = df
        else:
            st.error(f"⚠️ Could not fetch data for {company}. API limit may have been reached!")

    if all_stock_data:
        combined_df = pd.concat(all_stock_data.values())
        fig = px.line(combined_df, x=combined_df.index, y=["Close", "SMA_10"], color="Company",
                      title="Stock Trends Comparison", labels={"value": "Stock Price", "index": "Date"},
                      template=theme_template)
        st.plotly_chart(fig)

        # Investment Advice for Each Stock
        for company, df in all_stock_data.items():
            st.subheader(f"📊 {company} - Investment Advice")
            if df["SMA_10"].iloc[-1] > df["SMA_10"].iloc[-2]:
                st.success(f"📈 **{company}** is trending **upward**. Might be a good time to invest!")
            else:
                st.warning(f"📉 **{company}** is trending **downward**. Consider waiting.")
