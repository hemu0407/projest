import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Alpha Vantage API Key
API_KEY = "EY0BHX91K5UY3W6Q"

# List of companies and their stock symbols
companies = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
}

# Streamlit UI
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

# Dark/Light Mode Toggle
dark_mode = st.toggle("🌗 Toggle Dark/Light Mode", value=True)

# Define styles based on the mode
if dark_mode:
    background_color = "#1E1E1E"
    text_color = "#FFFFFF"
    plot_theme = "plotly_dark"
else:
    background_color = "#F0F0F0"
    text_color = "#000000"
    plot_theme = "plotly_white"

# Apply custom styles
st.markdown(
    f"""
    <style>
        body {{
            background-color: {background_color};
            color: {text_color};
        }}
        .stApp {{
            background-color: {background_color};
            color: {text_color};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Dropdown for company selection
selected_company = st.selectbox("Select a Company", list(companies.keys()))

# Function to fetch stock data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data

# Fetch Data Button
if st.button("Fetch Stock Data"):
    symbol = companies[selected_company]
    stock_data = get_stock_data(symbol)

    if "Time Series (Daily)" in stock_data:
        df = pd.DataFrame.from_dict(stock_data["Time Series (Daily)"], orient="index")
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]

        # Display Key Stats
        starting_price = df.iloc[0]["Open"]
        current_price = df.iloc[-1]["Close"]
        highest_price = df["High"].max()

        st.metric(label="📌 Starting Price", value=f"${starting_price:.2f}")
        st.metric(label="📌 Current Price", value=f"${current_price:.2f}")
        st.metric(label="📌 Highest Price", value=f"${highest_price:.2f}")

        # Moving Average
        df["SMA_10"] = df["Close"].rolling(window=10).mean()

        # Plot Stock Trend
        fig = px.line(df, x=df.index, y=["Close", "SMA_10"], title=f"{selected_company} Stock Trends",
                      labels={"value": "Stock Price", "index": "Date"},
                      template=plot_theme)
        st.plotly_chart(fig)

        # Machine Learning Model (Linear Regression)
        df["Days"] = (df.index - df.index.min()).days
        X = df["Days"].values.reshape(-1, 1)
        y = df["Close"].values.reshape(-1, 1)

        # Split Data for Training
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predict Future Prices
        future_days = 30
        future_X = np.array(range(df["Days"].max() + 1, df["Days"].max() + future_days + 1)).reshape(-1, 1)
        future_prices = model.predict(future_X)

        # Display Future Price Prediction
        future_df = pd.DataFrame({"Days": future_X.flatten(), "Predicted Price": future_prices.flatten()})
        future_df["Date"] = pd.date_range(start=df.index.max(), periods=future_days + 1, freq="D")[1:]
        
        fig_future = px.line(future_df, x="Date", y="Predicted Price",
                             title=f"Predicted Stock Price for {selected_company} (Next {future_days} days)",
                             labels={"Predicted Price": "Stock Price ($)", "Date": "Date"},
                             template=plot_theme)
        st.plotly_chart(fig_future)

        # Investment Calculator
        st.subheader("💰 Investment Profit/Loss Calculator")

        investment = st.slider("Enter the amount you want to invest ($)", min_value=10, max_value=10000, step=10)
        shares_to_buy = investment / current_price
        predicted_price = future_prices[-1][0]
        profit_loss_percentage = ((predicted_price - current_price) / current_price) * 100
        profit_loss_amount = (predicted_price - current_price) * shares_to_buy

        st.metric(label="📈 Predicted Price", value=f"${predicted_price:.2f}")
        st.metric(label="📊 Potential Profit/Loss (%)", value=f"{profit_loss_percentage:.2f}%")
        st.metric(label="💰 Expected Profit/Loss ($)", value=f"${profit_loss_amount:.2f}")

        # Buy/Sell Recommendation
        if profit_loss_percentage > 5:
            st.success(f"✅ **Good time to invest!** Expected Profit: ${profit_loss_amount:.2f}")
            st.markdown("**📅 Suggested Selling Time: In 30 Days**")
        elif profit_loss_percentage < -5:
            st.warning(f"⚠️ **High risk!** Expected Loss: ${profit_loss_amount:.2f}")
            st.markdown("❌ **Consider waiting before investing.**")
        else:
            st.info(f"⚖️ **Neutral Market**. Expected Change: {profit_loss_percentage:.2f}%")

    else:
        st.error("⚠️ Could not fetch stock data. API limit may have been reached!")
