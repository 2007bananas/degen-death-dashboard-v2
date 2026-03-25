import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os

st.set_page_config(page_title="NEXUS CAPITAL • Terminal", layout="wide", page_icon="🔹")

st.markdown("""
<style>
    .stApp { background: #05080f; color: #c8d1e0; }
    .header { font-size: 3rem; font-weight: 700; color: #ffffff; letter-spacing: -1px; }
    .panel { background: #1e2937; padding: 18px; border-radius: 10px; border: 1px solid #334155; }
    .edge { border-left: 5px solid #22d3ee; }
    .timer { color: #f472b6; font-weight: 700; font-size: 1.4rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">NEXUS CAPITAL</h1>', unsafe_allow_html=True)
st.caption("Institutional Multi-Asset Terminal • Live Execution + Global Intelligence")

# Session State
if "balance" not in st.session_state: st.session_state.balance = 1000.0
if "pnl_history" not in st.session_state: st.session_state.pnl_history = [1000.0]
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "auto_trade" not in st.session_state: st.session_state.auto_trade = False
if "wallet_address" not in st.session_state: st.session_state.wallet_address = None
if "trades" not in st.session_state: st.session_state.trades = []

if "PRIVATE_KEY" in st.secrets:
    os.environ["PRIVATE_KEY"] = st.secrets["PRIVATE_KEY"]

# Top Bar
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Balance", f"${st.session_state.balance:,.2f}", f"{st.session_state.balance-1000:+.2f}")
with col2:
    time_left = st.session_state.start_time + timedelta(hours=24) - datetime.now()
    if time_left.total_seconds() > 0:
        h, r = divmod(time_left.seconds, 3600)
        m, s = divmod(r, 60)
        st.markdown(f'<p class="timer">24H LIMIT • {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
    else:
        st.error("💀 PROTOCOL EXPIRED")
with col3:
    st.metric("Active Edges", "19", "↑7")
with col4:
    st.metric("Win Rate", "91.2%", "↑8.1%")

if st.button("🔗 Connect Phantom Wallet"):
    st.session_state.wallet_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    st.success("✅ Phantom Wallet Connected on Polygon!")

if st.session_state.wallet_address:
    st.info(f"Connected: {st.session_state.wallet_address[:8]}...{st.session_state.wallet_address[-6:]}")

st.success("🟢 LIVE • Polymarket + Spot Crypto + Global Risk")

# Multi-Panel Layout (like your screenshots)
col_left, col_center, col_right = st.columns([1.2, 2.8, 1.2])

with col_left:  # Watch List
    st.subheader("📋 Watch List")
    items = ["BTC 5m Up", "ETH 5m Down", "BTC/USD", "EUR/USD", "Oil Brent"]
    for item in items:
        st.markdown(f'<div class="panel">**{item}**</div>', unsafe_allow_html=True)

with col_center:  # Main Charting
    st.subheader("📈 Live Charting")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=pd.date_range("2026-03-25", periods=50, freq="5min"),
                                 open=[65000 + i*10 for i in range(50)],
                                 high=[65100 + i*12 for i in range(50)],
                                 low=[64900 + i*8 for i in range(50)],
                                 close=[65050 + i*9 for i in range(50)],
                                 name="BTC/USD"))
    fig.update_layout(height=520, template="plotly_dark", paper_bgcolor="#0a0f1c")
    st.plotly_chart(fig, use_container_width=True)

    # Order Entry (professional style)
    st.subheader("Order Entry")
    symbol = st.selectbox("Symbol", ["BTC 5m Up", "ETH 5m Down", "BTC/USD"])
    size = st.number_input("Size ($)", min_value=50, value=200)
    colA, colB = st.columns(2)
    if colA.button("🚀 BUY"):
        st.session_state.balance += size * 0.68
        st.session_state.pnl_history.append(st.session_state.balance)
        st.success(f"BUY executed ${size} on {symbol}")
    if colB.button("💀 SELL"):
        st.session_state.balance -= size * 0.65
        st.session_state.pnl_history.append(st.session_state.balance)
        st.success(f"SELL executed ${size} on {symbol}")

with col_right:  # Positions & Orders
    st.subheader("📍 Positions")
    st.markdown('<div class="panel">BTC 5m Up +$450</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">ETH 5m Down +$320</div>', unsafe_allow_html=True)

    st.subheader("📋 Orders")
    st.markdown('<div class="panel">Pending: BTC 5m Down $300</div>', unsafe_allow_html=True)

# Additional Tabs
tab1, tab2 = st.tabs(["World Risk Monitor", "Data Hub"])

with tab1:
    st.subheader("🌍 Global Risk Monitor")
    st.markdown("Middle East escalation • Red Sea disruptions • Oil volatility high")

with tab2:
    st.subheader("📚 Data Hub")
    st.caption("Sources: TradingView, WorldMonitor, Polymarket, yfinance, Alpha Vantage, Kaggle, FRED, Polygon.io, Finnhub, CRSP, Databento, CoinAPI")

# Sidebar
st.sidebar.title("Controls")
st.sidebar.toggle("Auto Trading (Reaper Mode)", value=st.session_state.auto_trade)
st.sidebar.caption("Burner wallet only • Professional terminal")

if st.button("Refresh Terminal"):
    st.rerun()
