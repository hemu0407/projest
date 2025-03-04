import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Simulate stock data (replace this with your actual data fetching logic)
def get_stock_data(symbol):
    # Example: Generate random stock data
    dates = pd.date_range(start="2023-10-01", periods=100, freq="D")
    prices = np.cumsum(np.random.randn(100)) + 100  # Simulated stock prices
    df = pd.DataFrame({"Date": dates, "Close": prices})
    df.set_index("Date", inplace=True)
    return df

# Stock Market Dashboard
if page == "📊 Stock Market Dashboard":
    st.title("📊 Stock Market Dashboard")
    
    selected_company = st.selectbox("📌 Select a Company", list(companies.keys()))

    if st.button("🔍 Fetch Stock Data"):
        df = get_stock_data(companies[selected_company])
        st.session_state.stock_data = df

    if "stock_data" in st.session_state:
        df = st.session_state.stock_data
        current_price = df["Close"].iloc[-1]
        highest_price = df["Close"].max()
        starting_price = df["Close"].iloc[0]

        st.subheader(f"📈 {selected_company} Stock Details")
        st.info(f"💰 *Current Price:* ${current_price:.2f}")
        st.success(f"📈 *Highest Price:* ${highest_price:.2f}")
        st.warning(f"🔽 *Starting Price:* ${starting_price:.2f}")

        # Intraday Graph
        fig = px.line(df, x=df.index, y="Close", title="📊 Historical Stock Prices", labels={"Close": "Stock Price"}, template="plotly_dark")
        st.plotly_chart(fig)

        # Investment Calculator
        num_stocks = st.number_input("🛒 Enter number of stocks to buy", min_value=1, step=1)

        if st.button("📊 Fetch Profit/Loss and Future Prediction"):
            total_cost = num_stocks * current_price
            st.info(f"💰 *Total Investment:* ${total_cost:.2f}")

            # **📈 Future Trend Prediction (Moving Averages)**
            st.subheader("📈 Future Stock Price Prediction (Moving Averages)")

            # Calculate moving average
            window_size = 10  # Adjust window size as needed
            df["Moving Avg"] = df["Close"].rolling(window=window_size).mean()

            # Predict future prices using moving average
            future_prices = df["Moving Avg"].iloc[-window_size:].values
            future_dates = pd.date_range(start=df.index[-1], periods=window_size + 1, freq="D")[1:]

            future_df = pd.DataFrame({"Date": future_dates, "Predicted Price": future_prices})
            fig_pred = px.line(future_df, x="Date", y="Predicted Price", title="📈 Predicted Stock Prices (Next 10 Days)", template="plotly_dark")
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
                
