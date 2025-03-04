import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Alpha Vantage API Key (Replace with your own key)
API_KEY = "EY0BHX91K5UY3W6Q"

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
st.title("📈 Beginner-Friendly Stock Market Dashboard")

# Theme Toggle
dark_mode = st.toggle("🌗 Toggle Dark/Light Mode", value=True)

# Define styles based on the mode
plot_theme = "plotly_dark" if dark_mode else "plotly_white"

# Multi-Stock Selection
selected_companies = st.multiselect("Select Companies", list(companies.keys()), default=["Apple (AAPL)"])

# Function to fetch stock data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data

# Fetch Data Button
if st.button("Fetch Stock Data"):
    all_stock_data = {}

    for company in selected_companies:
        symbol = companies[company]
        stock_data = get_stock_data(symbol)

        if "Time Series (5min)" in stock_data:
            df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index")
            df = df.astype(float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df["Company"] = company
            df.columns = ["Open", "High", "Low", "Close", "Volume", "Company"]
            all_stock_data[company] = df
        else:
            st.warning(f"⚠️ Could not fetch data for {company}. API limit may have been reached!")

    # Combine all stocks into one DataFrame
    if all_stock_data:
        combined_df = pd.concat(all_stock_data.values())

        for company, df in all_stock_data.items():
            st.subheader(f"📊 {company} Stock Details")
            starting_price = df.iloc[0]["Open"]
            current_price = df.iloc[-1]["Close"]
            highest_price = df["High"].max()

            st.metric(label="Starting Price", value=f"${starting_price:.2f}")
            st.metric(label="Current Price", value=f"${current_price:.2f}")
            st.metric(label="Highest Price of the Day", value=f"${highest_price:.2f}")

        # Plot all selected stocks
        fig = px.line(
            combined_df,
            x=combined_df.index,
            y="Close",
            color="Company",
            title="Stock Trends Comparison",
            labels={"Close": "Stock Price", "index": "Date"},
            template=plot_theme
        )
        st.plotly_chart(fig)
