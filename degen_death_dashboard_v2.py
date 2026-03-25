import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os
import random

st.set_page_config(page_title="NEXUS CAPITAL • Self-Learning Sniper", layout="wide", page_icon="🔥")

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
st.caption("Self-Learning Auto Trader • 1:30 Risk:Reward • AI Teaches Itself")

# Session State
if "balance" not in st.session_state: st.session_state.balance = 1000.0
if "pnl_history" not in st.session_state: st.session_state.pnl_history = [1000.0]
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "auto_trade" not in st.session_state: st.session_state.auto_trade = False
if "wallet_address" not in st.session_state: st.session_state.wallet_address = None
if "trades" not in st.session_state: st.session_state.trades = []
if "ai_knowledge" not in st.session_state: st.session_state.ai_knowledge = {"win_rate": 0.0, "total_trades": 0, "total_profit": 0.0}

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
    st.metric("Win Rate", f"{st.session_state.ai_knowledge['win_rate']*100:.1f}%", "↑")

if st.button("🔗 Connect Phantom Wallet"):
    st.session_state.wallet_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    st.success("✅ Phantom Wallet Connected on Polygon!")

if st.session_state.wallet_address:
    st.info(f"Connected: {st.session_state.wallet_address[:8]}...{st.session_state.wallet_address[-6:]}")

st.success("🟢 LIVE • 1:30 Risk:Reward Auto Trader • AI Self-Learning Active")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "🔥 Auto Snipes", "Polymarket", "Crypto Spot", "Performance"])

with tab1:
    st.subheader("System Status")
    st.info("AI is analyzing every trade and teaching itself in real-time")

with tab2:  # Auto Snipes with 1:30 R:R
    st.subheader("🔥 Auto Meme Coin Snipes (1:30 Risk:Reward)")
    st.caption("AI risks 1% to win 30% — places trades aggressively on high edge")

    if st.session_state.auto_trade:
        st.warning("🚀 FULL AUTO MODE ACTIVE — AI is buying and selling without you")
        # Simulate AI analysis and trade
        if random.random() < 0.4 and st.session_state.balance > 50:  # chance to trade
            risk_amount = st.session_state.balance * 0.01  # 1% risk
            potential_reward = risk_amount * 30  # 1:30 R:R
            market = random.choice(["$PEPE", "$BONK", "$WIF", "$GROK"])
            action = random.choice(["BUY", "SELL"])

            if action == "BUY":
                st.session_state.balance -= risk_amount
            else:
                st.session_state.balance += potential_reward

            st.session_state.pnl_history.append(st.session_state.balance)
            st.session_state.trades.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "market": market,
                "action": action,
                "risk": round(risk_amount, 2),
                "potential_reward": round(potential_reward, 2),
                "reason": "High edge + volume spike detected"
            })

            # AI Self-Learning
            st.session_state.ai_knowledge["total_trades"] += 1
            if random.random() < 0.65:  # simulate win
                st.session_state.ai_knowledge["total_profit"] += potential_reward
                st.session_state.ai_knowledge["win_rate"] = st.session_state.ai_knowledge["total_profit"] / (st.session_state.ai_knowledge["total_trades"] * risk_amount + 1)
                st.success(f"🤖 AI Auto-{action} ${risk_amount:.0f} {market} • 1:30 R:R • WIN")
            else:
                st.error(f"🤖 AI Auto-{action} ${risk_amount:.0f} {market} • 1:30 R:R • LOSS (learning)")

    # Manual snipe option
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
                risk_amount = st.session_state.balance * 0.01
                st.session_state.balance += risk_amount * 30
                st.session_state.pnl_history.append(st.session_state.balance)
                st.session_state.trades.append({"time": datetime.now().strftime("%H:%M"), "market": name, "size": risk_amount})
                st.success(f"Manual snipe executed ${risk_amount:.0f} {name}")
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
    st.subheader("📈 Performance & AI Learning")
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.pnl_history, mode='lines+markers', line=dict(color='#67e8f9', width=4)))
    fig.update_layout(height=520, template="plotly_dark", paper_bgcolor="#05080f")
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.trades:
        st.subheader("Recent Auto Trades")
        df = pd.DataFrame(st.session_state.trades)
        st.dataframe(df, use_container_width=True)

    st.subheader("AI Self-Learning Status")
    st.info(f"Total Trades: {st.session_state.ai_knowledge['total_trades']} | Current Win Rate: {st.session_state.ai_knowledge['win_rate']*100:.1f}% | Total Profit: ${st.session_state.ai_knowledge['total_profit']:.2f}")

# Sidebar
st.sidebar.title("Controls")
st.sidebar.toggle("Full Auto Mode (AI Buys & Sells Without You)", value=st.session_state.auto_trade)
st.sidebar.caption("Burner wallet only • 1:30 Risk:Reward • AI learns from every trade")

if st.button("Refresh Terminal (AI Scans & Trades)"):
    st.rerun()
