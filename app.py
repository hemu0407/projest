import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from sklearn.svm import SVR
import numpy as np

# Set Page Configuration (MUST be first)
st.set_page_config(page_title="Stock Market App", layout="wide")

# API Key for Alpha Vantage
API_KEY = "MPPUU3T1XG48JIOK"

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

# Sidebar Toggle Button (☰) using JavaScript
sidebar_toggle_js = """
<script>
    function toggleSidebar() {
        var sidebar = parent.document.querySelector("[data-testid='stSidebar']");
        if (sidebar.style.display === "none") {
            sidebar.style.display = "block";
        } else {
            sidebar.style.display = "none";
        }
    }
</script>
"""

# Inject JavaScript into the page
st.markdown(sidebar_toggle_js, unsafe_allow_html=True)

# Create a floating ☰ button for the sidebar
st.markdown(
    """
    <button onclick="toggleSidebar()" 
    style="
        position:fixed;
        top:10px;
        left:10px;
        background:#333;
        color:white;
        border:none;
        padding:10px 15px;
        font-size:24px;
        cursor:pointer;
    ">☰</button>
    """,
    unsafe_allow_html=True,
)

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📊 Stock Market Dashboard", "🚨 Price Alert", "🔄 Stock Comparison"])

# Home Page
if page == "🏠 Home":
    st.image("https://source.unsplash.com/featured/?stocks,market", use_column_width=True)

# Stock Market Dashboard
elif page == "📊 Stock Market Dashboard":
    st.title("📊 Stock Market Dashboard")
    
    # Select Company
    selected_company = st.selectbox("📌 Select a Company", list(companies.keys()))

    # Fetch Stock Data Function
    def get_stock_data(symbol):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
        response = requests.get(url)
        data = response.json()
        return data

    # Fetch Data Button
    if st.button("🔍 Fetch Stock Data"):
        stock_data = get_stock_data(companies[selected_company])

        if "Time Series (5min)" in stock_data:
            df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index")
            df = df.astype(float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ["Open", "High", "Low", "Close", "Volume"]
            st.session_state.stock_data = df  # Store data in session state
        else:
            st.warning(f"⚠ Could not fetch data for {selected_company}. API limit may have been reached!")

    # Display Stock Data
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

        # Investment Calculator
        num_stocks = st.number_input("🛒 Enter number of stocks to buy", min_value=1, step=1)
        total_cost = num_stocks * current_price
        st.info(f"💰 *Total Investment:* ${total_cost:.2f}")

# Price Alert
elif page == "🚨 Price Alert":
    st.title("🚨 Set Price Alert")
    
    selected_company = st.selectbox("📌 Choose a Company for Alerts", list(companies.keys()))
    alert_price = st.number_input("🔔 Enter Alert Price", min_value=0.0, format="%.2f")
    
    if st.button("✅ Set Alert"):
        st.success(f"🚀 Alert set for {selected_company} at ${alert_price:.2f}")

# Stock Comparison
elif page == "🔄 Stock Comparison":
    st.title("🔄 Compare Stock Performance")

    # Select two stocks to compare
    stock1 = st.selectbox("📌 Select First Company", list(companies.keys()), key="stock1")
    stock2 = st.selectbox("📌 Select Second Company", list(companies.keys()), key="stock2")

    # Fetch Data for Both Stocks
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

            # Create comparison plot
            comparison_df = pd.DataFrame({
                "Time": df1.index,
                stock1: df1["Close"],
                stock2: df2["Close"]
            })
            fig_compare = px.line(comparison_df, x="Time", y=[stock1, stock2], title="📊 Stock Price Comparison", template="plotly_dark")
            st.plotly_chart(fig_compare)
        else:
            st.warning("⚠ Unable to fetch stock data for comparison.")

