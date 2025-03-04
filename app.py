# Stock Comparison
elif page == "🔄 Stock Comparison":
    st.title("🔄 Compare Stock Performance")

    # Get list of companies for dropdowns
    company_list = list(companies.keys())

    # First Stock Selection
    stock1 = st.selectbox("📌 Select First Company", company_list, key="stock1")

    # Second Stock Selection (exclude the first selected stock)
    stock2_options = [company for company in company_list if company != stock1]
    stock2 = st.selectbox("📌 Select Second Company", stock2_options, key="stock2")

    if st.button("🔍 Compare Stocks"):
        stock1_data = get_stock_data(companies[stock1])
        stock2_data = get_stock_data(companies[stock2])

        if "Time Series (5min)" in stock1_data and "Time Series (5min)" in stock2_data:
            # Process Stock 1 Data
            df1 = pd.DataFrame.from_dict(stock1_data["Time Series (5min)"], orient="index").astype(float)
            df1.index = pd.to_datetime(df1.index)
            df1 = df1.sort_index()
            df1.columns = ["Open", "High", "Low", "Close", "Volume"]

            # Process Stock 2 Data
            df2 = pd.DataFrame.from_dict(stock2_data["Time Series (5min)"], orient="index").astype(float)
            df2.index = pd.to_datetime(df2.index)
            df2 = df2.sort_index()
            df2.columns = ["Open", "High", "Low", "Close", "Volume"]

            # Merge Data for Comparison
            comparison_df = pd.DataFrame({
                "Time": df1.index,
                stock1: df1["Close"],
                stock2: df2["Close"]
            })

            # Plot Dual-Axis Line Chart
            st.subheader("📊 Stock Price Comparison")
            fig_compare = px.line(comparison_df, x="Time", y=[stock1, stock2], title="📊 Stock Price Comparison", template="plotly_dark")
            st.plotly_chart(fig_compare)

            # Correlation Analysis
            st.subheader("📈 Correlation Analysis")
            correlation = df1["Close"].corr(df2["Close"])
            st.info(f"📊 *Correlation between {stock1} and {stock2}:* {correlation:.2f}")

            # Scatter Plot for Correlation
            scatter_df = pd.DataFrame({stock1: df1["Close"], stock2: df2["Close"]})
            fig_scatter = px.scatter(scatter_df, x=stock1, y=stock2, title="📈 Scatter Plot of Stock Prices", template="plotly_dark")
            st.plotly_chart(fig_scatter)

            # Percentage Change Comparison
            st.subheader("📉 Percentage Change Comparison")
            df1["Pct Change"] = df1["Close"].pct_change() * 100
            df2["Pct Change"] = df2["Close"].pct_change() * 100

            fig_pct_change = px.line(
                pd.DataFrame({
                    "Time": df1.index,
                    f"{stock1} % Change": df1["Pct Change"],
                    f"{stock2} % Change": df2["Pct Change"]
                }),
                x="Time",
                y=[f"{stock1} % Change", f"{stock2} % Change"],
                title="📉 Percentage Change Over Time",
                template="plotly_dark"
            )
            st.plotly_chart(fig_pct_change)

            # Volatility Comparison
            st.subheader("📊 Volatility Comparison")
            volatility_stock1 = df1["Close"].std()
            volatility_stock2 = df2["Close"].std()
            st.info(f"📈 *Volatility of {stock1}:* {volatility_stock1:.2f}")
            st.info(f"📈 *Volatility of {stock2}:* {volatility_stock2:.2f}")

            # Volatility Bar Chart
            fig_volatility = px.bar(
                x=[stock1, stock2],
                y=[volatility_stock1, volatility_stock2],
                labels={"x": "Stock", "y": "Volatility"},
                title="📊 Volatility Comparison",
                template="plotly_dark"
            )
            st.plotly_chart(fig_volatility)

        else:
            st.warning("⚠ Unable to fetch stock data for comparison.")
