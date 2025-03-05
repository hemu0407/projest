import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Set Page Configuration
st.set_page_config(page_title="Stock Market App", layout="wide")

# API Key
API_KEY = "MVVQ3GM2LROFV9JI"  # Replace with your actual API key

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
st.sidebar.markdown("---")

# Sidebar Sections
st.sidebar.markdown("### 📊 Dashboard")
page = st.sidebar.radio("", ["🏠 Home", "📊 Stock Market Dashboard", "🚨 Price Alert", "🔄 Stock Comparison"])

# Additional Information
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ Information")
st.sidebar.info("This app provides real-time stock market data analysis tools.")

# Home Page
if page == "🏠 Home":
    st.image("https://source.unsplash.com/featured/?stocks,market", use_column_width=True)
    st.markdown("## Welcome to Stock Market Analyzer")
    st.markdown("""
    **Features:**
    - Real-time stock data analysis
    - Price trend visualization
    - Intelligent price alerts
    - Comparative stock analysis
    - Actionable investment insights
    """)

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
        st.subheader(f"📈 {selected_company} Analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"${current_price:.2f}")
        with col2:
            st.metric("Daily High", f"${df['High'].max():.2f}")
        with col3:
            st.metric("Daily Low", f"${df['Low'].min():.2f}")

        fig = px.line(df, x=df.index, y="Close", title="Intraday Price Movement",
                      template="plotly_dark")
        st.plotly_chart(fig)

# Price Alert Section
elif page == "🚨 Price Alert":
    st.title("🚨 Price Alert Management")
    
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

    st.subheader("📋 Active Alerts")
    if st.session_state.alerts:
        for alert in st.session_state.alerts:
            st.write(f"- {alert['company']} @ ${alert['alert_price']:.2f}")
    else:
        st.info("No active alerts")

# Stock Comparison Section with Enhanced Insights
elif page == "🔄 Stock Comparison":
    st.title("📈 Comparative Stock Analysis")
    
    st.markdown("### 🔍 Select Companies to Compare")
    col1, col2 = st.columns(2)
    with col1:
        stock1 = st.selectbox("First Company", list(companies.keys()), key="stock1")
    with col2:
        stock2 = st.selectbox("Second Company", 
                             [c for c in companies.keys() if c != stock1], 
                             key="stock2")

    if st.button("🚀 Run Comparative Analysis"):
        with st.spinner("Analyzing stocks..."):
            data1 = get_stock_data(companies[stock1])
            data2 = get_stock_data(companies[stock2])

            if "Time Series (5min)" in data1 and "Time Series (5min)" in data2:
                # Process data
                df1 = pd.DataFrame(data1["Time Series (5min)"]).T.astype(float)
                df2 = pd.DataFrame(data2["Time Series (5min)"]).T.astype(float)
                
                # Create comparison dataframe
                comparison_df = pd.DataFrame({
                    stock1: df1["4. close"],
                    stock2: df2["4. close"]
                }).sort_index().ffill()

                # Calculate metrics
                correlation = comparison_df[stock1].corr(comparison_df[stock2])
                vol1 = comparison_df[stock1].pct_change().std() * 100
                vol2 = comparison_df[stock2].pct_change().std() * 100
                momentum1 = (comparison_df[stock1].iloc[-1] / comparison_df[stock1].iloc[0] - 1) * 100
                momentum2 = (comparison_df[stock2].iloc[-1] / comparison_df[stock2].iloc[0] - 1) * 100

                # Visualization
                st.subheader("📊 Comparative Analysis Results")
                
                # Metrics columns
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f"{stock1} Momentum", f"{momentum1:.2f}%")
                    st.metric(f"{stock1} Volatility", f"{vol1:.2f}%")
                with col2:
                    st.metric(f"{stock2} Momentum", f"{momentum2:.2f}%")
                    st.metric(f"{stock2} Volatility", f"{vol2:.2f}%")
                
                # Correlation insights
                st.markdown("### 📈 Correlation Analysis")
                st.write(f"Correlation Coefficient: {correlation:.2f}")
                if correlation > 0.8:
                    st.success("**Strong Positive Correlation** - These stocks tend to move together")
                    st.markdown("💡 **Strategy:** Consider pairs trading or sector-based investing")
                elif correlation < -0.8:
                    st.warning("**Strong Negative Correlation** - These stocks tend to move oppositely")
                    st.markdown("💡 **Strategy:** Potential hedging opportunity")
                else:
                    st.info("**Weak Correlation** - Stocks show independent movement")
                    st.markdown("💡 **Strategy:** Good for portfolio diversification")

                # Volatility comparison
                st.markdown("### 📉 Volatility Assessment")
                vol_df = pd.DataFrame({
                    "Stock": [stock1, stock2],
                    "Volatility": [vol1, vol2]
                })
                fig = px.bar(vol_df, x="Stock", y="Volatility", color="Stock",
                            title="Price Volatility Comparison")
                st.plotly_chart(fig)
                
                if vol1 > vol2:
                    st.markdown(f"**Analysis:** {stock1} is {vol1/vol2:.1f}x more volatile than {stock2}")
                    st.markdown("💡 **Consider:** Higher risk/reward potential in {stock1}")
                else:
                    st.markdown(f"**Analysis:** {stock2} is {vol2/vol1:.1f}x more volatile than {stock1}")
                    st.markdown("💡 **Consider:** {stock2} might offer better short-term trading opportunities")

                # Momentum analysis
                st.markdown("### 🚀 Momentum Comparison")
                mom_df = pd.DataFrame({
                    "Stock": [stock1, stock2],
                    "Momentum": [momentum1, momentum2]
                })
                fig = px.bar(mom_df, x="Stock", y="Momentum", color="Stock",
                            title="Price Momentum Comparison")
                st.plotly_chart(fig)
                
                if momentum1 > momentum2:
                    st.success(f"**Trend:** {stock1} shows stronger upward momentum")
                    st.markdown("💡 **Consider:** Potential buying opportunity in {stock1}")
                else:
                    st.warning(f"**Trend:** {stock2} demonstrates better recent performance")
                    st.markdown("💡 **Consider:** Investigate {stock2} for potential investments")

                # Price trend visualization
                st.markdown("### 📈 Price Trend Comparison")
                fig = px.line(comparison_df, x=comparison_df.index, y=[stock1, stock2],
                             title="Hourly Price Movement Comparison",
                             labels={"value": "Stock Price", "variable": "Company"},
                             template="plotly_dark")
                st.plotly_chart(fig)

                # Final recommendations
                st.markdown("### 💡 Investment Recommendations")
                if correlation > 0.7 and abs(momentum1 - momentum2) > 5:
                    st.success("**Strategy Recommendation:** Consider pairs trading strategy")
                    st.markdown("- Buy the outperforming stock")
                    st.markdown("- Short the underperforming stock")
                elif vol1 > 5 and vol2 > 5:
                    st.warning("**High Volatility Alert:** Both stocks show significant price swings")
                    st.markdown("- Consider options strategies")
                    st.markdown("- Implement stop-loss orders")
                else:
                    st.info("**Diversification Opportunity:** These stocks provide diversified exposure")
                    st.markdown("- Consider balanced portfolio allocation")

            else:
                st.error("Failed to fetch data for comparison")

# Run the app
if __name__ == "__main__":
    st.sidebar.markdown("---")
    st.sidebar.markdown("Built with Streamlit ♥")
