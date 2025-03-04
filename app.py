import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np

# Alpha Vantage API Key
API_KEY = "FG9COB3AYV3V9FVK"

# List of companies
companies = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA"
}

# Function to Fetch Stock Data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (5min)" in data:
        df = pd.DataFrame.from_dict(data["Time Series (5min)"], orient="index")
        df = df.astype(float)  # Convert values to float
        df.index = pd.to_datetime(df.index)  # Convert index to datetime
        df.sort_index(inplace=True)
        return df
    else:
        return None  # Return None if API request fails

# Function to Predict Future Trends
def predict_trend(data):
    if data is None or data.empty:
        return "No data available for prediction."

    # Simple Moving Average (SMA)
    data["SMA_5"] = data["4. close"].rolling(window=5).mean()

    # Get last two SMA values
    last_sma = data["SMA_5"].dropna().iloc[-1]
    prev_sma = data["SMA_5"].dropna().iloc[-2]

    if last_sma > prev_sma:
        return "📈 The trend is **UPWARDS**. Investing could be a good option!"
    else:
        return "📉 The trend is **DOWNWARDS**. You might want to wait before investing."

# Streamlit UI
st.title("📊 Stock Market Prediction App")
st.subheader("Select a Company and Get Stock Insights")

# Company Selection
selected_company = st.selectbox("Choose a Company:", list(companies.keys()))

# Fetch Data Button
if st.button("Fetch Data"):
    stock_symbol = companies[selected_company]
    stock_data = get_stock_data(stock_symbol)

    if stock_data is not None:
        # Show Key Statistics
        opening_price = stock_data.iloc[0]["1. open"]
        current_price = stock_data.iloc[-1]["4. close"]
        highest_price = stock_data["2. high"].max()

        st.markdown(f"""
        - **Opening Price:** ${opening_price:.2f}  
        - **Current Price:** ${current_price:.2f}  
        - **Highest Price:** ${highest_price:.2f}  
        """)

        # Display Stock Price Graph
        fig = px.line(stock_data, x=stock_data.index, y="4. close", title=f"{selected_company} Stock Price Trend")
        st.plotly_chart(fig)

        # Predict Future Trend
        prediction = predict_trend(stock_data)
        st.subheader("📢 Investment Advice")
        st.write(prediction)

    else:
        st.error("⚠️ Unable to fetch stock data. Try again later!")

