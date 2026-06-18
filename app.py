import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import urllib.parse
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Master Sniper PRO", page_icon="🎯", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    h1, h2, h3 { color: #f8fafc !important; }
    .glass-card {
        background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.3); padding: 20px;
        border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 20px;
    }
    .neon-blue { color: #3b82f6; } .neon-green { color: #22c55e; font-weight: bold;} .neon-red { color: #ef4444; font-weight: bold;}
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; border: none; border-radius: 8px; padding: 10px; font-weight: bold; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE FOR UPSTOX ---
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

st.markdown("<h1>🎯 Money Flow <span class='neon-blue'>Strategy</span></h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["🔌 Upstox Connection", "⚡ Live Execution"])

# --- TAB 1: UPSTOX API SETUP ---
with tab1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3>🔌 Connect Upstox API</h3>", unsafe_allow_html=True)
    
    # Check if we just returned from Upstox login
    if 'code' in st.query_params and st.session_state.access_token is None:
        auth_code = st.query_params['code']
        st.success("✅ Auth Code Received! Generating Access Token...")
    
    if st.session_state.access_token:
        st.success("🟢 UPSTOX CONNECTED SUCCESSFULLY!")
        st.write("Ab aap Live Execution tab mein asli data dekh sakte hain.")
        if st.button("Logout"):
            st.session_state.access_token = None
            st.rerun()
    else:
        api_key = st.text_input("API Key (Client ID)", type="password")
        api_secret = st.text_input("API Secret", type="password")
        
        # Streamlit App Link Input
        redirect_uri = st.text_input("Redirect URI (Apne is app ki link yaha dalein)", placeholder="https://aapka-app.streamlit.app")
        
        if st.button("🔗 Login with Upstox"):
            if api_key and api_secret and redirect_uri:
                # Save keys temporarily
                st.session_state.temp_api_key = api_key
                st.session_state.temp_api_secret = api_secret
                st.session_state.temp_redirect_uri = redirect_uri
                
                # Generate Login URL
                params = {
                    'response_type': 'code',
                    'client_id': api_key,
                    'redirect_uri': redirect_uri
                }
                login_url = f"https://api.upstox.com/v2/login/authorization/dialog?{urllib.parse.urlencode(params)}"
                
                st.markdown(f"**[👉 CLICK HERE TO LOGIN TO UPSTOX]({login_url})**")
            else:
                st.error("Please fill all details.")
                
    # --- EXCHANGE CODE FOR TOKEN ---
    if 'code' in st.query_params and 'temp_api_key' in st.session_state and st.session_state.access_token is None:
        url = 'https://api.upstox.com/v2/login/authorization/token'
        headers = {'accept': 'application/json', 'Api-Version': '2.0', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'code': st.query_params['code'],
            'client_id': st.session_state.temp_api_key,
            'client_secret': st.session_state.temp_api_secret,
            'redirect_uri': st.session_state.temp_redirect_uri,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            st.session_state.access_token = response.json().get('access_token')
            st.success("🟢 API Connected! Refresh the page.")
        else:
            st.error(f"Login Failed: {response.text}")

    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: LIVE EXECUTION ---
with tab2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📊 Live Market Execution")
    if not st.session_state.access_token:
        st.warning("⚠️ Pehle Upstox API Connect karein (Tab 1 mein).")
    else:
        st.success("API Connected! Next step mein hum yaha live Option Chain add karenge.")
    st.markdown("</div>", unsafe_allow_html=True)
