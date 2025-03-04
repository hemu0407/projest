# Price Alert
elif page == "🚨 Price Alert":
    st.title("🚨 Price Alert")

    # Initialize session state for alerts if not already done
    if "alerts" not in st.session_state:
        st.session_state.alerts = []

    # Set Alert
    st.subheader("🔔 Set Price Alert")
    selected_company = st.selectbox("📌 Choose a Company for Alerts", list(companies.keys()))
    alert_price = st.number_input("💰 Enter Alert Price", min_value=0.0, format="%.2f")
    
    if st.button("✅ Set Alert"):
        # Add alert to session state
        st.session_state.alerts.append({
            "company": selected_company,
            "symbol": companies[selected_company],
            "alert_price": alert_price
        })
        st.success(f"🚀 Alert set for {selected_company} at ${alert_price:.2f}")

    # Display Active Alerts
    st.subheader("📋 Active Alerts")
    if st.session_state.alerts:
        for i, alert in enumerate(st.session_state.alerts):
            st.write(f"{i + 1}. {alert['company']} - Alert at ${alert['alert_price']:.2f}")
            if st.button(f"❌ Clear Alert {i + 1}"):
                st.session_state.alerts.pop(i)
                st.session_state.rerun = True  # Trigger rerun
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
                        st.success(f"🚨 Alert triggered for {alert['company']}! Current price: ${current_price:.2f} (Target: ${alert['alert_price']:.2f})")
                    else:
                        st.info(f"⏳ {alert['company']} is at ${current_price:.2f}. Waiting to reach ${alert['alert_price']:.2f}.")
                else:
                    st.warning(f"⚠ The 'Close' column is missing in the data for {alert['company']}.")
            else:
                st.warning(f"⚠ Could not fetch data for {alert['company']}.")

    # Rerun the app if needed
    if "rerun" in st.session_state and st.session_state.rerun:
        st.session_state.rerun = False
        if hasattr(st, "experimental_rerun"):  # Check if st.experimental_rerun is available
            st.experimental_rerun()
        elif hasattr(st, "rerun"):  # Check if st.rerun is available
            st.rerun()
        else:
            st.warning("⚠ Rerun functionality is not available in your Streamlit version. Please upgrade Streamlit.")
