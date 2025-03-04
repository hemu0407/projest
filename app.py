import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from sklearn.svm import SVR
import numpy as np

# Alpha Vantage API Key
API_KEY = "CIGY6168CBD8UPYV"

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

# Initialize session state for storing stock data
if "stock_data" not in st.session_state:
    st.session_state.stock_data = None

# Theme Toggle
dark_mode = st.toggle("🌗 Toggle Dark/Light Mode", value=True)
plot_theme = "plotly_dark" if dark_mode else "plotly_white"

# Company selection
selected_company = st.selectbox("Select a Company", list(companies.keys()))

# Function to fetch stock data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data

# Fetch data button
if st.button("Fetch Stock Data"):
    stock_data = get_stock_data(companies[selected_company])

    if "Time Series (5min)" in stock_data:
        df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index")
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        st.session_state.stock_data = df  # Store in session state
    else:
        st.warning(f"⚠️ Could not fetch data for {selected_company}. API limit may have been reached!")

# Display stock data if available
if st.session_state.stock_data is not None:
    df = st.session_state.stock_data
    current_price = df["Close"].iloc[-1]
    highest_price = df["High"].max()
    starting_price = df["Open"].iloc[0]

    st.subheader(f"📈 {selected_company} Stock Details")
    st.write(f"**Current Price:** ${current_price:.2f}")
    st.write(f"**Highest Price:** ${highest_price:.2f}")
    st.write(f"**Starting Price:** ${starting_price:.2f}")

    # Display Intraday Graph
    fig = px.line(df, x=df.index, y="Close", title="📊 Intraday Stock Prices", labels={"Close": "Stock Price"}, template=plot_theme)
    st.plotly_chart(fig)

    # Long-Term Graph (Dummy Data for Demonstration)
    df_long = df.resample("D").mean().dropna()  # Resampling for daily mean (mock)
    fig_long = px.line(df_long, x=df_long.index, y="Close", title="📊 Long-Term Stock Trend", labels={"Close": "Stock Price"}, template=plot_theme)
    st.plotly_chart(fig_long)

    # Ask for investment amount
    num_stocks = st.number_input("Enter number of stocks to buy", min_value=1, step=1)

    # Get Results button
    if st.button("Get Results"):
        total_investment = num_stocks * current_price

        # Prepare data for SVM prediction
        df["Time"] = np.arange(len(df))  # Convert time into numerical format
        X = df["Time"].values.reshape(-1, 1)
        y = df["Close"].values.reshape(-1, 1)

        # Train SVM model
        model = SVR(kernel="rbf", C=100, gamma=0.1, epsilon=0.1)
        model.fit(X, y.ravel())

        # Predict future price
        future_time = np.array([[X[-1][0] + 10]])  # Predict 10 steps ahead
        predicted_price = model.predict(future_time)[0]

        # Calculate profit/loss percentage
        profit_loss_percentage = ((predicted_price - current_price) / current_price) * 100
        potential_profit_loss = num_stocks * (predicted_price - current_price)

        st.subheader("📊 Investment Prediction")

        if profit_loss_percentage > 0:
            st.success(f"✅ **Good Investment!** Estimated profit: **{profit_loss_percentage:.2f}%**")
            st.write(f"💰 **Projected Profit:** ${potential_profit_loss:.2f}")
            st.write(f"📌 **Best Time to Sell:** In {10} time intervals")
        else:
            st.error(f"❌ **Don't Invest!** Estimated loss: **{abs(profit_loss_percentage):.2f}%**")
            st.write(f"⚠️ **Potential Loss:** ${abs(potential_profit_loss):.2f}")

