import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import math
import time

# --- 1. Page Config & Professional Styling ---
st.set_page_config(page_title="Munger Value Pro | Business Auditor", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a "Legal-Grade" Premium Look
st.markdown("""
    <style>
    .metric-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #1f77b4; }
    .footer { text-align: center; color: #888; padding: 20px; font-size: 0.8rem; }
    .stMetric { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 10px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. Sidebar: Control Center ---
with st.sidebar:
    st.header("🔍 Audit Center")
    ticker_input = st.text_input("Enter US Ticker (e.g., AAPL)", "").upper().strip()
    target_pe = st.slider("Target Margin of Safety P/E", 10.0, 40.0, 20.0, help="Munger typically looks for great businesses at a fair price.")
    
    st.markdown("---")
    st.subheader("🚀 Upgrade to Pro")
    st.write("Unlock unlimited deep-audits and professional PDF reports.")
    #  这里是 Gumroad 收银台链接
    st.link_button("Get Munger Value Pro", "https://futuristicmind.gumroad.com/l/paciw", type="primary")
    
    st.markdown("---")
    st.caption("Data powered by Yahoo Finance real-time API.")

# --- 3. High-Performance Data Fetching ---
@st.cache_data(ttl=3600)
def get_full_data(ticker):
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        hist = tk.history(period="10y")
        shares = tk.get_shares_full(start="2020-01-01") 
        return info, hist, shares
    except:
        return None, None, None

# --- 4. UI Rendering Logic ---
if not ticker_input:
    # 🌟 Landing Page: Welcome Guide
    st.title("📈 Munger Value Pro: Business Essence Audit Tool")
    st.info("👋 **Welcome, Investor. Let's perform a 'Legal-Grade' Business Audit.**")
    st.markdown("""
    ### Why use this tool?
    Charlie Munger believed that it’s hard for an investor to perform much better than the underlying business. We don't just track prices; we audit:
    - **Earnest Earnings**: Is there real cash flow backing the profits?
    - **Moat Thickness**: Does the gross margin indicate true pricing power?
    - **Management Restraint**: Are they burning cash or buying back shares to reward you?
    
    **Enter a ticker in the sidebar (e.g., COST, AAPL, MSFT) to start your audit.**
    """)
else:
    with st.spinner(f'Auditing financial evidence for {ticker_input}...'):
        info, hist, shares = get_full_data(ticker_input)
        
        if info and 'trailingPE' in info:
            name = info.get('longName', ticker_input)
            price = info.get('currentPrice', 0)
            pe = info.get('trailingPE')
            growth = info.get('earningsGrowth')
            
            # --- A. Valuation Dashboard ---
            st.subheader(f"⚖️ Audit Result: {name}")
            v1, v2, v3, v4 = st.columns(4)
            v1.metric("Current Price", f"${price:.2f}")
            v2.metric("Trailing P/E (TTM)", f"{pe:.2f}")
            v3.metric("Est. Earnings Growth", f"{growth*100:.1f}%" if growth else "N/A")
            v4.metric("Target P/E", f"{target_pe}")

            # --- B. Quality Audit Metrics ---
            st.markdown("---")
            st.subheader("🛡️ Business Essence: Core Audit Metrics")
            
            q1, q2, q3, q4 = st.columns(4)
            
            # 1. ROE
            roe = info.get('returnOnEquity', 0)
            q1.metric("ROE", f"{roe*100:.1f}%", help="Munger: Long-term returns tend to mirror ROE.")
            
            # 2. Gross Margin
            margin = info.get('grossMargins', 0)
            q2.metric("Gross Margin", f"{margin*100:.1f}%", help="Pricing power is the ultimate defense against inflation.")
            
            # 3. Cash Quality
            ocf = info.get('operatingCashflow', 0)
            ni = info.get('netIncomeToCommon', 1)
            fcf_quality = ocf / ni if ni else 0
            q3.metric("Cash Quality", f"{fcf_quality:.2f}", help=">1.0 means profits are backed by solid cash flow.")
            
            # 4. Capital Allocation
            share_trend = "Stable"
            if shares is not None and not shares.empty:
                if shares.iloc[-1] < shares.iloc[0]:
                    share_trend = "Buybacks ✅"
                elif shares.iloc[-1] > shares.iloc[0]:
                    share_trend = "Dilution ⚠️"
            q4.metric("Capital Allocation", share_trend, help="Share buybacks show management's commitment to shareholders.")

            # --- C. Final Verdict ---
            st.markdown("---")
            if growth is None or growth <= 0:
                st.error(f"🚫 **Audit Terminated**: Missing growth data for {ticker_input}.")
                st.info("💡 Munger Lesson: If a company isn't growing or is losing money, it’s not a 'Great Business'.")
            else:
                years = math.log(pe / target_pe) / math.log(1 + growth) if pe > target_pe else 0
                
                if pe <= target_pe:
                    st.success(f"🌟 **Verdict: Highly Attractive**. The stock is currently in the 'Buy Zone'.")
                elif years < 3:
                    st.success(f"✅ **Verdict: Strong**. Only **{years:.2f}** years to hit target valuation.")
                elif years < 7:
                    st.info(f"⚖️ **Verdict: Fair**. Requires **{years:.2f}** years to regress to target.")
                else:
                    st.warning(f"⚠️ **Verdict: Overheated**. Requires **{years:.2f}** years to regress. Wait for a better Margin of Safety.")

            # --- D. Growth Trajectory (Log Scale) ---
            if not hist.empty:
                st.subheader("📊 10-Year Growth Trajectory (Log Scale)")
                fig = go.Figure()
                y_data = hist['Close'] if isinstance(hist['Close'], pd.Series) else hist['Close'].iloc[:, 0]
                fig.add_trace(go.Scatter(x=hist.index, y=y_data, name='Price', line=dict(color='#1f77b4', width=2.5)))
                fig.update_layout(yaxis_type="log", template="plotly_white", height=500, margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
        else:
            st.error("🚫 Audit failed. Please check the ticker symbol and try again.")

# --- 5. Footer ---
st.markdown(f'<div class="footer">Munger Value Pro | 2026 Legal-Grade Auditor</div>', unsafe_allow_html=True)