import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import mysql.connector
import hashlib

# Set Page Configuration
st.set_page_config(page_title="Stock Market App", layout="wide")

# API Key
API_KEY = "MVVQ3GM2LROFV9JI"

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
st.sidebar.markdown("---")  # Adds a horizontal line for separation

# Sidebar Sections
st.sidebar.markdown("### 📊 Dashboard")
page = st.sidebar.radio("", ["🏠 Home", "📊 Stock Market Dashboard", "🚨 Price Alert", "🔄 Stock Comparison"])

# Additional Information Section
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ Information")
st.sidebar.info("""
This app provides real-time stock market data, price alerts, and advanced stock comparison tools. 
Use the navigation above to explore different features.
""")

# API Information Section
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔑 API Information")
st.sidebar.info("""
Data is fetched using the Alpha Vantage API. 
For more details, visit [Alpha Vantage](https://www.alphavantage.co/).
""")

# Contact Information Section
st.sidebar.markdown("---")
st.sidebar.markdown("### 📧 Contact")
st.sidebar.info("""
For any queries or feedback, please contact us at:
- *Email:* support@stockmarketapp.com
- *Phone:* +1 (123) 456-7890
""")

# Footer Section
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Last Updated")
st.sidebar.info("""
*Date:* 2023-10-01  
*Version:* 1.0.0
""")

# --------------------------
# MySQL Database Functions
# --------------------------

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to create a connection to MySQL
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",   # Use "127.0.0.1" instead of "localhost"
            user="root",        # Your MySQL username
            password="Mysql$0407", # Your MySQL password
            database="stock_market_app"   # Your database name
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Function to create users table
def create_users_table():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

# Function to register user
def register_user(username, password, email):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password, email)
                VALUES (%s, %s, %s)
            """, (username, hash_password(password), email))
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        finally:
            cursor.close()
            conn.close()

# Function to verify login
def login_user(username, password):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and user[0] == hash_password(password):
            return True
    return False

# Create users table on startup
create_users_table()

# --------------------------
# Page Routing
# --------------------------

# Home Page (Updated Sign Up Section)
if page == "🏠 Home":
    st.title("📈 Stock Market Analyzer")
    st.markdown("---")

    # Home Page Layout
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🔐 Sign In / Sign Up")
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

        with tab1:
            st.write("Already have an account? Sign in below.")
            username = st.text_input("Username", key="signin_username")
            password = st.text_input("Password", type="password", key="signin_password")
            if st.button("Sign In"):
                if username and password:
                    if login_user(username, password):
                        st.session_state.user = username
                        st.success(f"Welcome back, {username}!")
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.warning("Please enter both username and password.")

        with tab2:
            st.write("New user? Sign up below.")
            new_username = st.text_input("Username", key="signup_username")
            new_password = st.text_input("Password", type="password", key="signup_password")
            email = st.text_input("Email", key="signup_email")
            if st.button("Sign Up"):
                if new_username and new_password and email:
                    if register_user(new_username, new_password, email):
                        st.success("🎉 Sign Up Successful! Please log in.")
                    else:
                        st.error("Username or email already exists!")
                else:
                    st.warning("Please fill all fields.")

    with col2:
        st.subheader("📰 Latest Stock Market News")
        # Fetch News Articles (NewsAPI)
        def fetch_news():
            try:
                news_api_key = "e2d4e597c657407b9c1dee3a880cd670"  # Your News API key
                url = f"https://newsapi.org/v2/everything?q=stock+market&apiKey={news_api_key}"
                response = requests.get(url)
                if response.status_code == 200:
                    return response.json()["articles"]
                else:
                    st.error("Failed to fetch news. Please try again later.")
                    return []
            except Exception as e:
                st.error(f"Error fetching news: {e}")
                return []

        news_articles = fetch_news()
        if news_articles:
            for article in news_articles[:5]:  # Display top 5 articles
                st.markdown(f"### {article['title']}")
                st.write(f"**Source:** {article['source']['name']}")
                st.write(f"**Published At:** {article['publishedAt']}")
                st.write(article['description'])
                st.markdown(f"[Read More]({article['url']})")
                st.markdown("---")
        else:
            st.info("No news articles available at the moment.")

    # Additional Features
    st.subheader("🌟 Why Choose Us?")
    st.markdown("""
    - **Real-Time Data:** Get up-to-date stock market data.
    - **Advanced Analysis:** Perform in-depth stock comparisons.
    - **Price Alerts:** Never miss important price movements.
    - **Personalized Experience:** Sign up to save your preferences and alerts.
    """)

    st.subheader("📊 Quick Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", "1,234")  # Replace with dynamic data from DB
    with col2:
        st.metric("Active Alerts", "56")  # Replace with dynamic data from DB
    with col3:
        st.metric("Stocks Tracked", "500+")

    st.subheader("📞 Contact Us")
    st.markdown("""
    Have questions or need support? Reach out to us:
    - **Email:** support@stockmarketapp.com
    - **Phone:** +1 (123) 456-7890
    """)

# Stock Market Dashboard (Unchanged)
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

# Price Alert Section (Unchanged)
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

# Stock Comparison Section (Unchanged)
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
            st.subheader("📈 Actionable Insights")
            
            # Correlation Analysis with Strategy Implications
            correlation = comparison_df[stock1].corr(comparison_df[stock2])
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Correlation Coefficient", f"{correlation:.2f}")
            with col2:
                if correlation > 0.8:
                    st.success("Strong Positive Correlation")
                    st.write("💡 **Strategy:** Consider pairs trading or sector-based investing")
                elif correlation < -0.8:
                    st.warning("Strong Negative Correlation")
                    st.write("💡 **Strategy:** Potential hedging opportunity")
                else:
                    st.info("Weak Correlation")
                    st.write("💡 **Strategy:** Good for portfolio diversification")

            # Volatility Analysis with Risk Assessment
            st.subheader("📉 Volatility Comparison")
            vol1 = comparison_df[stock1].pct_change().std() * 100
            vol2 = comparison_df[stock2].pct_change().std() * 100
            vol_df = pd.DataFrame({
                "Stock": [stock1, stock2],
                "Volatility": [vol1, vol2]
            })
            fig_vol = px.bar(vol_df, x="Stock", y="Volatility", 
                            color="Stock", template="plotly_dark",
                            title="Price Volatility (Standard Deviation of Daily Returns)")  # Fixed line
            st.plotly_chart(fig_vol)

            if vol1 > vol2:
                st.warning(f"{stock1} is {vol1/vol2:.1f}x more volatile than {stock2}")
                st.write("💡 **Consider:** Higher risk/reward potential in", stock1)
            else:
                st.info(f"{stock2} is {vol2/vol1:.1f}x more volatile than {stock1}")
                st.write("💡 **Consider:**", stock2, "might offer better short-term trading opportunities")

            # Momentum Analysis with Trend Insights
            st.subheader("🚀 Momentum Analysis")
            momentum1 = (comparison_df[stock1].iloc[-1] / comparison_df[stock1].iloc[0] - 1) * 100
            momentum2 = (comparison_df[stock2].iloc[-1] / comparison_df[stock2].iloc[0] - 1) * 100
            mom_df = pd.DataFrame({
                "Stock": [stock1, stock2],
                "Momentum": [momentum1, momentum2]
            })
            fig_momentum = px.bar(mom_df, x="Stock", y="Momentum", 
                                 color="Stock", template="plotly_dark",
                                 title="Percentage Change Over Period")
            st.plotly_chart(fig_momentum)

            if momentum1 > momentum2:
                st.success(f"{stock1} shows stronger upward momentum")
                st.write("💡 **Consider:** Potential buying opportunity in", stock1)
            else:
                st.warning(f"{stock2} demonstrates better recent performance")
                st.write("💡 **Consider:** Investigate", stock2, "for potential investments")

            # Final Recommendations
            st.subheader("💡 Investment Recommendations")
            if correlation > 0.7 and abs(momentum1 - momentum2) > 5:
                st.success("**Pairs Trading Opportunity**")
                st.write("- Buy the outperforming stock")
                st.write("- Short the underperforming stock")
            elif vol1 > 5 and vol2 > 5:
                st.warning("**High Volatility Alert**")
                st.write("- Consider options strategies")
                st.write("- Implement stop-loss orders")
            else:
                st.info("**Diversification Opportunity**")
                st.write("- Consider balanced portfolio allocation")

        else:
            st.warning("⚠ Failed to fetch comparison data")
