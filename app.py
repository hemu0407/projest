import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.svm import SVR
from datetime import datetime, timedelta

# Streamlit UI Setup
st.set_page_config(page_title="Stock Market Prediction", layout="wide")

# Theme Toggle
dark_mode = st.toggle("🌗 Toggle Dark/Light Mode", value=True)

# Define styles based on theme
if dark_mode:
    primary_bg = "#1E1E1E"
    secondary_bg = "#252526"
    text_color = "#FFFFFF"
    input_bg = "#333333"
    plot_theme = "plotly_dark"
else:
    primary_bg = "#F5F5F5"
    secondary_bg = "#FFFFFF"
    text_color = "#000000"
    input_bg = "#DDDDDD"
    plot_theme = "plotly_white"

# Apply custom styles
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {primary_bg};
            color: {text_color};
        }}
        div[data-testid="stMarkdownContainer"] {{
            color: {text_color};
        }}
        .stTextInput, .stNumberInput, .stSelectbox {{
            background-color: {input_bg};
            color: {text_color};
        }}
        .stButton button {{
            background-color: {secondary_bg};
            color: {text_color};
            border-radius: 8px;
            padding: 10px;
            transition: 0.3s;
        }}
        .stButton button:hover {{
            background-color: #4CAF50;
            color: white;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📈 Intraday Stock Market Prediction")

# Select company
company = st.selectbox("Select a Stock", ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"])

if st.button("Fetch Stock Data"):
    stock = yf.Ticker(company)
    hist = stock.history(period="1d", interval="5m")  # Fetch intraday data

    if hist.empty:
        st.error("No intraday data available. Try another stock.")
    else:
        st.subheader(f"Stock Data for {company}")

        # Display key stock details
        st.write(f"**Current Price:** ${hist['Close'].iloc[-1]:.2f}")
        st.write(f"**Highest Price Today:** ${hist['High'].max():.2f}")
        st.write(f"**Opening Price Today:** ${hist['Open'][0]:.2f}")

        # Display stock intraday graph
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=hist.index, open=hist['Open'], high=hist['High'],
            low=hist['Low'], close=hist['Close'], name="Stock Data"
        ))
        fig.update_layout(title="Intraday Stock Prices", xaxis_title="Time", yaxis_title="Price", template=plot_theme)
        st.plotly_chart(fig, use_container_width=True)

        # Ask for the number of stocks to invest in
        num_stocks = st.number_input("Enter the number of stocks to buy", min_value=1, step=1)

        if st.button("Get Results"):
            # Calculate total investment
            total_amount = num_stocks * hist['Close'].iloc[-1]
            st.write(f"**Total Investment Amount:** ${total_amount:.2f}")

            # Train SVM model to predict future price
            hist['Time_Index'] = np.arange(len(hist))  # Convert time to numerical index
            X = hist[['Time_Index']].values
            y = hist['Close'].values

            model = SVR(kernel='rbf', C=100, gamma=0.1, epsilon=0.1)
            model.fit(X, y)

            # Predict next time step
            next_time_step = np.array([[X[-1][0] + 1]])  # Next index
            predicted_price = model.predict(next_time_step)[0]

            st.write(f"**Predicted Next Price:** ${predicted_price:.2f}")

            # Profit or Loss Calculation
            price_difference = predicted_price - hist['Close'].iloc[-1]
            profit_or_loss = (price_difference / hist['Close'].iloc[-1]) * 100

            if price_difference > 0:
                st.success(f"✅ Expected Profit: {profit_or_loss:.2f}%")
                st.write("💰 **Best Time to Sell: Hold for a Short Gain!**")
            else:
                st.error(f"❌ Expected Loss: {abs(profit_or_loss):.2f}%")
                st.write("⚠️ **Advice: Don't Buy This Stock!**")

            # Future trend prediction graph
            future_times = [hist.index[-1] + timedelta(minutes=5 * i) for i in range(1, 11)]
            future_predictions = [model.predict([[X[-1][0] + i]])[0] for i in range(1, 11)]

            fig_future = go.Figure()
            fig_future.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name="Actual"))
            fig_future.add_trace(go.Scatter(x=future_times, y=future_predictions, mode='lines', name="Predicted", line=dict(dash='dot')))
            fig_future.update_layout(title="Intraday Future Trend", xaxis_title="Time", yaxis_title="Stock Price", template=plot_theme)
            st.plotly_chart(fig_future, use_container_width=True)
