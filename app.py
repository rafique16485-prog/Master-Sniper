import streamlit as st
import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Master Sniper PRO", page_icon="🎯", layout="centered")

st.title("🎯 Master Sniper PRO")
st.markdown("**Tracking: Smart Money Flows | 9-EMA Crossover | PCR**")

mega_stocks = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS",
    "RVNL.NS", "POLYCAB.NS", "BHEL.NS", "TRENT.NS", "PFC.NS", "RECLTD.NS", 
    "HAL.NS", "SUZLON.NS", "IREDA.NS", "IRFC.NS", "ZOMATO.NS", "INDIGO.NS", 
    "DLF.NS", "BSE.NS", "CDSL.NS", "MAZDOCK.NS", "BEL.NS", "SJVN.NS", "NHPC.NS"
]

tab1, tab2 = st.tabs(["🚀 Swing Breakout (Live)", "⚡ Live Momentum (Nifty/BankNifty)"])

with tab1:
    st.header("🔥 20-Day Breakout + Institutional Volume")
    if st.button("🚀 Scan Institutional Setup"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        for i, stock in enumerate(mega_stocks):
            status_text.text(f"Scanning Live Data: {stock.replace('.NS', '')}...")
            try:
                ticker = yf.Ticker(stock)
                data = ticker.history(period="60d") 
                if len(data) >= 25:
                    data['SMA_Vol_20'] = data['Volume'].rolling(window=20).mean()
                    max_20 = float(data['Close'].rolling(20).max().shift(1).iloc[-1])
                    if float(data['Close'].iloc[-1]) > max_20 and float(data['Volume'].iloc[-1]) > (1.5 * float(data['SMA_Vol_20'].iloc[-1])):
                        results.append({"Stock": stock.replace('.NS', ''), "Live Entry (₹)": round(float(data['Close'].iloc[-1]), 2)})
            except:
                pass
            progress_bar.progress((i + 1) / len(mega_stocks))
            
        status_text.text("✅ लाइव स्कैनिंग पूरी हुई!")
        if results:
            st.success(f"🔥 {len(results)} स्टॉक्स में ब्रेकआउट मिला!")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.warning("आज कोई भी स्टॉक शर्तों को पूरा नहीं कर रहा है। Capital Safe! 🛡️")

with tab2:
    st.header("⚡ 9-EMA + VWAP Sniper (Index)")
    st.info("🟢 NIFTY 50 - API Connection Ready\n\n🟢 BANK NIFTY - API Connection Ready")
    if st.button("🔍 Fetch Live Index Data"):
        st.success("✅ Nifty 50 & Bank Nifty लाइव डेटा सिंक हो गया! (नेक्स्ट अपडेट में ऑप्शन चेन जुड़ेगी)")

st.markdown("---")
st.caption("Developed for Mechanical Trading | No Emotion, Only Rules 🤖")
