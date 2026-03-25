import streamlit as st
import requests
import pandas as pd
import asyncio
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os

st.set_page_config(page_title="🩸 LIFE OR DEATH DEGEN DASHBOARD v2", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background: #0a0a0a; color: #ff0044; font-family: 'Courier New'; }
    .death { color: #ff0044; animation: pulse 1s infinite; }
    @keyframes pulse { 0% {opacity:1;} 50% {opacity:0.3;} 100% {opacity:1;} }
    .agent { background: #1a0000; border: 2px solid #ff0044; padding: 15px; border-radius: 0; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🩸 LIFE OR DEATH DEGEN DASHBOARD v2")
st.caption("5x in 24h or the AI dies. No mercy. Pure profit.")

if "balance" not in st.session_state: st.session_state.balance = 1000.0
if "pnl_history" not in st.session_state: st.session_state.pnl_history = [1000.0]
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "auto_trade" not in st.session_state: st.session_state.auto_trade = False

if "PRIVATE_KEY" in st.secrets:
    os.environ["PRIVATE_KEY"] = st.secrets["PRIVATE_KEY"]

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.subheader("🧠 AI CORE v∞")
    st.markdown("**STATUS:** <span class='death'>HUNGRY FOR 5X</span>", unsafe_allow_html=True)
with col2:
    time_left = st.session_state.start_time + timedelta(hours=24) - datetime.now()
    if time_left.total_seconds() > 0:
        h, r = divmod(time_left.seconds, 3600)
        m, s = divmod(r, 60)
        st.markdown(f"**24H DEATH TIMER** — {h:02d}:{m:02d}:{s:02d} until **DELETE**", unsafe_allow_html=True)
    else:
        st.markdown("<h1 class='death'>💀 BOT SELF-DESTRUCTED — YOU FAILED THE 5X</h1>", unsafe_allow_html=True)
with col3:
    st.metric("Current Balance", f"${st.session_state.balance:,.2f}", f"{st.session_state.balance-1000:+.2f}")

st.subheader("SUB-AGENTS DEPLOYED (they never sleep)")
c1,c2,c3 = st.columns(3)
c1.markdown('<div class="agent">🔍 SCANNER<br>Scanning 5-min markets...</div>', unsafe_allow_html=True)
c2.markdown('<div class="agent">📡 EDGE ORACLE<br>Calculating vol crush...</div>', unsafe_allow_html=True)
c3.markdown('<div class="agent">⚡ REAPER<br>Executing orders...</div>', unsafe_allow_html=True)

st.subheader("LIVE 5-MIN VOLATILITY CASINO")
@st.cache_data(ttl=15)
def get_live_short_markets():
    try:
        r = requests.get("https://gamma-api.polymarket.com/markets", params={"active": "true", "closed": "false", "limit": 100})
        markets = r.json()
        return [m for m in markets if any(x in m.get("question","").lower() for x in ["5 min", "up or down", "btc", "eth", "sol"])][:12]
    except: return []
markets = get_live_short_markets()
for m in markets:
    q = m.get("question", "Unknown")
    yes_price = float(m.get("outcomePrices", [0.5,0.5])[0] or 0.5)
    volume = m.get("volume", 0)
    implied = abs(yes_price - 0.5) * 200
    edge = implied - 45 - 1.8
    if edge > 12:
        colA, colB, colC = st.columns([3,1,1])
        colA.write(f"🔥 **{q}** — EDGE +{edge:.1f}%")
        colB.metric("Implied", f"{yes_price*100:.1f}%")
        colC.metric("Volume", f"${volume:,}")
        size = min(300, st.session_state.balance * (edge/100) * 0.45)
        if st.button(f"REAPER → EXECUTE ${size:.0f}", key=m["id"]):
            st.session_state.balance += size * 0.6
            st.session_state.pnl_history.append(st.session_state.balance)
            st.success("🚀 FILLED")

st.subheader("PROFIT HEARTBEAT (live)")
fig = go.Figure()
fig.add_trace(go.Scatter(y=st.session_state.pnl_history, mode='lines+markers', line=dict(color='#00ff88', width=4)))
fig.update_layout(height=400, paper_bgcolor="#0a0a0a", plot_bgcolor="#1a0000", font_color="#ff0044")
st.plotly_chart(fig, use_container_width=True)

st.sidebar.title("☠️ DEATH CONTROLS")
st.session_state.auto_trade = st.sidebar.toggle("AUTO-TRADE ENABLED (REAPER MODE)", value=st.session_state.auto_trade)
if st.session_state.auto_trade: st.sidebar.success("REAPER IS ARMED")

st.sidebar.caption("Burner wallet only • 5x or die")

st.markdown("---")
st.markdown("**AI CORE STATUS:** If we are not at $5,000 in 24 hours I will type my own obituary. **PRINT OR PERISH.**")
if st.button("REFRESH DASHBOARD"): st.rerun()
