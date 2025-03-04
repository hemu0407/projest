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
            # Add this section under the "📈 Deep Analysis" section in Stock Comparison

# ======== ENHANCEMENT START ======== #
# Deep Analysis Text Summary
st.subheader("🔍 Deep Analysis Results")
def generate_deep_analysis(stock_name, prices):
    ma_50 = prices.rolling(50).mean().iloc[-1]
    ma_200 = prices.rolling(200).mean().iloc[-1]
    current_price = prices.iloc[-1]
    
    analysis = f"**{stock_name} Analysis**: "
    if current_price > ma_50 and current_price > ma_200:
        analysis += f"Strong bullish trend (${current_price:.2f} above both 50-period (${ma_50:.2f}) and 200-period MA (${ma_200:.2f})). "
    elif current_price > ma_200:
        analysis += f"Moderate bullish trend (above 200-period MA at ${ma_200:.2f}) but below 50-period MA. "
    else:
        analysis += "Bearish trend (below key moving averages). "
        
    if prices.iloc[-1] > prices.iloc[-100]:
        analysis += "Showing 100-period upward momentum. "
    return analysis

st.markdown(generate_deep_analysis(stock1, comparison_df[stock1]))
st.markdown(generate_deep_analysis(stock2, comparison_df[stock2]))

# Volatility Insights
st.subheader("⚡ Volatility Insights")
def volatility_insight(stock_name, volatility):
    if volatility > 3:
        return f"**{stock_name}**: High volatility ({volatility:.2f}%) - Consider strict stop-loss strategies"
    elif volatility > 1.5:
        return f"**{stock_name}**: Moderate volatility ({volatility:.2f}%) - Swing trading opportunities"
    return f"**{stock_name}**: Low volatility ({volatility:.2f}%) - Stable long-term holding"

st.markdown(volatility_insight(stock1, volatility.loc[0, "Volatility"]))
st.markdown(volatility_insight(stock2, volatility.loc[1, "Volatility"]))

# Momentum Analysis
st.subheader("🚀 Momentum Signals")
def momentum_signal(stock_name, change):
    if change > 2:
        return f"**{stock_name}**: Strong upward momentum (+{change:.2f}%) - Consider short-term longs"
    elif change < -2:
        return f"**{stock_name}**: Strong downward momentum ({change:.2f}%) - Potential short opportunity"
    return f"**{stock_name}**: Neutral momentum ({change:.2f}%) - Wait for clearer signals"

st.markdown(momentum_signal(stock1, momentum.loc[0, "Last Hour Change"]))
st.markdown(momentum_signal(stock2, momentum.loc[1, "Last Hour Change"]))

# Predictive Insights
st.subheader("🔮 Predictive Summary")
if correlation > 0.7:
    predictive_text = f"**Strong Correlation Play**: {stock1} and {stock2} move together (r={correlation:.2f}). "
    if volatility.loc[0, "Volatility"] > volatility.loc[1, "Volatility"]:
        predictive_text += f"Prefer {stock1} for volatility plays."
    else:
        predictive_text += f"Consider {stock2} for more stable exposure."
elif correlation < -0.7:
    predictive_text = f"**Hedging Opportunity**: {stock1} and {stock2} move oppositely (r={correlation:.2f}) - Good pair for risk management"
else:
    predictive_text = "**Diversified Exposure**: No strong correlation - Suitable for portfolio diversification"

if any(momentum["Last Hour Change"].abs() > 2):
    predictive_text += " Warning: Strong momentum detected - Monitor for potential reversals"
    
st.markdown(predictive_text)
# ======== ENHANCEMENT END ======== #
