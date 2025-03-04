import streamlit as st
import requests
import pandas as pd
import plotly.express as px

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

# UI Theme Toggle
mode = st.toggle("🌞 Light Mode / 🌙 Dark Mode", value=False)

# Set Theme
if mode:
    background_color = "#ffffff"
    text_color = "#000000"
    chart_theme = "plotly_white"
else:
    background_color = "#0e1117"
    text_color = "#ffffff"
    chart_theme = "plotly_dark"

st.markdown(f"""
    <style>
        body {{
            background-color: {background_color};
            color: {text_color};
        }}
    </style>
""", unsafe_allow_html=True)

st.title("📈 Stock Market Prediction & Analysis")

# Multi-Company Selection
selected_companies = st.multiselect("Select Companies", list(companies.keys()), default=["Apple (AAPL)"])

def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data

if st.button("Fetch Stock Data"):
    all_data = []
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
            all_data.append(df)
    
    if all_data:
        combined_df = pd.concat(all_data)
        fig = px.line(combined_df, x=combined_df.index, y="Close", color="Company", title="Stock Trends Comparison",
                      labels={"Close": "Stock Price", "index": "Date"}, template=chart_theme)
        st.plotly_chart(fig)
    else:
        st.error("⚠️ Could not fetch stock data. API limit may have been reached!")
