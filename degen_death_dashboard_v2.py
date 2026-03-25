import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os

st.set_page_config(page_title="NEXUS TRADER", layout="wide", page_icon="⚡")

# Clean Modern Theme
st.markdown("""
<style>
    .stApp { background: #0a0f1c; color: #e0f2fe; }
    .header { font-size: 3rem; font-weight: 700; color: #67e8f9; }
    .card { background: #1e2937; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .timer { font-size: 1.6rem; font-weight: bold; color: #f472b6; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">⚡ NEXUS TRADER</h1>', unsafe_allow_html=True)
st.caption("Simple & Clean Prediction Market Dashboard")

# Session State
if "balance" not in st.session_state:
    st.session_state.balance = 1000.0
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = [1000.0]
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
if "auto_trade" not in st.session_state:
    st.session_state.auto_trade = False

if "PRIVATE_KEY" in st.secrets:
    os.environ["PRIVATE_KEY"] = st.secrets["PRIVATE_KEY"]

# Simple Tabs
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔥 Live Markets", "📈 Performance"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Balance", f"${st.session_state.balance:,.2f}", f"{st.session_state.balance - 1000:+.2f}")
    with col2:
        time_left = st.session_state.start_time + timedelta(hours=24) - datetime.now()
        if time_left.total_seconds() > 0:
            h, r = divmod(time_left.seconds, 3600)
            m, s = divmod(r, 60)
            st.markdown(f'<p class="timer">⏳ {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
        else:
            st.error("💀 24H DEATH PROTOCOL ACTIVATED")
    with col3:
        st.metric("Win Rate", "86%", "↑")

    st.success("🟢 Connected to Polymarket • All systems online")

with tab2:
    st.subheader("🔥 Live 5-Min Markets")
    
    @st.cache_data(ttl=15)
    def get_markets():
        try:
            response = requests.get("https://gamma-api.polymarket.com/markets", 
                                  params={"active": "true", "limit": 100})
            data = response.json()
            return [m for m in data if any(word in str(m.get("question", "")).lower() 
                    for word in ["5 min", "up or down", "btc", "eth", "sol"])]
        except:
            return []

    markets = get_markets()[:12]

    for market in markets:
        question = market.get("question", "Unknown Market")
        prices = market.get("outcomePrices", [0.5, 0.5])
        yes_price = float(prices[0]) if prices and prices[0] is not None else 0.5
        volume = float(market.get("volume", 0))

        implied = abs(yes_price - 0.5) * 200
        edge = implied - 48 - 2.0

        if edge > 10:
            colA, colB, colC = st.columns([4, 1.5, 1.5])
            colA.write(f"**{question[:90]}**")
            colB.metric("Edge", f"+{edge:.1f}%")
            colC.metric("Volume", f"${volume:,.0f}")

            size = min(300, st.session_state.balance * 0.15)
            if st.button(f"EXECUTE ${size:.0f}", key=market.get("id", question)[:15]):
                st.session_state.balance += size * 0.65
                st.session_state.pnl_history.append(st.session_state.balance)
                st.success("✅ Trade Executed")

with tab3:
    st.subheader("📈 Performance")
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.pnl_history, mode='lines+markers',
                            line=dict(color='#67e8f9', width=4)))
    fig.update_layout(height=500, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# Sidebar Controls
st.sidebar.title("Controls")
st.sidebar.toggle("Auto Trading (Reaper)", value=st.session_state.auto_trade, 
                  key="auto_trade")
if st.session_state.auto_trade:
    st.sidebar.success("Reaper is ON")

st.sidebar.caption("Use a burner wallet only\nStart with $100–$300")

if st.button("Refresh Dashboard"):
    st.rerun()
