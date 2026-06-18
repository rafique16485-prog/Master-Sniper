import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import urllib.parse
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Master Sniper PRO", page_icon="🎯", layout="centered")

# Aapki Link Hardcode kar di gayi hai (No typo possible)
MY_REDIRECT_URI = "https://master-sniper-krnbrvnsmtqr2v7xfr4sdg.streamlit.app"

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    h1, h2, h3 { color: #f8fafc !important; }
    .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(59, 130, 246, 0.3); padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    .neon-blue { color: #3b82f6; } .neon-green { color: #22c55e; font-weight: bold;} .neon-red { color: #ef4444; font-weight: bold;}
    .stButton>button { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; border-radius: 8px; padding: 10px; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

if 'access_token' not in st.session_state:
    st.session_state.access_token = None

st.markdown("<h1>🎯 Money Flow <span class='neon-blue'>Strategy</span></h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["🔌 Upstox Connection", "⚡ Live Execution"])

with tab1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3>🔌 Connect Upstox API</h3>", unsafe_allow_html=True)
    
    # 1. ALREADY CONNECTED
    if st.session_state.access_token:
        st.success("🟢 UPSTOX CONNECTED SUCCESSFULLY!")
        st.write("Ab aap Live Execution tab mein asli data dekh sakte hain.")
        if st.button("Logout"):
            st.session_state.access_token = None
            st.query_params.clear()
            st.rerun()
            
    # 2. RETURNED FROM UPSTOX LOGIN
    elif 'code' in st.query_params:
        auth_code = st.query_params['code']
        st.success("✅ Auth Code Received! (Step 2 of 2)")
        st.warning("Security ke chalte app purani keys bhool gaya hai. Token generate karne ke liye yaha keys dobara daalein.")
        
        api_key_final = st.text_input("API Key (Client ID) *", type="password", key="final_key")
        api_secret_final = st.text_input("API Secret *", type="password", key="final_secret")
        
        # NAYA BUTTON YAHAN HAI 👇
        if st.button("🔑 Generate Access Token"):
            if api_key_final and api_secret_final:
                url = 'https://api.upstox.com/v2/login/authorization/token'
                headers = {'accept': 'application/json', 'Api-Version': '2.0', 'Content-Type': 'application/x-www-form-urlencoded'}
                data = {
                    'code': auth_code,
                    'client_id': api_key_final,
                    'client_secret': api_secret_final,
                    'redirect_uri': MY_REDIRECT_URI,
                    'grant_type': 'authorization_code'
                }
                response = requests.post(url, headers=headers, data=data)
                if response.status_code == 200:
                    st.session_state.access_token = response.json().get('access_token')
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error(f"Failed: {response.text}")
            else:
                st.error("Dono boxes (Key aur Secret) bharna zaroori hai.")
                
    # 3. FRESH LOGIN SCREEN
    else:
        api_key = st.text_input("API Key (Client ID)", type="password")
        st.text_input("Redirect URI (Auto-filled)", value=MY_REDIRECT_URI, disabled=True)
        
        if st.button("🔗 Login with Upstox"):
            if api_key:
                params = {
                    'response_type': 'code',
                    'client_id': api_key,
                    'redirect_uri': MY_REDIRECT_URI
                }
                login_url = f"https://api.upstox.com/v2/login/authorization/dialog?{urllib.parse.urlencode(params)}"
                st.markdown(f"**[👉 CLICK HERE TO LOGIN TO UPSTOX]({login_url})**")
            else:
                st.error("API Key zaroori hai.")

    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📊 Live Market Execution")
    if not st.session_state.access_token:
        st.warning("⚠️ Pehle Upstox API Connect karein (Tab 1 mein).")
    else:
        st.success("API Connected! Ready for Live Option Chain.")
    st.markdown("</div>", unsafe_allow_html=True)

