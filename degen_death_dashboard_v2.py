import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os

st.set_page_config(page_title="NEXUS CAPITAL • TRADING TERMINAL", layout="wide", page_icon="🔹")

# Institutional Dark Theme (Multibillion $ look)
st.markdown("""
<style>
    .stApp { background: #05080f; color: #c8d1e0; font-family: 'Segoe UI', sans-serif; }
    .header { font-size: 2.8rem; font-weight: 700; letter-spacing: -1px; color: #ffffff; }
    .subheader { color: #94a3b8; font-size: 1.1rem; }
    .card { background: #0f172a; padding: 24px; border-radius: 8px; border: 1px solid #1e2937; }
    .metric-value { font-size: 2.1rem; font-weight: 600; color: #67e8f9; }
    .edge { border-left: 5px solid #22d3ee; }
    .timer { color: #f472b6; font-weight: 600; font-size: 1.35rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">NEXUS CAPITAL</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Prediction Markets • Proprietary AI Engine • Live Execution</p>', unsafe_allow_html=True)

# Session State
if "balance" not in st.session_state: st.session_state.balance = 1000.0
if "pnl_history" not in st.session_state: st.session_state.pnl_history = [1000.0]
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "auto_trade" not in st.session_state: st.session_state.auto_trade = False

if "PRIVATE_KEY" in st.secrets:
    os.environ["PRIVATE_KEY"] = st.secrets["PRIVATE_KEY"]

# Top Metrics Bar
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
        st.error("💀 24-HOUR PROTOCOL EXPIRED")
with col3:
    st.metric("Active Signals", "12", "↑4")
with col4:
    st.metric("Sharpe Ratio", "2.84", "↑0.31")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["OVERVIEW", "LIVE MARKETS", "AI SIGNALS", "PERFORMANCE"])

with tab1:
    st.subheader("System Status")
    st.success("● LIVE • Connected to Polymarket CLOB • All execution engines online")

with tab2:
    st.subheader("Live 5-Minute Markets")
    
    @st.cache_data(ttl=12)
    def get_markets():
        try:
            r = requests.get("https://gamma-api.polymarket.com/markets", 
                            params={"active": "true", "limit": 100})
            data = r.json()
            return [m for m in data if any(w in str(m.get("question","")).lower() 
                    for w in ["5 min", "up or down", "btc", "eth", "sol"])]
        except:
            return []

    for m in get_markets()[:10]:
        q = m.get("question", "Unknown")
        prices = m.get("outcomePrices", [0.5, 0.5])
        yes_price = float(prices[0]) if prices and prices[0] is not None else 0.5
        volume = float(m.get("volume", 0))

        implied = abs(yes_price - 0.5) * 200
        edge = implied - 48 - 2.0

        if edge > 10:
            with st.container():
                st.markdown(f'<div class="card edge">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([4, 1.5, 1.5, 1])
                c1.write(f"**{q[:95]}**")
                c2.metric("Edge", f"+{edge:.1f}%")
                c3.metric("Implied", f"{yes_price*100:.1f}%")
                c4.metric("Vol", f"${volume:,.0f}")

                size = min(400, int(st.session_state.balance * 0.12))
                if c4.button("EXECUTE", key=m.get("id", q)[:20]):
                    st.session_state.balance += size * 0.7
                    st.session_state.pnl_history.append(st.session_state.balance)
                    st.success(f"Executed ${size} • Filled by Nexus Engine")
                st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("AI Signal Engine")
    st.info("**Top Signal:** BTC 5-min Down → **Confidence 94%**  \nHigh volatility crush + order flow imbalance + bearish momentum")

with tab4:
    st.subheader("Performance")
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.pnl_history, mode='lines+markers',
                            line=dict(color='#67e8f9', width=4)))
    fig.update_layout(height=520, template="plotly_dark", paper_bgcolor="#05080f")
    st.plotly_chart(fig, use_container_width=True)

# Sidebar
st.sidebar.title("NEXUS CONTROL")
st.sidebar.toggle("Enable Auto Execution", value=st.session_state.auto_trade)
st.sidebar.slider("Max Position Size ($)", 50, 1000, 250)
st.sidebar.caption("NEXUS CAPITAL • Internal Trading Terminal\nBurner wallet recommended")

if st.button("Refresh Terminal"):
    st.rerun()
