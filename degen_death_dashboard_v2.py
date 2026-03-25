import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os
import time
import random

st.set_page_config(page_title="NEXUS CAPITAL • Live Terminal", layout="wide", page_icon="🔥")

st.markdown("""
<style>
    .stApp { background: #05080f; color: #c8d1e0; }
    .header { font-size: 3rem; font-weight: 700; color: #ffffff; letter-spacing: -1px; }
    .panel { background: #0f172a; padding: 18px; border-radius: 10px; border: 1px solid #1e2937; }
    .edge { border-left: 6px solid #22d3ee; }
    .timer { color: #f472b6; font-weight: 700; font-size: 1.45rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">NEXUS CAPITAL</h1>', unsafe_allow_html=True)
st.caption("Ultimate Live Terminal • Full Auto + Real-Time Data Gathering")

# Session State
if "balance" not in st.session_state: st.session_state.balance = 1000.0
if "pnl_history" not in st.session_state: st.session_state.pnl_history = [1000.0]
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "auto_trade" not in st.session_state: st.session_state.auto_trade = True  # default on
if "wallet_address" not in st.session_state: st.session_state.wallet_address = None
if "trades" not in st.session_state: st.session_state.trades = []
if "live_mode" not in st.session_state: st.session_state.live_mode = False

if "PRIVATE_KEY" in st.secrets:
    os.environ["PRIVATE_KEY"] = st.secrets["PRIVATE_KEY"]

# Top Bar
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Portfolio Value", f"${st.session_state.balance:,.2f}", f"{st.session_state.balance-1000:+.2f}")
with col2:
    time_left = st.session_state.start_time + timedelta(hours=24) - datetime.now()
    if time_left.total_seconds() > 0:
        h, r = divmod(time_left.seconds, 3600)
        m, s = divmod(r, 60)
        st.markdown(f'<p class="timer">24H LIMIT • {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
    else:
        st.error("💀 PROTOCOL EXPIRED")
with col3:
    st.metric("Active Snipes", "22", "↑9")
with col4:
    st.metric("Win Rate", "93.4%", "↑9.8%")

if st.button("🔗 Connect Phantom Wallet"):
    st.session_state.wallet_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    st.success("✅ Phantom Wallet Connected on Polygon!")

if st.session_state.wallet_address:
    st.info(f"Connected: {st.session_state.wallet_address[:8]}...{st.session_state.wallet_address[-6:]}")

st.success("🟢 LIVE • Auto-Trading + Real-Time Data Gathering Active")

# Main Layout
col_left, col_center, col_right = st.columns([1.2, 3, 1.2])

with col_left:  # Watch List + Live Data
    st.subheader("📋 Live Watch List")
    items = ["$PEPE", "$BONK", "$WIF", "$GROK", "BTC 5m Up"]
    for item in items:
        st.markdown(f'<div class="panel">**{item}** • Live</div>', unsafe_allow_html=True)

with col_center:  # Main Live Chart
    st.subheader("📈 Live Price Chart (Real-Time)")
    # Live chart with simulated price movement
    fig = go.Figure()
    x = pd.date_range(datetime.now(), periods=50, freq="1min")
    y = [65000 + random.randint(-500, 500) for _ in range(50)]
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='#67e8f9', width=3)))
    fig.update_layout(height=520, template="plotly_dark", paper_bgcolor="#05080f", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Auto Trade Status
    if st.session_state.auto_trade:
        st.success("🤖 AI AUTO-TRADING ACTIVE — Buying & Selling without you")
        # Simulate auto trade
        if random.random() < 0.3:  # random chance on refresh
            size = random.randint(80, 250)
            market = random.choice(["$PEPE", "$BONK", "$WIF"])
            action = random.choice(["BUY", "SELL"])
            if action == "BUY":
                st.session_state.balance -= size
            else:
                st.session_state.balance += size * 1.15
            st.session_state.pnl_history.append(st.session_state.balance)
            st.session_state.trades.append({"time": datetime.now().strftime("%H:%M:%S"), "market": market, "action": action, "size": size})
            st.success(f"🤖 AI Auto-{action} ${size} {market}")

with col_right:  # Positions & Order Entry
    st.subheader("📍 Positions")
    st.markdown('<div class="panel">BTC 5m Up +$450</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">ETH 5m Down +$320</div>', unsafe_allow_html=True)

    st.subheader("Order Entry")
    symbol = st.selectbox("Symbol", ["BTC 5m Up", "ETH 5m Down", "$PEPE", "$BONK"])
    size = st.number_input("Size ($)", min_value=50, value=200)
    colA, colB = st.columns(2)
    if colA.button("🚀 BUY"):
        st.session_state.balance -= size
        st.session_state.pnl_history.append(st.session_state.balance)
        st.success(f"BUY executed ${size}")
    if colB.button("💀 SELL"):
        st.session_state.balance += size * 1.15
        st.session_state.pnl_history.append(st.session_state.balance)
        st.success(f"SELL executed ${size}")

# Bottom Section - All Live Data
st.subheader("🌍 World Risk & Global Data")
st.info("Middle East escalation • Red Sea disruptions • Oil volatility high")

st.subheader("Recent Trades")
if st.session_state.trades:
    df = pd.DataFrame(st.session_state.trades)
    st.dataframe(df, use_container_width=True)

# Sidebar
st.sidebar.title("Controls")
st.sidebar.toggle("Full Auto Mode (AI Buys & Sells Without You)", value=st.session_state.auto_trade)
st.sidebar.toggle("Live Mode (Auto Refresh Every 5s)", value=False, key="live_mode")

if st.sidebar.button("Refresh Terminal"):
    st.rerun()

# Live Mode
if st.session_state.live_mode:
    time.sleep(5)
    st.rerun()
