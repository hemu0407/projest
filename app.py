import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Set Page Configuration
st.set_page_config(page_title="Stock Market App", layout="wide")

# Custom CSS for Login Page
st.markdown(
    """
    <style>
    .login-container {
        max-width: 400px;
        padding: 2rem;
        margin: 0 auto;
        border: 1px solid #ddd;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .login-title {
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# User Database (Replace with a real database in production)
USERS = {
    "user1": {"password": "pass1", "name": "John Doe"},
    "user2": {"password": "pass2", "name": "Jane Smith"}
}

# Authentication Functions
def authenticate(username, password):
    """Check if the username and password are valid."""
    if username in USERS and USERS[username]['password'] == password:
        return True
    return False

def login_page():
    """Display the login page and handle authentication."""
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>🔒 Stock App Login</h2>", unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.session_state.current_user = USERS[username]['name']
            st.success("Login successful! Redirecting...")
            st.experimental_rerun()
        else:
            st.error("Invalid username/password")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Check Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Show login page if not authenticated
if not st.session_state.authenticated:
    login_page()

# =================================================================
# REST OF YOUR ORIGINAL CODE STARTS HERE (Only for authenticated users)
# =================================================================

# Custom CSS for Sidebar Blocks (Original CSS remains same)
st.markdown(
    """
    <style>
    .sidebar .block-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .sidebar .stButton>button {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f2f6;
        border: 1px solid #ccc;
        text-align: left;
        font-size: 16px;
        color: #333;
    }
    .sidebar .stButton>button:hover {
        background-color: #e2e6ea;
        border-color: #bbb;
    }
    .sidebar .stMarkdown {
        margin-bottom: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Add logout button to sidebar
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.clear()
    st.experimental_rerun()

# Show welcome message
st.sidebar.markdown(f"### 👋 Welcome, {st.session_state.current_user}!")

# API Key and other original code continues...
API_KEY = "B1N3W1H7PD3F8ZRG"

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

# Sidebar Sections as Blocks
if st.sidebar.button("🏠 Home"):
    st.session_state.page = "🏠 Home"
if st.sidebar.button("📊 Stock Market Dashboard"):
    st.session_state.page = "📊 Stock Market Dashboard"
if st.sidebar.button("🚨 Price Alert"):
    st.session_state.page = "🚨 Price Alert"
if st.sidebar.button("🔄 Stock Comparison"):
    st.session_state.page = "🔄 Stock Comparison"

# Set default page if not set
if "page" not in st.session_state:
    st.session_state.page = "📊 Stock Market Dashboard"

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
- Email: support@stockmarketapp.com
- Phone: +1 (123) 456-7890
""")

# Footer Section
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Last Updated")
st.sidebar.info("""
Date: 2023-10-01  
Version: 1.0.0
""")

# Home Page
if st.session_state.page == "🏠 Home":
    st.image("https://source.unsplash.com/featured/?stocks,market", use_column_width=True)

# Stock Market Dashboard
elif st.session_state.page == "📊 Stock Market Dashboard":
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
        total_cost = num_stocks * current_price
        st.info(f"💰 Total Investment: ${total_cost:.2f}")

        if st.button("📊 Fetch Profit/Loss and Future Prediction"):
            # Prepare data for SVM
            df['Time'] = (df.index - df.index[0]).total_seconds() / 3600  # Convert time to hours
            X = df[['Time']]
            y = df['Close']
            
            # Train-test split (80:20)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale the data
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train SVM model
            svm_model = SVR(kernel='rbf')
            svm_model.fit(X_train_scaled, y_train)
            
            # Predict future prices
            future_hours = np.arange(df['Time'].max() + 1, df['Time'].max() + 24, 1).reshape(-1, 1)
            future_hours_scaled = scaler.transform(future_hours)
            predicted_prices = svm_model.predict(future_hours_scaled)
            
            # Create future dataframe
            future_times = pd.date_range(start=df.index[-1], periods=len(future_hours), freq="H")
            future_df = pd.DataFrame({"Time": future_times, "Predicted Price": predicted_prices})
            
            # Plot predictions
            st.subheader("📈 Future Stock Price Prediction (SVM Model)")
            fig_pred = px.line(future_df, x="Time", y="Predicted Price", 
                             title="📈 Predicted Stock Prices (Next 24 Hours)", 
                             template="plotly_dark")
            st.plotly_chart(fig_pred)
            
            # Profit/Loss Calculation
            future_price = predicted_prices[-1]
            future_value = num_stocks * future_price
            profit_loss = future_value - total_cost
            profit_loss_percentage = (profit_loss / total_cost) * 100

            if profit_loss > 0:
                st.success(f"📈 Profit: ${profit_loss:.2f} ({profit_loss_percentage:.2f}%)")
                st.info(f"💡 Recommendation: Consider selling when price reaches ${future_price:.2f}")
            else:
                st.error(f"📉 Loss: ${abs(profit_loss):.2f} ({abs(profit_loss_percentage):.2f}%)")
                st.warning("💡 Recommendation: Do not invest at this time")

# Price Alert Section
elif st.session_state.page == "🚨 Price Alert":
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

# Stock Comparison Section (Updated)
elif st.session_state.page == "🔄 Stock Comparison":
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
                    st.write("💡 *Strategy:* Consider pairs trading or sector-based investing")
                elif correlation < -0.8:
                    st.warning("Strong Negative Correlation")
                    st.write("💡 *Strategy:* Potential hedging opportunity")
                else:
                    st.info("Weak Correlation")
                    st.write("💡 *Strategy:* Good for portfolio diversification")

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
                            title="Price Volatility (Standard Deviation of Daily Returns)")
            st.plotly_chart(fig_vol)

            if vol1 > vol2:
                st.warning(f"{stock1} is {vol1/vol2:.1f}x more volatile than {stock2}")
                st.write("💡 *Consider:* Higher risk/reward potential in", stock1)
            else:
                st.info(f"{stock2} is {vol2/vol1:.1f}x more volatile than {stock1}")
                st.write("💡 *Consider:*", stock2, "might offer better short-term trading opportunities")

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
                st.write("💡 *Consider:* Potential buying opportunity in", stock1)
            else:
                st.warning(f"{stock2} demonstrates better recent performance")
                st.write("💡 *Consider:* Investigate", stock2, "for potential investments")

            # Final Recommendations
            st.subheader("💡 Investment Recommendations")
            if correlation > 0.7 and abs(momentum1 - momentum2) > 5:
                st.success("*Pairs Trading Opportunity*")
                st.write("- Buy the outperforming stock")
                st.write("- Short the underperforming stock")
            elif vol1 > 5 and vol2 > 5:
                st.warning("*High Volatility Alert*")
                st.write("- Consider options strategies")
                st.write("- Implement stop-loss orders")
            else:
                st.info("*Diversification Opportunity*")
                st.write("- Consider balanced portfolio allocation")

        else:
            st.warning("⚠ Failed to fetch comparison data")
