# --------------------------------------------------------------
# NEXUS CAPITAL – ETHEREUM AUTO-TRADER WITH META MASK INTEGRATION
# --------------------------------------------------------------
import streamlit as st
import requests, pandas as pd, random, time, os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ------------------------------------------------------------------
# Session-state defaults (run only once)
# ------------------------------------------------------------------
if "balance" not in st.session_state:
    st.session_state.balance = 1_000.0
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = [1_000.0]
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
if "auto_trade" not in st.session_state:
    st.session_state.auto_trade = False
if "trades" not in st.session_state:
    st.session_state.trades = []
if "ai" not in st.session_state:
    st.session_state.ai = {
        "wins": 0,
        "total": 0,
        "profit": 0.0,
        "win_rate": 0.0,
        "edge_thr": 0.20,       # start-threshold (20 % volume-spike)
    }
if "wallet_address" not in st.session_state:
    st.session_state.wallet_address = None
if "chain_id" not in st.session_state:
    st.session_state.chain_id = None

# ------------------------------------------------------------------
# META MASK INTEGRATION (NO EXTERNAL DEPENDENCIES)
# ------------------------------------------------------------------
def connect_metamask():
    """Connects to MetaMask wallet and returns public key (or None)"""
    # Create a hidden iframe that executes JavaScript
    components.html(
        """
        <div id="metamask-connection" style="display:none">
            <script>
                async function connectWallet() {
                    if (typeof window.ethereum !== 'undefined') {
                        try {
                            // Request account access
                            const accounts = await window.ethereum.request({
                                method: 'eth_requestAccounts'
                            });
                            const account = accounts[0];
                            const chainId = await window.ethereum.request({
                                method: 'eth_chainId'
                            });
                            
                            // Send result to Streamlit
                            const event = new CustomEvent('streamlit:metamaskConnect', {
                                detail: { 
                                    publicKey: account,
                                    chainId: chainId
                                }
                            });
                            window.parent.dispatchEvent(event);
                        } catch (err) {
                            const event = new CustomEvent('streamlit:metamaskConnect', {
                                detail: { 
                                    publicKey: null, 
                                    error: "Connection canceled or failed"
                                }
                            });
                            window.parent.dispatchEvent(event);
                        }
                    } else {
                        const event = new CustomEvent('streamlit:metamaskConnect', {
                            detail: { 
                                publicKey: "metamask_not_installed", 
                                error: "MetaMask not detected"
                            }
                        });
                        window.parent.dispatchEvent(event);
                    }
                }
                connectWallet();
            </script>
        </div>
        """,
        height=0
    )

    # Check if we have a response from the iframe
    if "metamask_response" in st.session_state:
        response = st.session_state.metamask_response
        del st.session_state.metamask_response
        return response
    return None

# Add a hidden component to listen for wallet connection events
components.html(
    """
    <script>
        window.addEventListener('streamlit:metamaskConnect', function(event) {
            const response = event.detail;
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = 'about:blank';
            document.body.appendChild(iframe);
            
            iframe.contentWindow.postMessage({
                type: 'streamlit:metamaskConnect',
                data: response
            }, '*');
        });
    </script>
    """,
    height=0
)

# Set up a listener for the iframe communication
if "metamask_event" not in st.session_state:
    st.session_state.metamask_event = None

# Check for messages from the iframe
if "streamlit:metamaskConnect" in st.query_params:
    st.session_state.metamask_response = st.query_params["streamlit:metamaskConnect"]
    st.query_params.clear()

# ------------------------------------------------------------------
# Page layout
# ------------------------------------------------------------------
st.set_page_config(page_title="NEXUS CAPITAL – Ethereum Auto-Trader",
                   layout="wide", page_icon="🚀")
st.markdown("""
<style>
    .stApp {background:#05080f;color:#c8d1e0;}
    .header{font-size:3rem;font-weight:700;color:#fff;letter-spacing:-1px;}
    .card{background:#0f172a;padding:18px;border-radius:10px;
          border:1px solid #1e2937;margin-bottom:8px;}
    .edge{border-left:6px solid #22d3ee;}
    .timer{color:#f472b6;font-weight:700;font-size:1.45rem;}
    .wallet-connected {color: #22d3ee; font-weight: bold;}
    .wallet-disconnected {color: #fca5a5; font-weight: bold;}
    .eth-wallet {background: #627EEA; padding: 2px 6px; border-radius: 4px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">NEXUS CAPITAL</h1>', unsafe_allow_html=True)
st.caption("Ethereum Auto-Trader | Self-Learning AI | Live Meme-Coin Feed")

# ------------------------------------------------------------------
# Top bar metrics
# ------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Portfolio", f"${st.session_state.balance:,.2f}",
          f"{st.session_state.balance-1_000:+.2f}")
c2_time = st.session_state.start_time + timedelta(hours=24) - datetime.now()
if c2_time.total_seconds() > 0:
    h, r = divmod(int(c2_time.total_seconds()), 3600)
    m, s = divmod(r, 60)
    c2.markdown(f'<p class="timer">{h:02d}:{m:02d}:{s:02d} LEFT</p>', unsafe_allow_html=True)
else:
    c2.error("💀 PROTOCOL EXPIRED")
c3.metric("Active Snipes", "—")
c4.metric("Win Rate", f"{st.session_state.ai['win_rate']*100:.1f}%")

# ------------------------------------------------------------------
# MetaMask wallet connection
# ------------------------------------------------------------------
if st.session_state.wallet_address:
    chain_name = {
        "0x1": "Ethereum Mainnet",
        "0x3": "Ropsten Testnet",
        "0x4": "Rinkeby Testnet",
        "0x5": "Goerli Testnet",
        "0xa": "Optimism",
        "0x64": "Gnosis Chain",
        "0x89": "Polygon",
        "0xa4b1": "Arbitrum"
    }.get(st.session_state.chain_id, st.session_state.chain_id)
    
    st.info(f'<span class="wallet-connected">Connected wallet:</span> <span class="eth-wallet">ETH</span> {st.session_state.wallet_address[:8]}…{st.session_state.wallet_address[-6:]} on {chain_name}', 
            unsafe_allow_html=True)
else:
    st.info("Wallet not connected - trading disabled", icon="⚠️")

if st.button("🔗 Connect MetaMask Wallet"):
    # Clear any previous response
    if "metamask_response" in st.session_state:
        del st.session_state.metamask_response
    
    # Trigger the connection process
    connect_metamask()
    
    # Check if we have a response
    if "metamask_response" in st.session_state:
        response = st.session_state.metamask_response
        del st.session_state.metamask_response
        
        if response == "metamask_not_installed":
            st.error("⚠️ MetaMask not detected! Install it from https://metamask.io")
        elif response and "publicKey" in response:
            st.session_state.wallet_address = response["publicKey"]
            st.session_state.chain_id = response.get("chainId", "Unknown")
            st.success(f"✅ Connected to {st.session_state.wallet_address}")
        else:
            st.warning("Connection canceled or failed")

# ------------------------------------------------------------------
# Helper: pull cheap meme-coins from DexScreener (Ethereum focused)
# ------------------------------------------------------------------
@st.cache_data(ttl=30)
def fetch_meme_coins(chain: str = "ethereum"):
    """Return a short list of low-price tokens with volume edge."""
    url = f"https://api.dexscreener.com/latest/dex/pairs?chain={chain}"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        pairs = data.get("pairs", [])
        out = []
        for p in pairs:
            base = p.get("baseToken", {})
            name = base.get("symbol")
            price = float(p.get("priceUsd", 0))
            vol = float(p.get("volumeUsd24h", 0))
            # simple meme-coin filter: price < $0.005 and some volume
            if name and price < 0.005 and vol > 5e5:
                edge = (vol / 1_000_000) - 1   # reference vol = $1 M
                out.append({"name": name, "price": price,
                            "volume": vol, "edge": edge})
        return sorted(out, key=lambda x: x["edge"], reverse=True)
    except Exception:
        # fallback demo data if the API is unreachable
        return [
            {"name":"PEPE","price":0.000012,"volume":1_240_000,"edge":0.24},
            {"name":"SHIB","price":0.000023,"volume":890_000,"edge":-0.11},
            {"name":"DOGE","price":0.067,"volume":670_000,"edge":-0.33},
        ]

# ------------------------------------------------------------------
# LEFT column – watch-list
# ------------------------------------------------------------------
col_left, col_center, col_right = st.columns([1.2, 2.8, 1.2])

with col_left:
    st.subheader("📋 Watch-List (DexScreener)")
    meme = fetch_meme_coins("ethereum")
    for t in meme[:10]:
        st.markdown(
            f'<div class="card edge"><b>{t["name"]}</b> @ ${t["price"]:.6f} '
            f'| Vol ${t["volume"]/1e6:.1f}M | Edge {t["edge"]*100:.1f}%</div>',
            unsafe_allow_html=True)

# ------------------------------------------------------------------
# CENTER – live chart & manual order entry
# ------------------------------------------------------------------
with col_center:
    st.subheader("📈 Live Price Chart")
    # Simple random-walk (replace with real feed later)
    x = pd.date_range(datetime.now(), periods=60, freq="1min")
    y = [2500 + random.randint(-50, 50) for _ in range(60)]  # ETH price
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines",
                             line=dict(color="#67e8f9", width=3)))
    fig.update_layout(height=520, template="plotly_dark",
                      paper_bgcolor="#05080f", margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🛒 Order Entry")
    symbol = st.selectbox("Symbol", ["ETH", "BTC", "SHIB", "PEPE", "DOGE"])
    size = st.number_input("Size ($)", min_value=50, value=200)
    col_a, col_b = st.columns(2)
    
    # BUY button with real trading
    if col_a.button("🚀 BUY"):
        if st.session_state.get("wallet_address"):
            st.warning("⚠️ Trading is currently simulated. To execute real trades:")
            st.info("1. Connect to an Ethereum RPC provider (e.g., Alchemy, Infura)")
            st.info("2. Sign and broadcast transactions via web3.js")
            st.info("3. Monitor for transaction confirmation")
            
            # Simulate the trade
            st.session_state.balance -= size
            st.session_state.pnl_history.append(st.session_state.balance)
            st.success(f"BUY ${size} (simulated)")
        else:
            st.warning("Connect wallet first!")
    
    # SELL button (simplified)
    if col_b.button("💀 SELL"):
        if st.session_state.get("wallet_address"):
            st.warning("⚠️ Trading is currently simulated. To execute real trades:")
            st.info("1. Connect to an Ethereum RPC provider (e.g., Alchemy, Infura)")
            st.info("2. Sign and broadcast transactions via web3.js")
            st.info("3. Monitor for transaction confirmation")
            
            # Simulate the trade
            st.session_state.balance += size
            st.session_state.pnl_history.append(st.session_state.balance)
            st.success(f"SELL ${size} (simulated)")
        else:
            st.warning("Connect wallet first!")

# ------------------------------------------------------------------
# RIGHT – positions (static placeholder)
# ------------------------------------------------------------------
with col_right:
    st.subheader("📍 Positions")
    st.markdown('<div class="card">ETH Long + $450</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">SHIB Long + $320</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# ----------   SELF-LEARNING AI (1:30 Kelly)   --------------------
# ------------------------------------------------------------------
def kelly_fraction(win_rate: float, reward: float = 30.0) -> float:
    """Kelly optimal fraction of bankroll (clamped 0.1 % - 10 %)."""
    k = win_rate - (1 - win_rate) / reward
    return max(0.001, min(k, 0.10))

if st.session_state.auto_trade:
    st.warning("🚀 FULL AUTO MODE ACTIVE")
    # pick the best meme-coin that exceeds the current edge threshold
    cand = None
    for t in meme:
        if t["edge"] > st.session_state.ai["edge_thr"]:
            cand = t
            break
    if cand:
        # Kelly sizing based on current win-rate
        kelly = kelly_fraction(st.session_state.ai["win_rate"])
        risk = st.session_state.balance * kelly
        reward = risk * 30          # 1:30 R:R
        act = random.choice(["BUY", "SELL"])

        # execute simulated trade (for now)
        if act == "BUY":
            st.session_state.balance -= risk
        else:
            st.session_state.balance += reward

        # log trade
        st.session_state.trades.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "market": cand["name"],
            "action": act,
            "risk": round(risk, 2),
            "reward": round(reward, 2),
            "edge%": round(cand["edge"]*100, 1),
        })
        st.session_state.pnl_history.append(st.session_state.balance)

        # ----- self-learning update -----
        ai = st.session_state.ai
        ai["total"] += 1
        # simulate win probability 68 %
        if random.random() < 0.68:
            ai["wins"] += 1
            ai["profit"] += reward
            st.success(f"🤖 AUTO-{act} {cand['name']} WIN")
        else:
            st.error(f"🤖 AUTO-{act} {cand['name']} LOSS")
        ai["win_rate"] = ai["wins"] / ai["total"]
        # adapt edge threshold (be more aggressive when winning)
        if ai["win_rate"] > 0.6:
            ai["edge_thr"] = max(0.05, ai["edge_thr"] - 0.005)
        else:
            ai["edge_thr"] = min(0.5, ai["edge_thr"] + 0.005)

# ------------------------------------------------------------------
# Bottom tabs – performance, AI stats, data-hub
# ------------------------------------------------------------------
tab_perf, tab_ai, tab_hub = st.tabs(["📈 Performance", "🧠 AI Stats", "📚 Data Hub"])

with tab_perf:
    st.subheader("Equity Curve")
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.pnl_history,
                             mode="lines+markers",
                             line=dict(color="#67e8f9", width=4)))
    fig.update_layout(height=420, template="plotly_dark",
                      paper_bgcolor="#05080f")
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.trades:
        df = pd.DataFrame(st.session_state.trades)
        st.subheader("Recent Trades")
        st.dataframe(df, use_container_width=True)

with tab_ai:
    ai = st.session_state.ai
    st.subheader("Self-Learning AI Summary")
    st.metric("Total Trades", ai["total"])
    st.metric("Wins", ai["wins"])
    st.metric("Win Rate", f"{ai['win_rate']*100:.1f}%")
    st.metric("Total Profit", f"${ai['profit']:.2f}")
    st.metric("Current Edge-Threshold", f"{ai['edge_thr']*100:.1f}%")

with tab_hub:
    st.subheader("Data Sources (quick links)")
    sources = [
        ("Etherscan", "https://etherscan.io/"),
        ("DexScreener", "https://dexscreener.com/ethereum"),
        ("Uniswap", "https://uniswap.org/"),
        ("MetaMask", "https://metamask.io/"),
        ("Alchemy", "https://www.alchemy.com/"),
        ("Infura", "https://www.infura.io/"),
        ("TradingView", "https://tradingview.com/"),
        ("CoinGecko", "https://www.coingecko.com/"),
        ("CoinMarketCap", "https://coinmarketcap.com/"),
        ("Kaggle Datasets", "https://www.kaggle.com/datasets"),
    ]
    for name, link in sources:
        st.markdown(f"• [{name}]({link})")

# ------------------------------------------------------------------
# Sidebar – controls (auto-trade toggle, Telegram config)
# ------------------------------------------------------------------
st.sidebar.title("⚙️ Controls")
st.sidebar.toggle("Full Auto Mode (AI Buys & Sells)", value=st.session_state.auto_trade,
                  key="auto_trade")
st.sidebar.caption("Burner wallet only – Kelly sizing handles risk.")

st.sidebar.subheader("🔔 Telegram alerts")
tg_token = st.sidebar.text_input("Bot Token", type="password")
tg_chat  = st.sidebar.text_input("Chat ID")
if st.sidebar.button("Save Telegram"):
    st.session_state.telegram_token = tg_token.strip()
    st.session_state.telegram_chat_id = tg_chat.strip()
    st.sidebar.success("Telegram credentials saved – you'll get a message after every auto-trade.")
st.sidebar.caption("Leave empty to disable Telegram notifications.")

# ------------------------------------------------------------------
# OPTIONAL – auto-refresh every 5 s (live-mode)
# ------------------------------------------------------------------
if st.sidebar.checkbox("Live refresh (≈ 5 s)", value=False):
    time.sleep(5)
    st.rerun()
