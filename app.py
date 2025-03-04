import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# Alpha Vantage API Key
API_KEY = "EY0BHX91K5UY3W6Q"

# List of companies and their stock symbols
companies = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA"
}

# Streamlit UI
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

dark_mode = st.toggle("🌗 Toggle Dark/Light Mode", value=True)

theme = "plotly_dark" if dark_mode else "plotly_white"

selected_company = st.selectbox("Select a Company", list(companies.keys()))
investment_amount = st.slider("Enter amount to invest ($)", min_value=10, max_value=10000, step=10)

def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    return response.json()

if st.button("Fetch Stock Data"):
    symbol = companies[selected_company]
    stock_data = get_stock_data(symbol)

    if "Time Series (5min)" in stock_data:
        df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index")
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        
        start_price = df.iloc[0]["Close"]
        current_price = df.iloc[-1]["Close"]
        highest_price = df["High"].max()
        
        st.metric("Starting Price ($)", round(start_price, 2))
        st.metric("Current Price ($)", round(current_price, 2))
        st.metric("Highest Price ($)", round(highest_price, 2))
        
        df["MA_20"] = df["Close"].rolling(window=20).mean()
        decision = "Buy" if df.iloc[-1]["Close"] > df.iloc[-1]["MA_20"] else "Sell"
        st.subheader(f"Recommendation: {decision}")

        x = np.arange(len(df)).reshape(-1, 1)
        y = df["Close"].values
        model = LinearRegression().fit(x, y)
        future_price = model.predict([[len(df) + 10]])[0]
        percentage_change = ((future_price - current_price) / current_price) * 100

        st.subheader(f"Predicted Price Change: {round(percentage_change, 2)}%")
        num_stocks = investment_amount / current_price
        st.subheader(f"You can buy approximately {int(num_stocks)} stocks with ${investment_amount}")
        
        fig = px.line(df, x=df.index, y="Close", title="Stock Price Trend", template=theme)
        st.plotly_chart(fig)
    else:
        st.warning("⚠️ Unable to fetch stock data. API limit may be reached!")
