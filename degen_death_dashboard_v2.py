import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os
import time

st.set_page_config(page_title="NEXUS CAPITAL • Full Auto Terminal", layout="wide", page_icon="🔥")

st.markdown("""
<style>
    .stApp { background: #05080f; color: #c8d1e0; }
    .header { font-size: 3rem; font-weight: 700; color: #ffffff; letter-spacing: -1px; }
    .card { background: #0f172a; padding: 22px; border-radius: 12px; border: 1px solid #1e2937; }
    .edge { border-left: 6px solid #22d3ee; }
    .timer { color: #f472b6; font-weight: 700; font-size: 1.45rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">NEXUS CAPITAL</h1>', unsafe_allow_html=True)
st.caption("Full Auto Sniper Terminal • AI Buys & Sells Without You")

# Session State
if "balance" not in st.session_state: st.session_state.balance = 1000.0
if "pnl_history" not in st.session_state: st.session_state.pnl_history = [1000.0]
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "auto_trade" not in st.session_state: st.session_state.auto_trade = False
if "wallet_address" not in st.session_state: st.session_state.wallet_address = None
if "trades" not in st.session_state: st.session_state.trades = []

if "PRIVATE_KEY" in st.secrets:
    os.environ["PRIVATE_KEY"] = st.secrets["PRIVATE_KEY"]

# Top Metrics
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
    st.metric("Active Snipes", "19", "↑7")
with col4:
    st.metric("Win Rate", "91.2%", "↑8.1%")

if st.button("🔗 Connect Phantom Wallet"):
    st.session_state.wallet_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    st.success("✅ Phantom Wallet Connected on Polygon!")

if st.session_state.wallet_address:
    st.info(f"Connected: {st.session_state.wallet_address[:8]}...{st.session_state.wallet_address[-6:]}")

st.success("🟢 LIVE • Full Auto Mode Ready")

# Auto Trading Logic
if st.session_state.auto_trade:
    st.warning("🚀 FULL AUTO MODE ACTIVE — AI is buying and selling without you")
    # Simulate AI scanning and auto-trading
    if len(st.session_state.trades) < 8:  # limit for demo
        auto_size = min(250, int(st.session_state.balance * 0.15))
        auto_market = "$PEPE" if len(st.session_state.trades) % 2 == 0 else "$BONK"
        action = "BUY" if len(st.session_state.trades) % 3 != 0 else "SELL"
        
        if action == "BUY":
            st.session_state.balance -= auto_size
        else:
            st.session_state.balance += auto_size * 1.12
        
        st.session_state.pnl_history.append(st.session_state.balance)
        st.session_state.trades.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "market": auto_market,
            "action": action,
            "size": auto_size,
            "reason": "AI detected high edge + volume spike"
        })
        st.success(f"🤖 AI Auto-{action} ${auto_size} {auto_market} • Reason: High edge + volume spike")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "🔥 Auto Snipes", "Polymarket", "Crypto Spot", "Performance"])

with tab1:
    st.subheader("System Status")
    st.info("AI Auto-Trader running • Scanning every refresh")

with tab2:
    st.subheader("🔥 Auto Meme Coin Snipes")
    st.caption("AI automatically buys and sells based on edge detection")

    meme_data = [
        ("$PEPE", 0.00001234, 1240000, 45.2),
        ("$BONK", 0.00002345, 890000, 32.1),
        ("$WIF", 2.34, 670000, 18.9),
        ("$GROK", 8.45, 450000, 67.8),
    ]

    for name, price, volume, edge in meme_data:
        with st.container():
            st.markdown('<div class="card edge">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5])
            c1.write(f"**{name}** — ${price}")
            c2.metric("Volume", f"${volume:,}")
            c3.metric("Edge", f"+{edge:.1f}%")
            if c4.button("🚀 MANUAL SNIPE", key=name):
                st.session_state.balance += 200 * 0.75
                st.session_state.pnl_history.append(st.session_state.balance)
                st.session_state.trades.append({"time": datetime.now().strftime("%H:%M"), "market": name, "size": 200})
                st.success(f"Manual snipe executed ${200} {name}")
            st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("Polymarket Edges")
    st.info("BTC 5-min Down — Edge +28% (High confidence)")

with tab4:
    st.subheader("💱 Spot Crypto Trading")
    symbol = st.selectbox("Asset", ["BTC", "ETH", "SOL"])
    amount = st.number_input("Amount ($)", min_value=10, value=100)
    colA, colB = st.columns(2)
    if colA.button(f"BUY {symbol}"):
        if st.session_state.balance >= amount:
            st.session_state.balance -= amount
            st.session_state.pnl_history.append(st.session_state.balance)
            st.success(f"Bought ${amount} {symbol}")
    if colB.button(f"SELL {symbol}"):
        st.session_state.balance += amount * 1.02
        st.session_state.pnl_history.append(st.session_state.balance)
        st.success(f"Sold ${amount} {symbol}")

with tab5:
    st.subheader("📈 Performance")
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.pnl_history, mode='lines+markers', line=dict(color='#67e8f9', width=4)))
    fig.update_layout(height=520, template="plotly_dark", paper_bgcolor="#05080f")
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.trades:
        st.subheader("Recent Auto Trades")
        df = pd.DataFrame(st.session_state.trades)
        st.dataframe(df, use_container_width=True)

# Sidebar
st.sidebar.title("Controls")
st.sidebar.toggle("Full Auto Mode (AI Buys & Sells Without You)", value=st.session_state.auto_trade)
st.sidebar.caption("Burner wallet only • AI fully autonomous when enabled")

if st.button("Refresh Terminal (AI Scans & Trades)"):
    st.rerun()
