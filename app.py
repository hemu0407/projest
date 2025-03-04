import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Set Page Configuration
st.set_page_config(page_title="Stock Market App", layout="wide")

# API Key
API_KEY = "2FBFACISUP9PL6YT"

# Stock Symbols
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

# Fetch Stock Data Function
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    return response.json()

# Initialize session state
if "alerts" not in st.session_state:
    st.session_state.alerts = []

# Custom CSS for sidebar styling
st.markdown("""
    <style>
    /* Sidebar navigation styling */
    [data-testid="stSidebarNav"] {
        padding: 20px;
    }
    /* Radio button styling */
    .st-eb {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        transition: background-color 0.3s;
    }
    .st-eb:hover {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.title("📌 Navigation")
    st.markdown("---")
    
    # Navigation radio buttons
    page = st.radio(
        "Menu",
        ["🏠 Home", "📊 Stock Market Dashboard", "🚨 Price Alert", "🔄 Stock Comparison"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ Information")
    st.info("""
    This app provides real-time stock market data, price alerts, and comparison tools.
    Data powered by Alpha Vantage API.
    """)

# Home Page
if page == "🏠 Home":
    st.title("🏠 Home")
    st.image("https://source.unsplash.com/featured/?stocks,market", use_column_width=True)

# Stock Market Dashboard
elif page == "📊 Stock Market Dashboard":
    st.title("📊 Stock Market Dashboard")
    
    selected_company = st.selectbox("📌 Select a Company", list(companies.keys()))

    if st.button("🔍 Fetch Stock Data"):
        stock_data = get_stock_data(companies[selected_company])

        if "Time Series (5min)" in stock_data:
            df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index").astype(float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ["Open", "High", "Low", "Close", "Volume"]
            st.session_state.stock_data = df
        else:
            st.warning(f"⚠ Could not fetch data for {selected_company}.")

    if "stock_data" in st.session_state:
        df = st.session_state.stock_data
        current_price = df["Close"].iloc[-1]
        highest_price = df["High"].max()
        starting_price = df["Open"].iloc[0]

        st.subheader(f"📈 {selected_company} Stock Details")
        cols = st.columns(3)
        cols[0].info(f"💰 Current Price: ${current_price:.2f}")
        cols[1].success(f"📈 Highest Price: ${highest_price:.2f}")
        cols[2].warning(f"🔽 Starting Price: ${starting_price:.2f}")

        fig = px.line(df, x=df.index, y="Close", title="📊 Intraday Stock Prices", 
                     labels={"Close": "Stock Price"}, template="plotly_dark")
        st.plotly_chart(fig)

        # Investment Calculator
        st.subheader("💵 Investment Calculator")
        num_stocks = st.number_input("🛒 Enter number of stocks to buy", min_value=1, step=1)

        if st.button("📊 Show Profit/Loss Prediction"):
            total_cost = num_stocks * current_price
            st.info(f"💰 Total Investment: ${total_cost:.2f}")

            # Simplified prediction logic
            st.subheader("📈 Price Movement Prediction")
            avg_change = df["Close"].pct_change().mean() * 100
            prediction = current_price * (1 + avg_change/100)
            
            if avg_change > 0:
                st.success(f"Predicted next hour: ▲ ${prediction:.2f} ({avg_change:.2f}% gain)")
            else:
                st.error(f"Predicted next hour: ▼ ${prediction:.2f} ({abs(avg_change):.2f}% loss)")

# Price Alert Section
elif page == "🚨 Price Alert":
    st.title("🚨 Price Alert")

    if "alerts" not in st.session_state:
        st.session_state.alerts = []

    # Set Alert
    with st.form("alert_form"):
        st.subheader("🔔 Set New Alert")
        selected_company = st.selectbox("📌 Choose a Company", list(companies.keys()))
        alert_price = st.number_input("💰 Enter Alert Price", min_value=0.0, format="%.2f")
        if st.form_submit_button("✅ Set Alert"):
            st.session_state.alerts.append({
                "company": selected_company,
                "symbol": companies[selected_company],
                "alert_price": alert_price
            })
            st.success(f"🚀 Alert set for {selected_company} at ${alert_price:.2f}")

    # Active Alerts
    st.subheader("📋 Active Alerts")
    if st.session_state.alerts:
        for i, alert in enumerate(st.session_state.alerts):
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(f"{i + 1}. {alert['company']} - Alert at ${alert['alert_price']:.2f}")
            with col2:
                if st.button(f"❌ Clear {i+1}"):
                    st.session_state.alerts.pop(i)
                    st.experimental_rerun()
    else:
        st.info("No active alerts.")

# Stock Comparison Section
elif page == "🔄 Stock Comparison":
    st.title("🔄 Stock Comparison")

    col1, col2 = st.columns(2)
    with col1:
        stock1 = st.selectbox("📌 Select First Company", list(companies.keys()), key="stock1")
    with col2:
        stock2 = st.selectbox("📌 Select Second Company", 
                            [c for c in companies.keys() if c != stock1], 
                            key="stock2")

    if st.button("🔍 Compare Stocks"):
        with st.spinner("Fetching comparison data..."):
            stock1_data = get_stock_data(companies[stock1])
            stock2_data = get_stock_data(companies[stock2])

            if "Time Series (5min)" in stock1_data and "Time Series (5min)" in stock2_data:
                df1 = pd.DataFrame(stock1_data["Time Series (5min)"]).T.astype(float)
                df2 = pd.DataFrame(stock2_data["Time Series (5min)"]).T.astype(float)
                
                comparison_df = pd.DataFrame({
                    stock1: df1["4. close"],
                    stock2: df2["4. close"]
                }).sort_index(ascending=False).iloc[:50]  # Last 50 data points

                st.subheader("📊 Price Trend Comparison")
                fig = px.line(comparison_df, 
                             title="Recent Price Movement Comparison",
                             template="plotly_dark")
                st.plotly_chart(fig)

                # Performance Metrics
                st.subheader("📈 Performance Metrics")
                metrics = pd.DataFrame({
                    "Metric": ["Current Price", "24h Change", "Volatility"],
                    stock1: [
                        comparison_df[stock1].iloc[0],
                        comparison_df[stock1].pct_change().mean() * 100,
                        comparison_df[stock1].std()
                    ],
                    stock2: [
                        comparison_df[stock2].iloc[0],
                        comparison_df[stock2].pct_change().mean() * 100,
                        comparison_df[stock2].std()
                    ]
                })
                st.dataframe(metrics.set_index("Metric"), use_container_width=True)
            else:
                st.error("⚠ Failed to fetch comparison data")
