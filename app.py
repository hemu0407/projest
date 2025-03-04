import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Set Page Configuration
st.set_page_config(page_title="Stock Market App", layout="wide")

# API Key
API_KEY = "2FBFACISUP9PL6YT"

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

# Initialize session state
if "alerts" not in st.session_state:
    st.session_state.alerts = []

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📊 Stock Market Dashboard", "🚨 Price Alert", "🔄 Stock Comparison"])

# Home Page
if page == "🏠 Home":
    st.image("https://source.unsplash.com/featured/?stocks,market", use_column_width=True)

# Stock Market Dashboard
elif page == "📊 Stock Market Dashboard":
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

    if "stock_data" in st.session_state:
        df = st.session_state.stock_data
        current_price = df["Close"].iloc[-1]
        highest_price = df["High"].max()
        starting_price = df["Open"].iloc[0]

        st.subheader(f"📈 {selected_company} Stock Details")
        st.info(f"💰 Current Price: ${current_price:.2f}")
        st.success(f"📈 Highest Price: ${highest_price:.2f}")
        st.warning(f"🔽 Starting Price: ${starting_price:.2f}")

        # Intraday Graph
        fig = px.line(df, x=df.index, y="Close", title="📊 Intraday Stock Prices", 
                     labels={"Close": "Stock Price"}, template="plotly_dark")
        st.plotly_chart(fig)

        # Investment Calculator
        num_stocks = st.number_input("🛒 Enter number of stocks to buy", min_value=1, step=1)

        if st.button("📊 Fetch Profit/Loss and Future Prediction"):
            total_cost = num_stocks * current_price
            st.info(f"💰 Total Investment: ${total_cost:.2f}")

            # Future Trend Prediction
            st.subheader("📈 Future Stock Price Prediction (Moving Averages)")
            today = datetime.now().date()
            df_today = df[df.index.date == today]

            if df_today.empty:
                st.warning("⚠ Market is closed. No predictions available for today.")
            else:
                window_size = 10
                df_today["Moving Avg"] = df_today["Close"].rolling(window=window_size).mean()
                future_prices = df_today["Moving Avg"].iloc[-window_size:].values
                future_times = pd.date_range(start=df_today.index[-1], periods=window_size + 1, freq="5T")[1:]

                future_df = pd.DataFrame({"Time": future_times, "Predicted Price": future_prices})
                fig_pred = px.line(future_df, x="Time", y="Predicted Price", 
                                 title="📈 Predicted Stock Prices (Next 10 Intervals)", 
                                 template="plotly_dark")
                st.plotly_chart(fig_pred)

                # Profit/Loss Calculation
                future_price = future_prices[-1]
                future_value = num_stocks * future_price
                profit_loss = future_value - total_cost
                profit_loss_percentage = (profit_loss / total_cost) * 100

                if profit_loss > 0:
                    st.success(f"📈 Profit: ${profit_loss:.2f} ({profit_loss_percentage:.2f}%)")
                    st.info(f"💡 Recommendation: Consider selling when price reaches ${future_price:.2f}")
                else:
                    st.error(f"📉 Loss: ${abs(profit_loss):.2f} ({abs(profit_loss_percentage):.2f}%)")
                    st.warning("💡 Recommendation: Wait for better entry point")

# Price Alert Section
elif page == "🚨 Price Alert":
    st.title("🚨 Price Alert")

    if "alerts" not in st.session_state:
        st.session_state.alerts = []

    # Set Alert
    st.subheader("🔔 Set Price Alert")
    selected_company = st.selectbox("📌 Choose a Company", list(companies.keys()))
    alert_price = st.number_input("💰 Enter Alert Price", min_value=0.0, format="%.2f")

    if st.button("✅ Set Alert"):
        st.session_state.alerts.append({
            "company": selected_company,
            "symbol": companies[selected_company],
            "alert_price": alert_price
        })
        st.success(f"🚀 Alert set for {selected_company} at ${alert_price:.2f}")

    # Active Alerts
    st.subheader("📋 Active Alerts")
    if st.session_state.alerts:
        for i, alert in enumerate(st.session_state.alerts):
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(f"{i + 1}. {alert['company']} - Alert at ${alert['alert_price']:.2f}")
            with col2:
                if st.button(f"❌ Clear {i+1}"):
                    st.session_state.alerts.pop(i)
                    st.experimental_rerun()
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
                        st.success(f"🚨 {alert['company']} Alert Triggered! Current: ${current_price:.2f}")
                    else:
                        st.info(f"⏳ {alert['company']} at ${current_price:.2f} (Target: ${alert['alert_price']:.2f})")
                else:
                    st.warning(f"⚠ Missing data for {alert['company']}")
            else:
                st.warning(f"⚠ Couldn't fetch data for {alert['company']}")

# Stock Comparison Section
elif page == "🔄 Stock Comparison":
    st.title("🔄 Advanced Stock Comparison")

    company_list = list(companies.keys())

    # Dynamic stock selection
    stock1 = st.selectbox("📌 Select First Company", company_list, key="stock1")
    stock2 = st.selectbox("📌 Select Second Company", 
                         [c for c in company_list if c != stock1], 
                         key="stock2")

    if st.button("🔍 Compare Stocks"):
        stock1_data = get_stock_data(companies[stock1])
        stock2_data = get_stock_data(companies[stock2])

        if "Time Series (5min)" in stock1_data and "Time Series (5min)" in stock2_data:
            # Process data
            df1 = pd.DataFrame(stock1_data["Time Series (5min)"]).T.astype(float)
            df2 = pd.DataFrame(stock2_data["Time Series (5min)"]).T.astype(float)
            df1.index = pd.to_datetime(df1.index)
            df2.index = pd.to_datetime(df2.index)

            # Price Comparison
            comparison_df = pd.DataFrame({
                stock1: df1["4. close"],
                stock2: df2["4. close"]
            }).sort_index()

            st.subheader("📊 Price Trend Comparison")
            fig = px.line(comparison_df, template="plotly_dark", 
                         title="Hourly Price Movement Comparison")
            st.plotly_chart(fig)

            # Advanced Analysis
            st.subheader("📈 Deep Analysis")
            
            # Correlation Analysis
            correlation = comparison_df[stock1].corr(comparison_df[stock2])
            st.info(f"**Correlation Coefficient:** {correlation:.2f}")
            
            if correlation > 0.8:
                st.write("💡 These stocks move **strongly together** - similar sector exposure")
            elif correlation < -0.8:
                st.write("💡 These stocks move **oppositely** - potential hedging opportunity")
            else:
                st.write("💡 **No strong correlation** - diversified exposure")

            # Volatility Analysis
            volatility = pd.DataFrame({
                "Stock": [stock1, stock2],
                "Volatility": [
                    comparison_df[stock1].pct_change().std() * 100,
                    comparison_df[stock2].pct_change().std() * 100
                ]
            })
            
            st.subheader("📉 Volatility Comparison")
            fig_vol = px.bar(volatility, x="Stock", y="Volatility", 
                            color="Stock", template="plotly_dark",
                            title="Price Volatility (Standard Deviation of Daily Returns)")
            st.plotly_chart(fig_vol)

            # Momentum Analysis
            st.subheader("🚀 Momentum Analysis")
            momentum = pd.DataFrame({
                "Stock": [stock1, stock2],
                "Last Hour Change": [
                    (comparison_df[stock1][-1] - comparison_df[stock1][-6])/comparison_df[stock1][-6] * 100,
                    (comparison_df[stock2][-1] - comparison_df[stock2][-6])/comparison_df[stock2][-6] * 100
                ]
            })
            
            fig_momentum = px.bar(momentum, x="Stock", y="Last Hour Change", 
                                 color="Stock", template="plotly_dark",
                                 title="Percentage Change in Last Hour")
            st.plotly_chart(fig_momentum)

            # Predictive Insights
            st.subheader("🔮 Predictive Insights")
            if correlation > 0.7 and volatility[volatility['Stock'] == stock1]['Volatility'].values[0] > 3:
                st.success(f"**Trading Opportunity:** Consider paired trading strategy for {stock1} and {stock2}")
            elif momentum["Last Hour Change"].max() > 2:
                st.info(f"**Short-Term Play:** {momentum.loc[momentum['Last Hour Change'].idxmax()]['Stock']} showing strong momentum")
            else:
                st.warning("**Neutral Outlook:** No strong signals detected - maintain current positions")

        else:
            st.warning("⚠ Failed to fetch comparison data")
