import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

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

        if st.button("📊 Fetch Profit/Loss and Future Prediction"):
            total_cost = num_stocks * current_price
            st.info(f"💰 *Total Investment:* ${total_cost:.2f}")

            # **📈 Future Trend Prediction (Moving Averages)**
            st.subheader("📈 Future Stock Price Prediction (Moving Averages)")

            # Filter data for the current day
            today = datetime.now().date()
            df_today = df[df.index.date == today]

            # Check if the market is open
            if df_today.empty:
                st.warning("⚠ Market is closed. No predictions available for today.")
            else:
                # Calculate moving average
                window_size = 10  # Adjust window size as needed
                df_today["Moving Avg"] = df_today["Close"].rolling(window=window_size).mean()

                # Predict future prices using moving average
                future_prices = df_today["Moving Avg"].iloc[-window_size:].values
                future_times = pd.date_range(start=df_today.index[-1], periods=window_size + 1, freq="5T")[1:]

                # Create future DataFrame
                future_df = pd.DataFrame({"Time": future_times, "Predicted Price": future_prices})

                # Plot the predicted prices
                fig_pred = px.line(future_df, x="Time", y="Predicted Price", title="📈 Predicted Stock Prices (Next 10 Intervals)", template="plotly_dark")
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
