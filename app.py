import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from sklearn.svm import SVR
import numpy as np

# Alpha Vantage API Key
API_KEY = "LZ00UEYC5FP1SZS8"

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
if "alerts" not in st.session_state:
    st.session_state.alerts = {}

# Theme Toggle
dark_mode = st.toggle("🌗 Toggle Dark/Light Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode
plot_theme = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
st.markdown(
    f"""
    <style>
        body {{
            background-color: {'#0e1117' if dark_mode else '#f4f4f4'};
            color: {'#ffffff' if dark_mode else '#000000'};
        }}
        .stButton>button {{
            background-color: {'#1f77b4' if dark_mode else '#4caf50'};
            color: white;
            font-size: 16px;
            border-radius: 8px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Company selection
st.title("📊 Stock Market Dashboard")
st.markdown("---")
selected_company = st.selectbox("📌 Select a Company", list(companies.keys()))

# Function to fetch stock data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Fetch data button
if st.button("🔍 Fetch Stock Data"):
    stock_data = get_stock_data(companies[selected_company])

    if stock_data and "Time Series (5min)" in stock_data:
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
    highest_price = df["High"].max()
    starting_price = df["Open"].iloc[0]

    st.subheader(f"📈 {selected_company} Stock Details")
    st.info(f"💰 **Current Price:** ${current_price:.2f}")
    st.success(f"📈 **Highest Price:** ${highest_price:.2f}")
    st.warning(f"🔽 **Starting Price:** ${starting_price:.2f}")

    # Display Intraday Graph
    fig = px.line(df, x=df.index, y="Close", title="📊 Intraday Stock Prices", labels={"Close": "Stock Price"}, template=plot_theme)
    st.plotly_chart(fig)

    # Stock Price Alerts
    st.subheader("🔔 Stock Price Alerts")
    alert_price = st.number_input("Set an alert for when stock price reaches: ", min_value=0.0, step=0.1)
    if st.button("Set Alert"):
        st.session_state.alerts[selected_company] = alert_price
        st.success(f"Alert set for {selected_company} at ${alert_price:.2f}")
    
    # Stock Comparison Tool
    st.subheader("📊 Compare Stocks")
    compare_companies = st.multiselect("Select companies to compare", list(companies.keys()), default=[selected_company])
    if len(compare_companies) > 1:
        comparison_data = {}
        for company in compare_companies:
            symbol = companies[company]
            data = get_stock_data(symbol)
            if data and "Time Series (5min)" in data:
                df_temp = pd.DataFrame.from_dict(data["Time Series (5min)"], orient="index").astype(float)
                df_temp.index = pd.to_datetime(df_temp.index)
                df_temp = df_temp.sort_index()
                comparison_data[company] = df_temp["Close"].iloc[-1]
        comp_df = pd.DataFrame(list(comparison_data.items()), columns=["Company", "Current Price"])
        st.dataframe(comp_df)

    # Future trend prediction
    if st.button("📊 Get Investment Results"):
        df["Time"] = np.arange(len(df))
        X = df[["Time"]].values
        y = df["Close"].values
        model = SVR(kernel="rbf", C=100, gamma=0.05, epsilon=0.1)
        model.fit(X, y)
        future_time = np.array([[X[-1][0] + i] for i in range(1, 11)])
        future_predictions = model.predict(future_time)
        future_dates = pd.date_range(start=df.index[-1], periods=10, freq="5min")
        df_future = pd.DataFrame({"Date": future_dates, "Predicted Price": future_predictions})
        fig_future = px.line(df_future, x="Date", y="Predicted Price", title="🔮 Predicted Future Trend", template=plot_theme)
        st.plotly_chart(fig_future)
