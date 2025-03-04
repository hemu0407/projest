import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Set Page Configuration
st.set_page_config(page_title="Stock Analysis Pro", layout="wide")

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

# Analysis Functions
def generate_deep_analysis(stock_name, prices):
    ma_50 = prices.rolling(50).mean().iloc[-1]
    ma_200 = prices.rolling(200).mean().iloc[-1]
    current_price = prices.iloc[-1]
    
    analysis = f"**{stock_name} Analysis**: "
    if current_price > ma_50 and current_price > ma_200:
        analysis += f"🔥 Strong bullish trend (${current_price:.2f} above both 50-period (${ma_50:.2f}) and 200-period MA (${ma_200:.2f}). "
    elif current_price > ma_200:
        analysis += f"📈 Moderate bullish trend (above 200-period MA at ${ma_200:.2f}) but below 50-period MA. "
    else:
        analysis += "📉 Bearish trend (below key moving averages). "
        
    if prices.iloc[-1] > prices.iloc[-100]:
        analysis += "🚀 Showing 100-period upward momentum."
    return analysis

def volatility_insight(stock_name, volatility):
    if volatility > 3:
        return f"🔴 **{stock_name}**: High volatility ({volatility:.2f}%) - Consider strict stop-loss strategies"
    elif volatility > 1.5:
        return f"🟠 **{stock_name}**: Moderate volatility ({volatility:.2f}%) - Swing trading opportunities"
    return f"🟢 **{stock_name}**: Low volatility ({volatility:.2f}%) - Stable long-term holding"

def momentum_signal(stock_name, change):
    if change > 2:
        return f"🚀 **{stock_name}**: Strong upward momentum (+{change:.2f}%) - Consider short-term longs"
    elif change < -2:
        return f"📉 **{stock_name}**: Strong downward momentum ({change:.2f}%) - Potential short opportunity"
    return f"⚖️ **{stock_name}**: Neutral momentum ({change:.2f}%) - Wait for clearer signals"

# Initialize session state
if "alerts" not in st.session_state:
    st.session_state.alerts = []

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📊 Stock Dashboard", "🚨 Price Alerts", "🔄 Stock Comparison"])

# Home Page
if page == "🏠 Home":
    st.image("https://source.unsplash.com/featured/?stocks,market", use_column_width=True)
    st.markdown("""
    <div style="text-align: center;">
        <h1>Stock Analysis Pro</h1>
        <p>Advanced analytics platform for intelligent trading decisions</p>
    </div>
    """, unsafe_allow_html=True)

# Stock Dashboard
elif page == "📊 Stock Dashboard":
    st.title("📊 Real-Time Stock Dashboard")
    
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

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Current Price", f"${current_price:.2f}")
        with col2:
            st.metric("📈 All Time High", f"${highest_price:.2f}")
        with col3:
            st.metric("📉 Opening Price", f"${starting_price:.2f}")

        fig = px.line(df, x=df.index, y="Close", title="📊 Intraday Price Movement", 
                     labels={"Close": "Price"}, template="plotly_dark")
        st.plotly_chart(fig)

# Price Alerts
elif page == "🚨 Price Alerts":
    st.title("🚨 Price Alert System")

    if "alerts" not in st.session_state:
        st.session_state.alerts = []

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔔 Set New Alert")
        selected_company = st.selectbox("Select Company", list(companies.keys()))
        alert_price = st.number_input("Alert Price", min_value=0.0, format="%.2f")
        
        if st.button("✅ Set Alert"):
            st.session_state.alerts.append({
                "company": selected_company,
                "symbol": companies[selected_company],
                "alert_price": alert_price
            })
            st.success(f"Alert set for {selected_company} at ${alert_price:.2f}")

    with col2:
        st.subheader("📋 Active Alerts")
        if st.session_state.alerts:
            for i, alert in enumerate(st.session_state.alerts):
                st.write(f"{i+1}. {alert['company']} @ ${alert['alert_price']:.2f}")
                if st.button(f"Clear {i+1}"):
                    st.session_state.alerts.pop(i)
                    st.experimental_rerun()
        else:
            st.info("No active alerts")

# Stock Comparison
elif page == "🔄 Stock Comparison":
    st.title("🔍 Advanced Stock Comparison")
    
    company_list = list(companies.keys())
    stock1 = st.selectbox("First Company", company_list, key="stock1")
    stock2 = st.selectbox("Second Company", 
                         [c for c in company_list if c != stock1], 
                         key="stock2")

    if st.button("🔍 Compare"):
        stock1_data = get_stock_data(companies[stock1])
        stock2_data = get_stock_data(companies[stock2])

        if "Time Series (5min)" in stock1_data and "Time Series (5min)" in stock2_data:
            # Data Processing
            df1 = pd.DataFrame(stock1_data["Time Series (5min)"]).T.astype(float)
            df2 = pd.DataFrame(stock2_data["Time Series (5min)"]).T.astype(float)
            
            df1.index = pd.to_datetime(df1.index)
            df2.index = pd.to_datetime(df2.index)
            
            comparison_df = pd.DataFrame({
                stock1: df1["4. close"],
                stock2: df2["4. close"]
            }).sort_index()

            # Main Comparison Chart
            fig = px.line(comparison_df, template="plotly_dark", 
                         title="📊 Price Trend Comparison")
            st.plotly_chart(fig)

            # ---- Analysis Section ----
            st.header("📈 Advanced Analytics")
            
            # Deep Analysis
            st.subheader("🔍 Trend Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(generate_deep_analysis(stock1, comparison_df[stock1]))
            with col2:
                st.markdown(generate_deep_analysis(stock2, comparison_df[stock2]))

            # Volatility Analysis
            st.subheader("⚡ Volatility Profile")
            volatility = pd.DataFrame({
                "Stock": [stock1, stock2],
                "Volatility": [
                    comparison_df[stock1].pct_change().std() * 100,
                    comparison_df[stock2].pct_change().std() * 100
                ]
            })
            col1, col2 = st.columns(2)
            with col1:
                fig_vol = px.bar(volatility, x="Stock", y="Volatility", 
                                color="Stock", template="plotly_dark")
                st.plotly_chart(fig_vol)
            with col2:
                st.markdown(volatility_insight(stock1, volatility.loc[0, "Volatility"]))
                st.markdown(volatility_insight(stock2, volatility.loc[1, "Volatility"]))

            # Momentum Analysis
            st.subheader("🚀 Momentum Signals")
            momentum = pd.DataFrame({
                "Stock": [stock1, stock2],
                "Change": [
                    (comparison_df[stock1][-1] - comparison_df[stock1][-6])/comparison_df[stock1][-6] * 100,
                    (comparison_df[stock2][-1] - comparison_df[stock2][-6])/comparison_df[stock2][-6] * 100
                ]
            })
            col1, col2 = st.columns(2)
            with col1:
                fig_momentum = px.bar(momentum, x="Stock", y="Change", 
                                    color="Stock", template="plotly_dark")
                st.plotly_chart(fig_momentum)
            with col2:
                st.markdown(momentum_signal(stock1, momentum.loc[0, "Change"]))
                st.markdown(momentum_signal(stock2, momentum.loc[1, "Change"]))

            # Predictive Insights
            st.subheader("🔮 Predictive Insights")
            correlation = comparison_df[stock1].corr(comparison_df[stock2])
            predictive_text = ""
            
            if correlation > 0.7:
                predictive_text += f"**Strong Correlation (r={correlation:.2f})**: "
                predictive_text += f"{stock1} and {stock2} move together - Consider pairs trading\n\n"
            elif correlation < -0.7:
                predictive_text += f"**Inverse Relationship (r={correlation:.2f})**: "
                predictive_text += "Good hedging opportunity\n\n"
            else:
                predictive_text += "**Diversified Exposure**: Stocks show independent movement patterns\n\n"

            if any(momentum["Change"].abs() > 2):
                predictive_text += "⚠️ **Momentum Warning**: Significant price movement detected in last hour - Monitor for potential reversals"

            st.markdown(predictive_text)

        else:
            st.warning("Failed to fetch comparison data")

# Run the app
if __name__ == "__main__":
    st.rerun()
