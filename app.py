import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.svm import SVR
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
st.set_page_config(page_title="Stock Predictor", layout="wide")
st.title("📈 Stock Predictor - Intraday Analysis")

# Select a Company
selected_company = st.selectbox("Select a Company", list(companies.keys()))
symbol = companies[selected_company]

# Function to fetch intraday stock data
def get_intraday_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=15min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    return response.json()

# Fetch Data Button
if st.button("🔍 Fetch Stock Data"):
    stock_data = get_intraday_data(symbol)

    if "Time Series (15min)" in stock_data:
        df = pd.DataFrame.from_dict(stock_data["Time Series (15min)"], orient="index")
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]

        # Display Current Price
        current_price = df.iloc[-1]["Close"]
        highest_price = df["High"].max()
        opening_price = df.iloc[0]["Open"]

        col1, col2, col3 = st.columns(3)
        col1.metric(label="📌 Current Price", value=f"${current_price:.2f}")
        col2.metric(label="📈 Highest Price Today", value=f"${highest_price:.2f}")
        col3.metric(label="🏁 Opening Price", value=f"${opening_price:.2f}")

        # Display Intraday Graph
        st.subheader("📊 Intraday Stock Price Trend")
        fig = px.line(df, x=df.index, y="Close", title=f"📈 {selected_company} Intraday Trend")
        st.plotly_chart(fig)

        # Ask user how many stocks they want to buy
        stocks_to_buy = st.slider("Select the number of stocks to buy", min_value=1, max_value=1000, value=10)

        # Calculate Total Investment
        total_investment = stocks_to_buy * current_price
        st.info(f"💰 **Total Investment: ${total_investment:.2f}**")

        # Prepare Data for Machine Learning Model (SVM)
        df["Minutes"] = np.arange(len(df))
        X = df["Minutes"].values.reshape(-1, 1)
        y = df["Close"].values.reshape(-1, 1)

        # Train Model with SVM
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = SVR(kernel="rbf", C=1000, gamma=0.1)
        model.fit(X_train, y_train.ravel())

        # Predict Future Stock Prices
        future_minutes = np.array(range(df["Minutes"].max() + 1, df["Minutes"].max() + 10)).reshape(-1, 1)
        predicted_prices = model.predict(future_minutes)

        # Display Predicted Prices
        st.subheader("📊 Future Stock Price Prediction")
        future_df = pd.DataFrame({"Minutes": future_minutes.flatten(), "Predicted Price": predicted_prices.flatten()})
        future_df["Time"] = pd.date_range(start=df.index.max(), periods=len(future_df), freq="15min")

        fig_pred = px.line(future_df, x="Time", y="Predicted Price", title=f"📈 Predicted Stock Prices for {selected_company}")
        st.plotly_chart(fig_pred)

        # Calculate Profit and Loss
        predicted_high = max(predicted_prices)  # Maximum predicted price
        predicted_low = min(predicted_prices)   # Minimum predicted price

        profit_per_stock = predicted_high - current_price
        loss_per_stock = predicted_low - current_price

        total_profit = profit_per_stock * stocks_to_buy
        total_loss = loss_per_stock * stocks_to_buy

        profit_percentage = (profit_per_stock / current_price) * 100
        loss_percentage = abs((loss_per_stock / current_price) * 100)

        # Display only Profit OR Loss (not both)
        if total_profit > 0:
            st.success(f"✅ **Potential Profit: ${total_profit:.2f} ({profit_percentage:.2f}%)** if stock reaches predicted high of ${predicted_high:.2f}")
            best_sell_time = future_df.loc[future_df["Predicted Price"].idxmax(), "Time"]
            st.write(f"🕒 **Best Time to Sell (Expected High):** {best_sell_time.strftime('%H:%M %p')}")

        elif total_loss < 0:
            st.error(f"⚠️ **Potential Loss: ${abs(total_loss):.2f} ({loss_percentage:.2f}%)** if stock drops to predicted low of ${predicted_low:.2f}")

        # Final Recommendation
        if profit_percentage > loss_percentage:
            st.success("📈 **Recommended: Buy Now. Market trend shows a potential uptrend.**")
        else:
            st.warning("📉 **Not Recommended: High risk of loss detected. Do not invest.**")

    else:
        st.error("⚠️ Could not fetch intraday stock data!")
