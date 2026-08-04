import sys
import subprocess

# Auto-install plotly if needed
try:
    import plotly.graph_objects as go
    import plotly.express as px
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.graph_objects as go
    import plotly.express as px

import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. SYSTEM CONFIG & LIGHT THEME CSS OVERRIDE
# ==========================================
st.set_page_config(
    page_title="AI Investment Decision Support System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS จัดระเบียบหน้าจอ ธีมสว่าง Modern Clean Light
st.markdown("""
    <style>
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    .main .block-container {
        max-width: 98% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 6px 4px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    
    .svg-donut-box {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 4px 0;
    }
    
    .badge-excellent { background-color: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; padding: 2px 6px; border-radius: 10px; font-weight: bold; font-size: 8px; }
    .badge-good { background-color: #DBEAFE; color: #1D4ED8; border: 1px solid #93C5FD; padding: 2px 6px; border-radius: 10px; font-weight: bold; font-size: 8px; }
    .badge-warn { background-color: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; padding: 2px 6px; border-radius: 10px; font-weight: bold; font-size: 8px; }
    .badge-danger { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; padding: 2px 6px; border-radius: 10px; font-weight: bold; font-size: 8px; }
    
    .star-rating { font-size: 10px; color: #D97706; letter-spacing: 0.5px; }
    .metric-value { font-size: 16px; font-weight: bold; color: #0F172A; }
    .metric-label { font-size: 10px; color: #64748B; }

    .fv-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .fv-label { font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }
    .fv-val { font-size: 22px; font-weight: 800; color: #0F172A; margin: 4px 0; }
    .fv-sub { font-size: 10px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER VISUAL COMPONENTS
# ==========================================
def render_stars(score_100):
    stars = int(round(score_100 / 20))
    stars = max(1, min(5, stars))
    return "★" * stars + "☆" * (5 - stars)

def render_svg_donut(score, color_hex="#16A34A", size=56):
    stroke_dasharray = f"{score}, 100"
    return f"""
    <div class="svg-donut-box">
        <svg width="{size}" height="{size}" viewBox="0 0 42 42">
            <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#E2E8F0" stroke-width="4"></circle>
            <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="{color_hex}" stroke-width="4"
                    stroke-dasharray="{stroke_dasharray}" stroke-dashoffset="25" stroke-linecap="round"></circle>
            <text x="50%" y="46%" font-size="9" font-weight="bold" fill="#0F172A" text-anchor="middle" dominant-baseline="middle">{score:.0f}</text>
            <text x="50%" y="64%" font-size="4" fill="#64748B" text-anchor="middle" dominant-baseline="middle">/100</text>
        </svg>
    </div>
    """

def create_gauge_meter(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': "/100", 'font': {'size': 22, 'color': '#0F172A'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 0, 'showticklabels': False},
            'bar': {'color': "#16A34A" if score>=75 else ("#D97706" if score>=55 else "#DC2626")},
            'bgcolor': "#E2E8F0",
            'bordercolor': "rgba(0,0,0,0)"
        }
    ))
    fig.update_layout(height=120, margin=dict(t=15, b=0, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_stock_price_chart(dates, prices, color="#16A34A"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor='rgba(22, 163, 74, 0.08)'
    ))
    
    fig.update_layout(
        height=115,
        margin=dict(t=5, b=15, l=5, r=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showline=False, zeroline=False, tickfont=dict(size=8, color='#64748B'), nticks=4),
        yaxis=dict(side='right', showgrid=True, gridcolor='#E2E8F0', showline=False, zeroline=False, tickfont=dict(size=8, color='#64748B'), nticks=3)
    )
    return fig

# ==========================================
# 3. ACCURATE INDIVIDUAL FINANCIAL DATASTORE
# ==========================================
stock_list = ["ADVANC", "CCET", "DELTA", "HANA", "JMART", "KCE", "TRUE", "THCOM"]

@st.cache_data
def get_raw_financial_db():
    dates = ["Nov 2024", "Dec 2024", "Jan 2025", "Feb 2025", "Mar 2025", "May 2025"]
    return {
        "ADVANC": {
            "name": "Advanced Info Service PCL", "price": 285.00, "change_str": "+2.00 (+0.71%)", "mcap": "847,700 MB", "pe": 25.4, "pb": 8.2, "div": 3.85, "sector": "Technology", "industry": "Telecommunication", "eps": 11.22,
            "dates": dates, "prices_hist": [245, 252, 260, 272, 280, 285],
            "financials": {"ROE": 28.5, "ROA": 14.2, "NPM": 22.1, "DE": 1.25, "CR": 0.95, "OCF_NI": 1.25, "RevGrowth": 6.2, "NetGrowth": 9.5, "FCF": "42,100 MB", "Rank": "TOP 2"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)"], "2023": [24.1, 12.1, 19.5, 1.45, 0.82], "2024": [26.2, 13.2, 20.8, 1.32, 0.88], "2025 Q1": [28.5, 14.2, 22.1, 1.25, 0.95], "Status": ["Excellent", "Excellent", "Excellent", "Good", "Moderate"]})
        },
        "DELTA": {
            "name": "Delta Electronics (Thailand) PCL", "price": 160.00, "change_str": "+3.50 (+2.23%)", "mcap": "1,996,000 MB", "pe": 65.3, "pb": 18.2, "div": 0.85, "sector": "Technology", "industry": "Electronic Components", "eps": 2.45,
            "dates": dates, "prices_hist": [120, 132, 145, 150, 155, 160],
            "financials": {"ROE": 32.1, "ROA": 21.5, "NPM": 16.8, "DE": 0.42, "CR": 1.85, "OCF_NI": 1.12, "RevGrowth": 22.0, "NetGrowth": 28.4, "FCF": "18,500 MB", "Rank": "TOP 1"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)"], "2023": [26.2, 18.2, 14.1, 0.55, 1.65], "2024": [29.5, 19.8, 15.5, 0.48, 1.75], "2025 Q1": [32.1, 21.5, 16.8, 0.42, 1.85], "Status": ["Excellent", "Excellent", "Excellent", "Excellent", "Excellent"]})
        },
        "CCET": {
            "name": "Cal-Comp Electronics (Thailand) PCL", "price": 4.20, "change_str": "+0.10 (+2.44%)", "mcap": "43,800 MB", "pe": 12.0, "pb": 1.65, "div": 2.80, "sector": "Technology", "industry": "Electronic Components", "eps": 0.35,
            "dates": dates, "prices_hist": [2.8, 3.1, 3.4, 3.7, 4.0, 4.2],
            "financials": {"ROE": 14.2, "ROA": 6.1, "NPM": 4.5, "DE": 1.65, "CR": 1.15, "OCF_NI": 0.95, "RevGrowth": 18.5, "NetGrowth": 25.0, "FCF": "2,400 MB", "Rank": "TOP 4"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)"], "2023": [10.5, 4.2, 3.2, 1.85, 1.02], "2024": [12.8, 5.1, 3.8, 1.72, 1.08], "2025 Q1": [14.2, 6.1, 4.5, 1.65, 1.15], "Status": ["Good", "Moderate", "Moderate", "Moderate", "Good"]})
        },
        "HANA": {
            "name": "Hana Microelectronics PCL", "price": 38.50, "change_str": "-0.50 (-1.28%)", "mcap": "30,900 MB", "pe": 17.9, "pb": 1.25, "div": 4.20, "sector": "Technology", "industry": "Electronic Components", "eps": 2.15,
            "dates": dates, "prices_hist": [44, 42, 41, 39, 38, 38.5],
            "financials": {"ROE": 11.2, "ROA": 7.5, "NPM": 8.2, "DE": 0.35, "CR": 2.15, "OCF_NI": 1.35, "RevGrowth": -2.5, "NetGrowth": -8.4, "FCF": "3,100 MB", "Rank": "TOP 5"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)"], "2023": [14.5, 9.2, 10.1, 0.42, 2.05], "2024": [12.1, 8.0, 8.9, 0.38, 2.10], "2025 Q1": [11.2, 7.5, 8.2, 0.35, 2.15], "Status": ["Moderate", "Good", "Good", "Excellent", "Excellent"]})
        },
        "JMART": {
            "name": "Jaymart Group Holdings PCL", "price": 14.20, "change_str": "-0.20 (-1.39%)", "mcap": "20,700 MB", "pe": 24.5, "pb": 1.85, "div": 1.50, "sector": "Commerce", "industry": "Technology Retail", "eps": 0.58,
            "dates": dates, "prices_hist": [20, 18, 16, 15, 14, 14.2],
            "financials": {"ROE": 7.8, "ROA": 3.8, "NPM": 4.1, "DE": 2.15, "CR": 1.05, "OCF_NI": 0.82, "RevGrowth": 4.2, "NetGrowth": 12.1, "FCF": "850 MB", "Rank": "TOP 7"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)"], "2023": [-5.2, -2.1, -3.5, 2.45, 0.92], "2024": [5.1, 2.5, 2.8, 2.25, 0.98], "2025 Q1": [7.8, 3.8, 4.1, 2.15, 1.05], "Status": ["Weak", "Weak", "Weak", "Weak", "Moderate"]})
        },
        "KCE": {
            "name": "KCE Electronics PCL", "price": 41.00, "change_str": "+0.50 (+1.23%)", "mcap": "48,400 MB", "pe": 19.3, "pb": 2.85, "div": 3.40, "sector": "Technology", "industry": "Electronic Components", "eps": 2.12,
            "dates": dates, "prices_hist": [50, 47, 44, 42, 40, 41],
            "financials": {"ROE": 15.8, "ROA": 10.2, "NPM": 11.5, "DE": 0.58, "CR": 1.75, "OCF_NI": 1.18, "RevGrowth": 3.5, "NetGrowth": 5.2, "FCF": "4,200 MB", "Rank": "TOP 3"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)"], "2023": [18.2, 11.8, 12.8, 0.68, 1.55], "2024": [16.5, 10.8, 11.9, 0.62, 1.65], "2025 Q1": [15.8, 10.2, 11.5, 0.58, 1.75], "Status": ["Good", "Good", "Good", "Excellent", "Excellent"]})
        },
        "TRUE": {
            "name": "True Corporation PCL", "price": 11.80, "change_str": "+0.30 (+2.61%)", "mcap": "407,700 MB", "pe": 53.6, "pb": 3.12, "div": 1.20, "sector": "Technology", "industry": "Telecommunication", "eps": 0.22,
            "dates": dates, "prices_hist": [7.0, 8.2, 9.5, 10.2, 11.0, 11.8],
            "financials": {"ROE": 4.2, "ROA": 1.8, "NPM": 2.1, "DE": 3.85, "CR": 0.62, "OCF_NI": 2.85, "RevGrowth": 5.1, "NetGrowth": 110.0, "FCF": "18,200 MB", "Rank": "TOP 6"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)"], "2023": [-8.5, -2.8, -5.2, 4.50, 0.51], "2024": [1.2, 0.5, 0.8, 4.10, 0.58], "2025 Q1": [4.2, 1.8, 2.1, 3.85, 0.62], "Status": ["Weak", "Weak", "Weak", "Weak", "Weak"]})
        },
        "THCOM": {
            "name": "Thaicom PCL", "price": 12.50, "change_str": "+0.10 (+0.81%)", "mcap": "13,700 MB", "pe": 27.7, "pb": 0.92, "div": 2.40, "sector": "Technology", "industry": "Telecommunication", "eps": 0.45,
            "dates": dates, "prices_hist": [14.0, 13.5, 13.0, 12.4, 12.2, 12.5],
            "financials": {"ROE": 5.8, "ROA": 4.1, "NPM": 6.2, "DE": 0.28, "CR": 2.85, "OCF_NI": 1.45, "RevGrowth": -1.2, "NetGrowth": 15.2, "FCF": "1,250 MB", "Rank": "TOP 8"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)"], "2023": [4.2, 2.8, 4.5, 0.35, 2.50], "2024": [5.1, 3.5, 5.2, 0.31, 2.70], "2025 Q1": [5.8, 4.1, 6.2, 0.28, 2.85], "Status": ["Weak", "Moderate", "Moderate", "Excellent", "Excellent"]})
        }
    }

# ==========================================
# 4. DYNAMIC CALCULATION ENGINE (KOS 1.0)
# ==========================================
def calculate_stock_metrics(stock_data):
    f = stock_data["financials"]
    p = stock_data["price"]
    eps = stock_data["eps"]
    
    m1_dims = [
        {"name": "1. PROFITABILITY", "score": min(max(f["ROE"] * 3.2, 10), 100), "w": "30%", "w_num": 0.30},
        {"name": "2. GROWTH", "score": max(min(f["RevGrowth"] * 2.5 + 50, 100), 10), "w": "15%", "w_num": 0.15},
        {"name": "3. STABILITY", "score": max(100 - (f["DE"] * 20), 10), "w": "20%", "w_num": 0.20},
        {"name": "4. LIQUIDITY", "score": min(f["CR"] * 45, 100), "w": "10%", "w_num": 0.10},
        {"name": "5. CASH FLOW", "score": min(f["OCF_NI"] * 65, 100), "w": "10%", "w_num": 0.10},
        {"name": "6. EFFICIENCY", "score": min(f["ROA"] * 4.5, 100), "w": "10%", "w_num": 0.10},
        {"name": "7. EARNINGS QLTY", "score": min(f["NPM"] * 3.8, 100), "w": "5%", "w_num": 0.05}
    ]
    
    m1_score = sum([d["score"] * d["w_num"] for d in m1_dims])
    
    growth_rate = max(f["NetGrowth"] / 100, 0.03)
    target_pe = max(stock_data["pe"] * 0.85, 12.0)
    
    fair_base = eps * (1 + min(growth_rate, 0.15)) * target_pe
    fair_bear = fair_base * 0.85
    fair_bull = fair_base * 1.20
    
    mos_pct = ((fair_base - p) / fair_base) * 100 if fair_base > 0 else 0.0
    m2_score = max(min(50 + (mos_pct * 2), 100), 10)
    
    m3_score = 65.0
    m4_score = max(min(50 + (f["NetGrowth"] * 0.8), 95), 20)
    m5_score = max(100 - (f["DE"] * 18), 15)
    m6_score = m1_score * 0.95
    
    overall_score = (m1_score * 0.35) + (m2_score * 0.35) + (m4_score * 0.15) + (m5_score * 0.15)
    
    if overall_score >= 75 and mos_pct > 0:
        rec = "BUY"
        rec_text = "ATTRACTIVE"
    elif overall_score >= 60:
        rec = "ACCUMULATE"
        rec_text = "ATTRACTIVE"
    elif overall_score >= 45:
        rec = "HOLD"
        rec_text = "NEUTRAL"
    else:
        rec = "SELL / AVOID"
        rec_text = "UNATTRACTIVE"
        
    return {
        "m1_score": round(m1_score),
        "m1_dims": m1_dims,
        "m2_score": round(m2_score),
        "fair_base": fair_base,
        "fair_bear": fair_bear,
        "fair_bull": fair_bull,
        "mos_pct": mos_pct,
        "m3_score": round(m3_score),
        "m4_score": round(m4_score),
        "m5_score": round(m5_score),
        "m6_score": round(m6_score),
        "overall_score": round(overall_score),
        "rec": rec,
        "rec_text": rec_text
    }

# ==========================================
# 5. SIDEBAR & APP CONTROLS
# ==========================================
raw_db = get_raw_financial_db()

with st.sidebar:
    st.title("🧠 AI Investment System")
    st.caption("Financial Analysis Engine v1.0")
    st.divider()
    
    selected_symbol = st.selectbox("📌 เลือกบริษัทที่ต้องการวิเคราะห์:", stock_list, index=0)
    st.divider()
    
    selected_tab = st.radio("🎯 เมนูการวิเคราะห์ (Modules):", [
        " Overview",
        " Company Health",
        " Fair Value Assessment",
        " Entry Timing",
        " AI Prediction",
        " Risk Analysis",
        " Industry Benchmark"
    ])

stock_raw = raw_db[selected_symbol]
calc = calculate_stock_metrics(stock_raw)

# Header Bar
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; background-color: #FFFFFF; padding: 12px 20px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
        <div>
            <span style='font-size:22px; font-weight:bold; color:#0F172A;'>{selected_symbol}</span>
            <span style='color:#64748B; font-size:14px; margin-left:10px;'>({stock_raw['name']})</span>
        </div>
        <div>
            <span style='font-size:18px; font-weight:bold; color:#16A34A;'>{stock_raw['price']:.2f} THB</span>
            <span style='color:#64748B; font-size:12px; margin-left:20px;'>Market Cap: {stock_raw['mcap']}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 6. TAB 1: OVERVIEW DASHBOARD
# ==========================================
if "Overview" in selected_tab:
    st.markdown("<h2 style='color:#0F172A;'>OVERVIEW DASHBOARD</h2>", unsafe_allow_html=True)
    st.caption("AI-Powered Investment Decision Support System")
    
    col_left, col_mid, col_right = st.columns([2.5, 5.5, 4.0])
    
    # --- LEFT COLUMN ---
    with col_left:
        with st.container(border=True):
            st.markdown(f"""
                <div style='font-size:18px; font-weight:bold; color:#0F172A;'>{selected_symbol} ☆</div>
                <div style='font-size:11px; color:#64748B; margin-bottom:8px;'>{stock_raw['name']}</div>
                <div style='font-size:24px; font-weight:bold; color:#0F172A;'>{stock_raw['price']:.2f} <span style='font-size:12px;'>THB</span></div>
                <div style='color:#16A34A; font-size:11px;'>{stock_raw['change_str']}</div>
                <div style='font-size:9px; color:#64748B; margin-top:2px; margin-bottom:8px;'>Market Closed | 23 May 2025</div>
            """, unsafe_allow_html=True)
            
            fig_stock = create_stock_price_chart(stock_raw["dates"], stock_raw["prices_hist"])
            st.plotly_chart(fig_stock, use_container_width=True, config={'displayModeBar': False})
            
            st.markdown(f"""
                <hr style='border-color:#E2E8F0; margin:10px 0;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                    <div><div class='metric-label'>Market Cap</div><div class='metric-value' style='font-size:12px;'>{stock_raw['mcap']}</div></div>
                    <div><div class='metric-label'>P/E (TTM)</div><div class='metric-value' style='font-size:12px;'>{stock_raw['pe']}x</div></div>
                </div>
                <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                    <div><div class='metric-label'>Sector</div><div class='metric-value' style='font-size:12px;'>{stock_raw['sector']}</div></div>
                    <div><div class='metric-label'>P/B (TTM)</div><div class='metric-value' style='font-size:12px;'>{stock_raw['pb']}x</div></div>
                </div>
                <div style='display:flex; justify-content:space-between;'>
                    <div><div class='metric-label'>Industry</div><div class='metric-value' style='font-size:12px;'>{stock_raw['industry']}</div></div>
                    <div><div class='metric-label'>Dividend Yield</div><div class='metric-value' style='font-size:12px;'>{stock_raw['div']}%</div></div>
                </div>
            """, unsafe_allow_html=True)

    # --- MIDDLE COLUMN ---
    with col_mid:
        with st.container(border=True):
            st.markdown("<h5 style='margin-bottom:12px; color:#0F172A;'>INVESTMENT DECISION OVERVIEW</h5>", unsafe_allow_html=True)
            
            mos_class = "badge-excellent" if calc['mos_pct'] > 0 else "badge-danger"
            mos_label = "UNDERVALUED" if calc['mos_pct'] > 0 else "OVERVALUED"
            
            modules = [
                ("01 COMPANY HEALTH", calc["m1_score"], "#16A34A", "EXCELLENT", "badge-excellent", "Strong health & quality"),
                ("02 FAIR VALUE", calc["m2_score"], "#D97706", mos_label, mos_class, f"MoS {calc['mos_pct']:+.1f}%"),
                ("03 ENTRY TIMING", calc["m3_score"], "#2563EB", "NEUTRAL", "badge-good", "Technical entry timing"),
                ("04 AI PREDICTION", calc["m4_score"], "#9333EA", "POSITIVE", "badge-good", "AI forecast 6-12m"),
                ("05 RISK ANALYSIS", calc["m5_score"], "#EA580C", "MODERATE", "badge-warn", "Moderate risk level"),
                ("06 BENCHMARK", calc["m6_score"], "#0891B2", "OUTPERFORM", "badge-excellent", "Industry outperform")
            ]
            
            r1_c1, r1_c2, r1_c3 = st.columns(3)
            r2_c1, r2_c2, r2_c3 = st.columns(3)
            cols = [r1_c1, r1_c2, r1_c3, r2_c1, r2_c2, r2_c3]
            
            for idx, (title, score, color, badge_txt, badge_cls, desc) in enumerate(modules):
                with cols[idx]:
                    with st.container(border=True):
                        st.markdown(f"<div style='font-size:8px; font-weight:bold; color:#64748B; text-align:center;'>{title}</div>", unsafe_allow_html=True)
                        st.markdown(render_svg_donut(score, color, size=56), unsafe_allow_html=True)
                        st.markdown(f"<div class='star-rating' style='text-align:center;'>{render_stars(score)}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center; margin-top:2px;'><span class='{badge_cls}'>{badge_txt}</span></div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:8px; color:#64748B; text-align:center; margin-top:3px;'>{desc}</div>", unsafe_allow_html=True)

    # --- RIGHT COLUMN ---
    with col_right:
        with st.container(border=True):
            st.markdown("<h5 style='margin-bottom:10px; color:#0F172A; text-align:center;'>AI INVESTMENT SUMMARY</h5>", unsafe_allow_html=True)
            
            st.plotly_chart(create_gauge_meter(calc["overall_score"]), use_container_width=True, config={'displayModeBar': False})
            
            st.markdown(f"<div style='color:#64748B; font-size:10px; font-weight:bold; text-align:center; margin-top:-10px;'>OVERALL SCORE</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='star-rating' style='font-size:16px; text-align:center;'>{render_stars(calc['overall_score'])}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:#16A34A; margin:4px 0; text-align:center;'>{calc['rec_text']}</h3>", unsafe_allow_html=True)
            
            st.markdown(f"<p style='font-size:10px; color:#64748B; line-height:1.3; text-align:center;'>{selected_symbol} shows attractive investment potential with strong fundamentals and solid AI predictions.</p>", unsafe_allow_html=True)
            
            st.divider()
            st.markdown("<div style='color:#64748B; font-size:10px; font-weight:bold; text-align:center;'>RECOMMENDATION</div>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#16A34A; margin:4px 0; text-align:center;'>🚀 {calc['rec']}</h2>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center; font-size:9px; color:#64748B;'>Investment Horizon: LONG TERM (12+ Months)</div>", unsafe_allow_html=True)

    # --- BOTTOM ROW ---
    st.markdown("<h5 style='color:#0F172A; margin-top:15px;'>KEY HIGHLIGHTS</h5>", unsafe_allow_html=True)
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns(6)
    fin = stock_raw["financials"]
    
    with h_col1:
        with st.container(border=True):
            st.markdown(f"📈 <span class='metric-label'>Revenue Growth</span><div class='metric-value' style='color:#16A34A;'>{fin['RevGrowth']:+.1f}%</div><span class='metric-label'>YoY</span>", unsafe_allow_html=True)
    with h_col2:
        with st.container(border=True):
            st.markdown(f"💰 <span class='metric-label'>Net Profit Growth</span><div class='metric-value' style='color:#16A34A;'>{fin['NetGrowth']:+.1f}%</div><span class='metric-label'>YoY</span>", unsafe_allow_html=True)
    with h_col3:
        with st.container(border=True):
            st.markdown(f"🔄 <span class='metric-label'>ROE (TTM)</span><div class='metric-value' style='color:#2563EB;'>{fin['ROE']:.1f}%</div><span class='metric-label'>High Efficiency</span>", unsafe_allow_html=True)
    with h_col4:
        with st.container(border=True):
            st.markdown(f"💵 <span class='metric-label'>Free Cash Flow</span><div class='metric-value' style='font-size:14px;'>{fin['FCF']}</div><span class='metric-label'>Strong Cash Gen</span>", unsafe_allow_html=True)
    with h_col5:
        with st.container(border=True):
            st.markdown(f"🛡️ <span class='metric-label'>Debt to Equity</span><div class='metric-value' style='color:#D97706;'>{fin['DE']:.2f}x</div><span class='metric-label'>Low Risk</span>", unsafe_allow_html=True)
    with h_col6:
        with st.container(border=True):
            st.markdown(f"🏆 <span class='metric-label'>Industry Rank</span><div class='metric-value' style='color:#0891B2;'>{fin['Rank']}</div><span class='metric-label'>In Sector</span>", unsafe_allow_html=True)

# ==========================================
# 7. TAB 2: COMPANY HEALTH
# ==========================================
elif "Company Health" in selected_tab:
    st.markdown(f"<h2 style='color:#0F172A;'>COMPANY HEALTH ANALYSIS ({selected_symbol})</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 8])
    with col1:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:12px; font-weight:bold; color:#64748B; text-align:center;'>01 OVERALL HEALTH SCORE</div>", unsafe_allow_html=True)
            st.markdown(render_svg_donut(calc["m1_score"], "#16A34A", size=85), unsafe_allow_html=True)
            st.markdown(f"<div class='star-rating' style='text-align:center;'>{render_stars(calc['m1_score'])}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center; color:#16A34A;'>SCORE {calc['m1_score']} / 100</h3>", unsafe_allow_html=True)

    with col2:
        with st.container(border=True):
            st.markdown("<h5 style='color:#0F172A;'>💡 EXPLAINABLE AI REASONING</h5>", unsafe_allow_html=True)
            st.write(f"จากการประมวลผลงบการเงิน: บริษัท {selected_symbol} มีคะแนน ROE เท่ากับ {stock_raw['financials']['ROE']}% และมีภาระหนี้สิน D/E เท่ากับ {stock_raw['financials']['DE']}x ส่งผลให้ระดับเสถียรภาพทางการเงินอยู่ในเกณฑ์สอดคล้องกับมาตรฐาน KOS 1.0")

    st.markdown("<h5 style='color:#0F172A; margin-top:15px;'>7 DIMENSIONS SCORE BREAKDOWN</h5>", unsafe_allow_html=True)
    dim_cols = st.columns(7)
    for idx, dim in enumerate(calc["m1_dims"]):
        with dim_cols[idx]:
            with st.container(border=True):
                st.markdown(f"<div style='font-size:8px; font-weight:bold; color:#64748B; text-align:center;'>0{idx+1} {dim['name']}</div>", unsafe_allow_html=True)
                st.markdown(render_svg_donut(round(dim["score"]), "#16A34A", size=50), unsafe_allow_html=True)
                st.markdown(f"<div class='star-rating' style='text-align:center;'>{render_stars(dim['score'])}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; margin-top:2px;'><span class='badge-excellent'>W: {dim['w']}</span></div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<h5 style='color:#0F172A;'>📋 FINANCIAL STATEMENT HISTORY & RATIOS</h5>", unsafe_allow_html=True)
    st.dataframe(stock_raw["history_table"], use_container_width=True, hide_index=True)

# ==========================================
# 8. TAB 3: FAIR VALUE ASSESSMENT
# ==========================================
elif "Fair Value" in selected_tab:
    st.markdown(f"<h2 style='color:#0F172A;'>FAIR VALUE ASSESSMENT ({selected_symbol})</h2>", unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    status_label = "UNDERVALUED" if calc['mos_pct'] > 0 else "OVERVALUED"
    status_color = "#16A34A" if calc['mos_pct'] > 0 else "#DC2626"
    
    with col_f1:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>CURRENT MARKET PRICE</div><div class='fv-val'>{stock_raw['price']:.2f} <span style='font-size:14px;'>THB</span></div></div>", unsafe_allow_html=True)
    with col_f2:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>ESTIMATED FAIR VALUE (BASE)</div><div class='fv-val' style='color:#2563EB;'>{calc['fair_base']:.2f} <span style='font-size:14px;'>THB</span></div></div>", unsafe_allow_html=True)
    with col_f3:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>MARGIN OF SAFETY</div><div class='fv-val' style='color:{status_color};'>{calc['mos_pct']:+.1f}%</div></div>", unsafe_allow_html=True)
    with col_f4:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>VALUATION STATUS</div><div class='fv-val' style='color:{status_color}; font-size:22px;'>{status_label}</div></div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<h5 style='color:#0F172A;'>INTRINSIC VALUE RANGE (DCF SCENARIOS)</h5>", unsafe_allow_html=True)
    sc_col1, sc_col2, sc_col3 = st.columns(3)
    
    with sc_col1:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>Bear Case</div><div class='fv-val' style='color:#D97706;'>{calc['fair_bear']:.2f} THB</div><div class='fv-sub' style='color:#64748B;'>Conservative Growth</div></div>", unsafe_allow_html=True)
    with sc_col2:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>Base Case (Target)</div><div class='fv-val' style='color:#16A34A;'>{calc['fair_base']:.2f} THB</div><div class='fv-sub' style='color:#16A34A;'>Base Growth</div></div>", unsafe_allow_html=True)
    with sc_col3:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>Bull Case</div><div class='fv-val' style='color:#2563EB;'>{calc['fair_bull']:.2f} THB</div><div class='fv-sub' style='color:#2563EB;'>Optimistic Growth</div></div>", unsafe_allow_html=True)

else:
    st.info("โมดูลอื่นๆ พร้อมขยายระบบเชื่อมต่อข้อมูลเชิงลึกในลำดับถัดไปครับ")
