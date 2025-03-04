import streamlit as st
import requests
import pandas as pd
import plotly.express as px

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

# JavaScript for Sidebar Toggle
toggle_sidebar_script = """
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

# Inject Sidebar Toggle Button
st.markdown(toggle_sidebar_script, unsafe_allow_html=True)
st.markdown('<button onclick="toggleSidebar()" style="position:fixed; top:10px; left:10px; background:#333; color:white; border:none; padding:10px 15px; cursor:pointer;">☰</button>', unsafe_allow_html=True)

# Streamlit Page Config
st.set_page_config(page_title="Stock Market App", layout="wide")

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📊 Stock Market Dashboard", "🚨 Price Alert", "🔄 Stock Comparison"])

# Function to fetch stock data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data

# Home Page
if page == "🏠 Home":
    st.image("https://source.unsplash.com/featured/?stocks,market", use_column_width=True)

# Stock Market Dashboard
elif page == "📊 Stock Market Dashboard":
    st.title("📊 Stock Market Dashboard")
    
    selected_company = st.selectbox("📌 Select a Company", list(companies.keys()))
    num_stocks = st.number_input("🛒 Enter number of stocks to buy", min_value=1, step=1)

    if st.button("🔍 Fetch Stock Data"):
        stock_data = get_stock_data(companies[selected_company])

        if "Time Series (5min)" in stock_data:
            df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index")
            df = df.astype(float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ["Open", "High", "Low", "Close", "Volume"]

            current_price = df["Close"].iloc[-1]
            total_investment = num_stocks * current_price

            st.success(f"💰 Current Price: ${current_price:.2f}")
            st.info(f"📊 Total Investment: ${total_investment:.2f}")

            fig = px.line(df, x=df.index, y="Close", title="📊 Intraday Stock Prices")
            st.plotly_chart(fig)

# Stock Price Alert
elif page == "🚨 Price Alert":
    st.title("🚨 Set a Stock Price Alert")
    
    alert_company = st.selectbox("Select a Company", list(companies.keys()), key="alert_company")
    alert_price = st.number_input("Enter Alert Price", min_value=0.0, step=0.1, format="%.2f")

    if st.button("Set Alert"):
        st.success(f"✅ Alert set for {alert_company} at ${alert_price:.2f}")

# Stock Comparison
elif page == "🔄 Stock Comparison":
    st.title("🔄 Compare Two Stocks")

    stock1 = st.selectbox("Select First Stock", list(companies.keys()), key="stock1")
    stock2 = st.selectbox("Select Second Stock", list(companies.keys()), key="stock2")

    if st.button("Compare Stocks"):
        data1 = get_stock_data(companies[stock1])
        data2 = get_stock_data(companies[stock2])

        if "Time Series (5min)" in data1 and "Time Series (5min)" in data2:
            df1 = pd.DataFrame.from_dict(data1["Time Series (5min)"], orient="index").astype(float)
            df2 = pd.DataFrame.from_dict(data2["Time Series (5min)"], orient="index").astype(float)

            df1.index = pd.to_datetime(df1.index)
            df2.index = pd.to_datetime(df2.index)

            df1.columns = ["Open", "High", "Low", "Close", "Volume"]
            df2.columns = ["Open", "High", "Low", "Close", "Volume"]

            fig = px.line(title="Stock Price Comparison")
            fig.add_scatter(x=df1.index, y=df1["Close"], mode="lines", name=stock1)
            fig.add_scatter(x=df2.index, y=df2["Close"], mode="lines", name=stock2)
            st.plotly_chart(fig)
