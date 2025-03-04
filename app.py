import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# Set Page Configuration
st.set_page_config(page_title="Stock Market App", layout="wide")

# API Key
API_KEY = "MPPUU3T1XG48JIOK"

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

# Initialize session state for alerts and alert history
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "alert_history" not in st.session_state:
    st.session_state.alert_history = []

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📊 Stock Market Dashboard", "🚨 Price Alert", "🔄 Stock Comparison"])

# Home Page
if page == "🏠 Home":
    st.image("https://source.unsplash.com/featured/?stocks,market", use_column_width=True)

# Stock Market Dashboard
if page == "📊 Stock Market Dashboard":
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

    # Display Stock Data & Insights
    if "stock_data" in st.session_state:
        df = st.session_state.stock_data
        current_price = df["Close"].iloc[-1]
        highest_price = df["High"].max()
        starting_price = df["Open"].iloc[0]

        st.subheader(f"📈 {selected_company} Stock Details")
        st.info(f"💰 *Current Price:* ${current_price:.2f}")
        st.success(f"📈 *Highest Price:* ${highest_price:.2f}")
        st.warning(f"🔽 *Starting Price:* ${starting_price:.2f}")

        # Intraday Graph
        fig = px.line(df, x=df.index, y="Close", title="📊 Intraday Stock Prices", labels={"Close": "Stock Price"}, template="plotly_dark")
        st.plotly_chart(fig)

# Price Alert
elif page == "🚨 Price Alert":
    st.title("🚨 Price Alert")

    # Set Alert
    st.subheader("🔔 Set Price Alert")
    selected_company = st.selectbox("📌 Choose a Company for Alerts", list(companies.keys()))
    alert_price = st.number_input("💰 Enter Alert Price", min_value=0.0, format="%.2f")
    alert_type = st.radio("🔔 Alert Type", ["Above", "Below"])
    
    if st.button("✅ Set Alert"):
        # Add alert to session state
        st.session_state.alerts.append({
            "company": selected_company,
            "symbol": companies[selected_company],
            "alert_price": alert_price,
            "alert_type": alert_type
        })
        st.success(f"🚀 Alert set for {selected_company} when price is {alert_type} ${alert_price:.2f}")

    # Display Active Alerts
    st.subheader("📋 Active Alerts")
    if st.session_state.alerts:
        for i, alert in enumerate(st.session_state.alerts):
            st.write(f"{i + 1}. {alert['company']} - Alert when price is {alert['alert_type']} ${alert['alert_price']:.2f}")
            if st.button(f"❌ Clear Alert {i + 1}"):
                st.session_state.alerts.pop(i)
                st.session_state.rerun = True  # Trigger rerun
    else:
        st.info("No active alerts.")

    # Clear All Alerts
    if st.button("❌ Clear All Alerts"):
        st.session_state.alerts = []
        st.session_state.alert_history = []
        st.session_state.rerun = True  # Trigger rerun

    # Check Alerts
    st.subheader("🔍 Check Alerts")
    if st.button("🔔 Check Alerts Now"):
        for alert in st.session_state.alerts:
            stock_data = get_stock_data(alert["symbol"])
            if "Time Series (5min)" in stock_data:
                df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index").astype(float)
                if "Close" in df.columns:
                    current_price = df["Close"].iloc[-1]

                    # Check if alert condition is met
                    if (alert["alert_type"] == "Above" and current_price >= alert["alert_price"]) or \
                       (alert["alert_type"] == "Below" and current_price <= alert["alert_price"]):
                        st.success(f"🚨 Alert triggered for {alert['company']}! Current price: ${current_price:.2f} (Target: {alert['alert_type']} ${alert['alert_price']:.2f})")
                        # Add to alert history
                        st.session_state.alert_history.append({
                            "company": alert["company"],
                            "symbol": alert["symbol"],
                            "alert_price": alert["alert_price"],
                            "alert_type": alert["alert_type"],
                            "triggered_price": current_price,
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                    else:
                        st.info(f"⏳ {alert['company']} is at ${current_price:.2f}. Waiting for price to go {alert['alert_type']} ${alert['alert_price']:.2f}.")
                else:
                    st.warning(f"⚠ The 'Close' column is missing in the data for {alert['company']}.")
            else:
                st.warning(f"⚠ Could not fetch data for {alert['company']}.")

    # Display Alert History
    st.subheader("📜 Alert History")
    if st.session_state.alert_history:
        for alert in st.session_state.alert_history:
            st.write(f"🚨 {alert['company']} - Price reached {alert['alert_type']} ${alert['alert_price']:.2f} at {alert['time']} (Triggered Price: ${alert['triggered_price']:.2f})")
    else:
        st.info("No alerts have been triggered yet.")

# Stock Comparison
elif page == "🔄 Stock Comparison":
    st.title("🔄 Compare Stock Performance")

    stock1 = st.selectbox("📌 Select First Company", list(companies.keys()), key="stock1")
    stock2 = st.selectbox("📌 Select Second Company", list(companies.keys()), key="stock2")

    if st.button("🔍 Compare Stocks"):
        stock1_data = get_stock_data(companies[stock1])
        stock2_data = get_stock_data(companies[stock2])

        if "Time Series (5min)" in stock1_data and "Time Series (5min)" in stock2_data:
            df1 = pd.DataFrame.from_dict(stock1_data["Time Series (5min)"], orient="index").astype(float)
            df1.index = pd.to_datetime(df1.index)
            df1 = df1.sort_index()
            df1.columns = ["Open", "High", "Low", "Close", "Volume"]

            df2 = pd.DataFrame.from_dict(stock2_data["Time Series (5min)"], orient="index").astype(float)
            df2.index = pd.to_datetime(df2.index)
            df2 = df2.sort_index()
            df2.columns = ["Open", "High", "Low", "Close", "Volume"]

            comparison_df = pd.DataFrame({
                "Time": df1.index,
                stock1: df1["Close"],
                stock2: df2["Close"]
            })
            fig_compare = px.line(comparison_df, x="Time", y=[stock1, stock2], title="📊 Stock Price Comparison", template="plotly_dark")
            st.plotly_chart(fig_compare)
        else:
            st.warning("⚠ Unable to fetch stock data for comparison.")

# Rerun the app if needed
if "rerun" in st.session_state and st.session_state.rerun:
    st.session_state.rerun = False
    st.experimental_rerun()  # Use st.rerun() if available
