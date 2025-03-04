import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from sklearn.svm import SVR
import numpy as np

# Alpha Vantage API Key
API_KEY = "3N5V8TAO9YIDT59Q"

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
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

# Initialize session state for storing stock data and theme mode
if "stock_data" not in st.session_state:
    st.session_state.stock_data = None
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # Default theme

# Theme Toggle
dark_mode = st.toggle("\U0001F317 Toggle Dark/Light Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode
plot_theme = "plotly_dark" if st.session_state.dark_mode else "plotly_white"

# Company selection
st.title("\U0001F4CA Stock Market Dashboard")
st.markdown("---")
selected_company = st.selectbox("\U0001F4CC Select a Company", list(companies.keys()))

# Function to fetch stock data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data

# Fetch data button
if st.button("\U0001F50D Fetch Stock Data"):
    stock_data = get_stock_data(companies[selected_company])
    if "Time Series (5min)" in stock_data:
        df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index")
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        st.session_state.stock_data = df  # Store in session state
    else:
        st.warning(f"⚠ Could not fetch data for {selected_company}. API limit may have been reached!")

# Display stock data if available
if st.session_state.stock_data is not None:
    df = st.session_state.stock_data
    current_price = df["Close"].iloc[-1]
    
    st.subheader(f"📈 {selected_company} Stock Details")
    st.info(f"💰 *Current Price:* ${current_price:.2f}")

    # Stock Price Alert
    st.subheader("\U0001F514 Stock Price Alert")
    price_threshold = st.number_input("Set Price Alert", min_value=0.0, value=current_price, step=0.1)
    if current_price >= price_threshold:
        st.success(f"\U0001F680 Alert! {selected_company} has reached ${price_threshold}!")
    
    # Stock Comparison Tool
    st.subheader("🔄 Compare Stocks")
    compare_company = st.selectbox("Select another company to compare", [c for c in companies.keys() if c != selected_company])
    
    compare_data = get_stock_data(companies[compare_company])
    if "Time Series (5min)" in compare_data:
        df_compare = pd.DataFrame.from_dict(compare_data["Time Series (5min)"], orient="index")
        df_compare = df_compare.astype(float)
        df_compare.index = pd.to_datetime(df_compare.index)
        df_compare = df_compare.sort_index()
        df_compare.columns = ["Open", "High", "Low", "Close", "Volume"]
        
        df_combined = pd.DataFrame({
            f"{selected_company} Close": df["Close"],
            f"{compare_company} Close": df_compare["Close"]
        }).dropna()
        
        fig_compare = px.line(df_combined, x=df_combined.index, y=df_combined.columns,
                              title=f"📊 {selected_company} vs {compare_company}", template=plot_theme)
        st.plotly_chart(fig_compare)
    
    # News Feed
    st.subheader("📰 Latest News")
    news_url = f"https://newsapi.org/v2/everything?q={companies[selected_company]}&apiKey=YOUR_NEWS_API_KEY"
    news_response = requests.get(news_url).json()
    
    if "articles" in news_response:
        for article in news_response["articles"][:5]:
            st.markdown(f"**[{article['title']}]({article['url']})**")
            st.write(article["description"])
