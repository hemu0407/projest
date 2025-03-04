import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.svm import SVR

# Set Page Configuration
st.set_page_config(page_title="Stock Market App", layout="wide")

# API Key
API_KEY = "MPPUU3T1XG48JIOK"

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

# Sidebar Toggle JavaScript
st.markdown("""
<script>
    function toggleSidebar() {
        var sidebar = parent.document.querySelector("[data-testid='stSidebar']");
        if (sidebar.style.display === "none") {
            sidebar.style.display = "block";
        } else {
            sidebar.style.display = "none";
        }
    }
</script>
""", unsafe_allow_html=True)

# Floating ☰ Sidebar Button
st.markdown(
    """
    <button onclick="toggleSidebar()" 
    style="
        position:fixed;
        top:10px;
        left:10px;
        background:#333;
        color:white;
        border:none;
        padding:10px 15px;
        font-size:24px;
        cursor:pointer;
    ">☰</button>
    """,
    unsafe_allow_html=True,
)

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📊 Stock Market Dashboard", "🚨 Price Alert", "🔄 Stock Comparison"])

# Home Page
if page == "🏠 Home":
    st.image("https://source.unsplash.com/featured/?stocks,market", use_column_width=True)

# Fetch Stock Data Function
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    return response.json()

# Stock Market Dashboard
if page == "📊 Stock Market Dashboard":
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

    # Display Stock Data & Insights
    if "stock_data" in st.session_state:
        df = st.session_state.stock_data
        current_price = df["Close"].iloc[-1]
        highest_price = df["High"].max()
        starting_price = df["Open"].iloc[0]

        st.subheader(f"📈 {selected_company} Stock Details")
        st.info(f"💰 *Current Price:* ${current_price:.2f}")
        st.success(f"📈 *Highest Price:* ${highest_price:.2f}")
        st.warning(f"🔽 *Starting Price:* ${starting_price:.2f}")

        # Intraday Graph
        fig = px.line(df, x=df.index, y="Close", title="📊 Intraday Stock Prices", labels={"Close": "Stock Price"}, template="plotly_dark")
        st.plotly_chart(fig)

        # Investment Calculator
        num_stocks = st.number_input("🛒 Enter number of stocks to buy", min_value=1, step=1)

        if st.button("📊 Fetch Profit/Loss and Future Prediction"):
            total_cost = num_stocks * current_price
            st.info(f"💰 *Total Investment:* ${total_cost:.2f}")

            # **🧠 Future Trend Prediction (SVR)**
            st.subheader("📈 Future Stock Price Prediction")

            df["Time"] = np.arange(len(df))
            X = df[["Time"]].values
            y = df["Close"].values

            model = SVR(kernel="rbf", C=1e3, gamma=0.1)
            model.fit(X, y)

            future_times = np.arange(len(df) + 10).reshape(-1, 1)
            future_prices = model.predict(future_times)

            future_df = pd.DataFrame({"Time": future_times.flatten(), "Predicted Price": future_prices})
            fig_pred = px.line(future_df, x="Time", y="Predicted Price", title="📈 Predicted Stock Prices (Next 10 Ticks)", template="plotly_dark")
            st.plotly_chart(fig_pred)

            # Calculate Profit/Loss
            future_price = future_prices[-1]
            future_value = num_stocks * future_price
            profit_loss = future_value - total_cost
            profit_loss_percentage = (profit_loss / total_cost) * 100

            if profit_loss > 0:
                st.success(f"📈 *Profit:* ${profit_loss:.2f} ({profit_loss_percentage:.2f}%)")
                st.info(f"💡 *Recommendation:* Consider selling when the price reaches ${future_price:.2f} to maximize profit.")
            else:
                st.error(f"📉 *Loss:* ${abs(profit_loss):.2f} ({abs(profit_loss_percentage):.2f}%)")
                st.warning(f"💡 *Recommendation:* It might not be the best time to buy. Consider waiting for a better price.")

            # **📊 Historical Trend Analysis**
            st.subheader("📊 Historical Performance")
            st.metric(label="📉 Lowest Price", value=f"${df['Low'].min():.2f}")
            st.metric(label="📈 Highest Price", value=f"${df['High'].max():.2f}")
            st.metric(label="📊 Average Price", value=f"${df['Close'].mean():.2f}")

# Price Alert
elif page == "🚨 Price Alert":
    st.title("🚨 Set Price Alert")
    
    selected_company = st.selectbox("📌 Choose a Company for Alerts", list(companies.keys()))
    alert_price = st.number_input("
