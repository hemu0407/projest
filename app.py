import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.svm import SVR

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

# Initialize session state for alerts
if "alerts" not in st.session_state:
    st.session_state.alerts = []

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

        # Investment Calculator
        num_stocks = st.number_input("🛒 Enter number of stocks to buy", min_value=1, step=1)
        total_cost = num_stocks * current_price
        st.info(f"💰 *Total Investment:* ${total_cost:.2f}")

        # Future Trend Prediction (SVR)
        st.subheader("📈 Future Stock Price Prediction")

        df["Time"] = np.arange(len(df))
        X = df[["Time"]].values
        y = df["Close"].values

        model = SVR(kernel="rbf", C=1e3, gamma=0.1)
        model.fit(X, y)

        future_times = np.arange(len(df) + 10).reshape(-1, 1)
        future_prices = model.predict(future_times)

        future_df = pd.DataFrame({"Time": future_times.flatten(), "Predicted Price": future_prices})
        fig_pred = px.line(future_df, x="Time", y="Predicted Price", title="📈 Predicted Stock Prices (Next 10 Ticks)", template="plotly_dark")
        st.plotly_chart(fig_pred)

        # Calculate Profit/Loss
        future_price = future_prices[-1]
        future_value = num_stocks * future_price
        profit_loss = future_value - total_cost
        profit_loss_percentage = (profit_loss / total_cost) * 100

        if profit_loss > 0:
            st.success(f"📈 *Profit:* ${profit_loss:.2f} ({profit_loss_percentage:.2f}%)")
            st.info(f"💡 *Recommendation:* Consider selling when the price reaches ${future_price:.2f} to maximize profit.")
        else:
            st.error(f"📉 *Loss:* ${abs(profit_loss):.2f} ({abs(profit_loss_percentage):.2f}%)")
            st.warning(f"💡 *Recommendation:* It might not be the best time to buy. Consider waiting for a better price.")

# Price Alert
elif page == "🚨 Price Alert":
    st.title("🚨 Price Alert")

    # Set Alert
    st.subheader("🔔 Set Price Alert")
    selected_company = st.selectbox("📌 Choose a Company for Alerts", list(companies.keys()))
    alert_price = st.number_input("💰 Enter Alert Price", min_value=0.0, format="%.2f")
    
    if st.button("✅ Set Alert"):
        # Add alert to session state
        st.session_state.alerts.append({
            "company": selected_company,
            "symbol": companies[selected_company],
            "alert_price": alert_price
        })
        st.success(f"🚀 Alert set for {selected_company} at ${alert_price:.2f}")

    # Display Active Alerts
    st.subheader("📋 Active Alerts")
    if st.session_state.alerts:
        for i, alert in enumerate(st.session_state.alerts):
            st.write(f"{i + 1}. {alert['company']} - Alert at ${alert['alert_price']:.2f}")
            if st.button(f"❌ Clear Alert {i + 1}"):
                st.session_state.alerts.pop(i)
                st.session_state.rerun = True  # Trigger rerun
    else:
        st.info("No active alerts.")

    # Check Alerts
    st.subheader("🔍 Check Alerts")
    if st.button("🔔 Check Alerts Now"):
        for alert in st.session_state.alerts:
            stock_data = get_stock_data(alert["symbol"])
            if "Time Series (5min)" in stock_data:
                df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index").astype(float)
                if "Close" in df.columns:
                    current_price = df["Close"].iloc[-1]

                    if current_price >= alert["alert_price"]:
                        st.success(f"🚨 Alert triggered for {alert['company']}! Current price: ${current_price:.2f} (Target: ${alert['alert_price']:.2f})")
                    else:
                        st.info(f"⏳ {alert['company']} is at ${current_price:.2f}. Waiting to reach ${alert['alert_price']:.2f}.")
                else:
                    st.warning(f"⚠ The 'Close' column is missing in the data for {alert['company']}.")
            else:
                st.warning(f"⚠ Could not fetch data for {alert['company']}.")

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
    if hasattr(st, "experimental_rerun"):  # Check if st.experimental_rerun is available
        st.experimental_rerun()
    elif hasattr(st, "rerun"):  # Check if st.rerun is available
        st.rerun()
    else:
        st.warning("⚠ Rerun functionality is not available in your Streamlit version. Please upgrade Streamlit.")
