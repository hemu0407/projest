import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Alpha Vantage API Key
API_KEY = "EY0BHX91K5UY3W6Q"

# List of stock symbols for intraday trading
companies = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
}

# Streamlit UI
st.set_page_config(page_title="Intraday Stock Predictor", layout="wide")

# Select a Company
selected_company = st.selectbox("Select a Company", list(companies.keys()))
symbol = companies[selected_company]

# Get user input for investment amount
investment_amount = st.number_input("Enter the amount you want to invest ($)", min_value=10, max_value=10000, step=10)

# Function to fetch intraday stock data
def get_intraday_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=15min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data

# Fetch Data Button
if st.button("Predict Intraday Profit/Loss"):
    stock_data = get_intraday_data(symbol)

    if "Time Series (15min)" in stock_data:
        df = pd.DataFrame.from_dict(stock_data["Time Series (15min)"], orient="index")
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]

        # Display Current Price
        current_price = df.iloc[-1]["Close"]
        st.metric(label="📌 Current Stock Price", value=f"${current_price:.2f}")

        # Prepare Data for Machine Learning Model
        df["Minutes"] = np.arange(len(df))  # Convert timestamps to numerical values
        X = df["Minutes"].values.reshape(-1, 1)
        y = df["Close"].values.reshape(-1, 1)

        # Train Model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predict Stock Price for the Next Few Hours
        future_minutes = np.array(range(df["Minutes"].max() + 1, df["Minutes"].max() + 10)).reshape(-1, 1)
        predicted_prices = model.predict(future_minutes)

        # Display Predictions
        future_df = pd.DataFrame({"Minutes": future_minutes.flatten(), "Predicted Price": predicted_prices.flatten()})
        future_df["Time"] = pd.date_range(start=df.index.max(), periods=len(future_df), freq="15min")

        fig = px.line(future_df, x="Time", y="Predicted Price", title=f"Intraday Stock Prediction ({selected_company})")
        st.plotly_chart(fig)

        # Calculate Profit and Loss Separately
        shares_to_buy = investment_amount / current_price
        predicted_high = max(predicted_prices)[0]  # Maximum predicted price
        predicted_low = min(predicted_prices)[0]   # Minimum predicted price

        profit_amount = (predicted_high - current_price) * shares_to_buy
        loss_amount = (predicted_low - current_price) * shares_to_buy

        # Profit Section
        if profit_amount > 0:
            st.success(f"✅ **Potential Profit: ${profit_amount:.2f}** if stock reaches predicted high of ${predicted_high:.2f}")
        else:
            st.info("⚖️ **Neutral trend detected. No significant profit expected.**")

        # Loss Section
        if loss_amount < 0:
            st.error(f"⚠️ **Potential Loss: ${abs(loss_amount):.2f}** if stock drops to predicted low of ${predicted_low:.2f}")

        # Final Recommendation
        if profit_amount > abs(loss_amount):
            st.success("📈 **Recommended: Buy Now. Market trend shows a potential uptrend.**")
        else:
            st.warning("📉 **Not Recommended: High risk of loss detected.**")

    else:
        st.error("⚠️ Could not fetch stock data. API limit may have been reached!")
