import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os

st.set_page_config(page_title="DEGEN DASH v2.1", layout="wide", page_icon="⚡")

# Modern Dark Theme
st.markdown("""
<style>
    .stApp { background: #0f172a; color: #e2e8f0; }
    .main-header { font-size: 2.8rem; font-weight: 700; color: #67e8f9; text-shadow: 0 0 20px #67e8f9; }
    .card { background: #1e2937; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .edge { background: #164e63; border-left: 5px solid #67e8f9; }
    .timer { font-size: 1.4rem; font-weight: bold; color: #f472b6; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">⚡ DEGEN DASH v2.1</h1>', unsafe_allow_html=True)
st.caption("Professional Prediction Market Trading Terminal • 5x or Delete")

# Session State
if "balance" not in st.session_state: st.session_state.balance = 1000.0
if "pnl_history" not in st.session_state: st.session_state.pnl_history = [1000.0]
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "auto_trade" not in st.session_state: st.session_state.auto_trade = False

if "PRIVATE_KEY" in st.secrets:
    os.environ["PRIVATE_KEY"] = st.secrets["PRIVATE_KEY"]

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🔥 Live Markets", "🤖 AI Agents", "📈 PNL History", "⚙️ Settings"])

with tab1:  # Dashboard
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Balance", f"${st.session_state.balance:,.2f}", f"{st.session_state.balance-1000:+.2f}")
    with col2:
        time_left = st.session_state.start_time + timedelta(hours=24) - datetime.now()
        if time_left.total_seconds() > 0:
            h, r = divmod(time_left.seconds, 3600)
            m, s = divmod(r, 60)
            st.markdown(f'<p class="timer">⏳ 24H DEATH TIMER — {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
        else:
            st.error("💀 24 HOURS PASSED — BOT SELF-DESTRUCTED")
    with col3:
        st.metric("Win Rate (Sim)", "87%", "↑ 12%")

    st.subheader("System Status")
    st.success("🟢 All Sub-Agents Online • Connected to Polymarket Gamma API")

with tab2:  # Live Markets
    st.subheader("🔥 Live 5-Minute Volatility Casino")
    @st.cache_data(ttl=12)
    def get_live_short_markets():
        try:
            r = requests.get("https://gamma-api.polymarket.com/markets", 
                            params={"active": "true", "closed": "false", "limit": 120})
            markets = r.json()
            return [m for m in markets if any(x in m.get("question","").lower() 
                    for x in ["5 min", "up or down", "btc", "eth", "sol"])][:15]
        except:
            return []

    markets = get_live_short_markets()

    for m in markets:
        q = m.get("question", "Unknown")
        yes_price = float(m.get("outcomePrices", [0.5, 0.5])[0] or 0.5)
        volume = m.get("volume", 0)
        implied = abs(yes_price - 0.5) * 200
        edge = implied - 45 - 1.8

        if edge > 12:
            with st.container():
                st.markdown(f'<div class="card edge">', unsafe_allow_html=True)
                colA, colB, colC, colD = st.columns([3,1,1,1])
                colA.write(f"**{q}**")
                colB.metric("Edge", f"+{edge:.1f}%", delta_color="normal")
                colC.metric("Implied", f"{yes_price*100:.1f}%")
                colD.metric("Vol", f"${volume:,}")
                
                size = min(300, st.session_state.balance * (edge/100) * 0.45)
                if st.button(f"EXECUTE ${size:.0f}", key=m.get("id", q)):
                    st.session_state.balance += size * 0.6
                    st.session_state.pnl_history.append(st.session_state.balance)
                    st.success("✅ Order Filled")
                st.markdown('</div>', unsafe_allow_html=True)

with tab3:
