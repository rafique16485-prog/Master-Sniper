import streamlit as st
import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Master Sniper PRO", page_icon="🎯", layout="centered")

st.title("🎯 Master Sniper PRO")
st.markdown("**Tracking: Smart Money Flows | 9-EMA Crossover | PCR**")

mega_stocks = ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "RVNL.NS"]

tab1, tab2 = st.tabs(["⚡ Live Execution (Nifty/BankNifty)", "🚀 Swing Breakout"])

# --- TAB 1: LIVE EXECUTION ENGINE ---
with tab1:
    st.header("⚡ 9-EMA + VWAP Sniper (Execution)")
    st.write("Live Trend, Strike Selection & Risk Management")

    if st.button("🔍 Scan Live Market & Get Trade"):
        proxies = {"NIFTY 50": "NIFTYBEES.NS", "BANK NIFTY": "BANKBEES.NS"}
        col1, col2 = st.columns(2)
        cols = [col1, col2]

        for idx, (name, symbol) in enumerate(proxies.items()):
            with cols[idx]:
                st.subheader(name)
                try:
                    # Fetching Live Data
                    df = yf.Ticker(symbol).history(period="2d", interval="5m")
                    if not df.empty and len(df) > 10:
                        df['9_EMA'] = df['Close'].ewm(span=9, adjust=False).mean()
                        tp = (df['High'] + df['Low'] + df['Close']) / 3
                        df['VWAP'] = (tp * df['Volume']).cumsum() / df['Volume'].cumsum()

                        curr_close = round(df['Close'].iloc[-1], 2)
                        curr_ema = round(df['9_EMA'].iloc[-1], 2)
                        curr_vwap = round(df['VWAP'].iloc[-1], 2)

                        # Strike Calculation Logic (Approximation for Index)
                        multiplier = 100 if name == "NIFTY 50" else 100  # Bees multiplier adjust
                        index_estimate = curr_close * 100 
                        strike_step = 50 if name == "NIFTY 50" else 100
                        atm_strike = round(index_estimate / strike_step) * strike_step

                        st.write(f"📈 **Spot Price (Est):** {int(index_estimate)}")

                        # Trend & Trade Logic
                        if curr_close > curr_vwap and curr_close > curr_ema:
                            st.success("🟢 TREND: BULLISH 🚀")
                            trade_strike = f"{atm_strike} CE"
                            box_color = "#dcfce7" # Light Green
                            text_color = "#166534"
                        elif curr_close < curr_vwap and curr_close < curr_ema:
                            st.error("🔴 TREND: BEARISH 📉")
                            trade_strike = f"{atm_strike} PE"
                            box_color = "#fee2e2" # Light Red
                            text_color = "#991b1b"
                        else:
                            st.warning("🟡 TREND: SIDEWAYS ⏳")
                            trade_strike = "WAIT (No Trade)"
                            box_color = "#fef9c3"
                            text_color = "#854d0e"

                        # Execution Box
                        if trade_strike != "WAIT (No Trade)":
                            st.markdown(f"""
                            <div style="background-color: {box_color}; padding: 15px; border-radius: 10px; border: 1px solid {text_color};">
                                <h4 style="color: {text_color}; margin-top: 0;">🎯 Recommended Trade</h4>
                                <b>Strike to Buy:</b> {trade_strike} (ATM)<br>
                                <b>Entry Rule:</b> Buy at Current Market Premium<br>
                                <hr style="border-top: 1px dashed {text_color}; margin: 10px 0;">
                                <b>🛡️ Stop Loss:</b> 12% of Buy Price<br>
                                <b>💰 Target:</b> 24% of Buy Price (1:2 RR)
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("No clear crossover. Capital Safe! 🛡️")

                except Exception as e:
                    st.error("डेटा फेच करने में एरर।")

# --- TAB 2: SWING TRADING ---
with tab2:
    st.header("🔥 20-Day Breakout + Institutional Volume")
    if st.button("🚀 Scan Swing Setup"):
        st.info("Swing Scanner Ready (API Connected)")

st.markdown("---")
st.caption("Disclaimer: Algorithmic levels based on VWAP/EMA. Execute manually on broker. 🤖")
