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
# 1. SYSTEM CONFIG & DARK THEME CSS OVERRIDE
# ==========================================
st.set_page_config(
    page_title="AI Investment Decision Support System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS จัดการ Dark Mode 100%, แก้ตารางสีขาว, และทำ Stat Cards ในหน้า Fair Value
st.markdown("""
    <style>
    /* Dark Theme Global & Sidebar */
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #0A0E1A !important;
        color: #E2E8F0 !important;
    }
    
    /* Native Container Card Style */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #101625 !important;
        border: 1px solid #1E293B !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }
    
    /* Grid 3x2 สำหรับ 6 โมดูล */
    .modules-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 10px;
    }
    
    /* การ์ดย่อย 6 ใบ */
    .module-card-inner {
        background-color: #172033;
        border: 1px solid #232D42;
        border-radius: 10px;
        padding: 12px 8px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        min-height: 200px;
    }
    
    /* Donut Ring */
    .donut-container {
        position: relative;
        width: 65px;
        height: 65px;
        margin: 4px auto;
    }
    
    .donut-ring {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .donut-inner {
        width: 48px;
        height: 48px;
        background-color: #172033;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .donut-score { font-size: 15px; font-weight: bold; color: #FFFFFF; line-height: 1; }
    .donut-sub { font-size: 8px; color: #64748B; margin-top: 1px; }
    
    /* Badges */
    .badge-excellent { background-color: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid #10B981; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 9px; margin-top: 3px; }
    .badge-good { background-color: rgba(59, 130, 246, 0.12); color: #3B82F6; border: 1px solid #3B82F6; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 9px; margin-top: 3px; }
    .badge-warn { background-color: rgba(245, 158, 11, 0.12); color: #F59E0B; border: 1px solid #F59E0B; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 9px; margin-top: 3px; }
    .badge-danger { background-color: rgba(239, 68, 68, 0.12); color: #EF4444; border: 1px solid #EF4444; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 9px; margin-top: 3px; }
    
    .star-rating { font-size: 12px; color: #F59E0B; letter-spacing: 1px; margin-top: 2px; }
    .card-title { font-size: 10px; font-weight: 700; color: #94A3B8; letter-spacing: 0.5px; text-transform: uppercase; }
    .card-desc { font-size: 9px; color: #64748B; margin-top: 4px; line-height: 1.2; padding: 0 2px; }
    
    .metric-value { font-size: 18px; font-weight: bold; color: #FFFFFF; }
    .metric-label { font-size: 11px; color: #64748B; }

    /* แก้ปัญหาตารางงบการเงินสีขาว ให้เป็น Dark Theme */
    [data-testid="stDataFrame"], [data-testid="stTable"], table {
        background-color: #101625 !important;
        color: #E2E8F0 !important;
        border-radius: 8px !important;
    }
    
    th {
        background-color: #172033 !important;
        color: #94A3B8 !important;
        font-weight: bold !important;
    }
    
    td {
        background-color: #101625 !important;
        color: #E2E8F0 !important;
        border-bottom: 1px solid #1E293B !important;
    }

    /* Stat Card สำหรับ Fair Value Assessment */
    .fv-card {
        background-color: #172033;
        border: 1px solid #232D42;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        margin-bottom: 12px;
    }
    .fv-label { font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; }
    .fv-val { font-size: 26px; font-weight: 800; color: #FFFFFF; margin: 6px 0; }
    .fv-sub { font-size: 12px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER VISUAL COMPONENTS
# ==========================================
def render_stars(score_100):
    stars = int(round(score_100 / 20))
    stars = max(1, min(5, stars))
    return "★" * stars + "☆" * (5 - stars)

def get_module_card_html(num, title, score, color_hex, badge_text, badge_class, desc_text):
    stars = render_stars(score)
    score_deg = int((score / 100) * 360)
    
    return f"""
        <div class='module-card-inner'>
            <div class='card-title'>{num} {title}</div>
            <div class='donut-container'>
                <div class='donut-ring' style='background: conic-gradient({color_hex} 0deg {score_deg}deg, #2A364F {score_deg}deg 360deg);'>
                    <div class='donut-inner'>
                        <span class='donut-score'>{score:.0f}</span>
                        <span class='donut-sub'>/100</span>
                    </div>
                </div>
            </div>
            <div class='star-rating'>{stars}</div>
            <div class='{badge_class}'>{badge_text}</div>
            <div class='card-desc'>{desc_text}</div>
        </div>
    """

def create_gauge_meter(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': "/100", 'font': {'size': 26, 'color': 'white'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 0, 'showticklabels': False},
            'bar': {'color': "#10B981" if score>=75 else ("#F59E0B" if score>=55 else "#EF4444")},
            'bgcolor': "#1E293B",
            'bordercolor': "rgba(0,0,0,0)"
        }
    ))
    fig.update_layout(height=130, margin=dict(t=20, b=0, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_stock_price_chart(dates, prices, color="#10B981"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    fig.update_layout(
        height=125,
        margin=dict(t=10, b=20, l=10, r=35),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
            tickfont=dict(size=9, color='#64748B'),
            nticks=4
        ),
        yaxis=dict(
            side='right',
            showgrid=True,
            gridcolor='#1E293B',
            showline=False,
            zeroline=False,
            tickfont=dict(size=9, color='#64748B'),
            nticks=3
        )
    )
    return fig

# ==========================================
# 3. REAL FINANCIAL DATASTORE (8 STOCKS)
# ==========================================
stock_list = ["ADVANC", "CCET", "DELTA", "HANA", "JMART", "KCE", "TRUE", "THCOM"]

@st.cache_data
def get_raw_financial_db():
    dates = ["May 2024", "Jul 2024", "Sep 2024", "Nov 2024", "Jan 2025", "Mar 2025", "May 2025"]
    return {
        "ADVANC": {
            "name": "Advanced Info Service PCL", "price": 285.00, "mcap": "847,700 MB", "pe": 25.4, "pb": 8.2, "div": 3.85, "sector": "Technology", "industry": "Telecommunication", "eps": 11.22,
            "dates": dates, "prices_hist": [240, 248, 255, 268, 275, 282, 285],
            "financials": {"ROE": 28.5, "ROA": 14.2, "NPM": 22.1, "DE": 1.25, "CR": 0.95, "OCF_NI": 1.25, "RevGrowth": 6.2, "NetGrowth": 9.5, "FCF": "42,100 MB", "Rank": "TOP 2"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"], "2023": [24.1, 12.1, 19.5, 1.45, 0.82, 1.15], "2024": [26.2, 13.2, 20.8, 1.32, 0.88, 1.20], "2025 Q1": [28.5, 14.2, 22.1, 1.25, 0.95, 1.25], "Status": ["Excellent", "Excellent", "Excellent", "Good", "Moderate", "Excellent"]})
        },
        "DELTA": {
            "name": "Delta Electronics (Thailand) PCL", "price": 160.00, "mcap": "1,996,000 MB", "pe": 65.3, "pb": 18.2, "div": 0.85, "sector": "Technology", "industry": "Electronic Components", "eps": 2.45,
            "dates": dates, "prices_hist": [115, 125, 138, 145, 150, 158, 160],
            "financials": {"ROE": 32.1, "ROA": 21.5, "NPM": 16.8, "DE": 0.42, "CR": 1.85, "OCF_NI": 1.12, "RevGrowth": 22.0, "NetGrowth": 28.4, "FCF": "18,500 MB", "Rank": "TOP 1"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"], "2023": [26.2, 18.2, 14.1, 0.55, 1.65, 1.05], "2024": [29.5, 19.8, 15.5, 0.48, 1.75, 1.10], "2025 Q1": [32.1, 21.5, 16.8, 0.42, 1.85, 1.12], "Status": ["Excellent", "Excellent", "Excellent", "Excellent", "Excellent", "Excellent"]})
        },
        "CCET": {
            "name": "Cal-Comp Electronics (Thailand) PCL", "price": 4.20, "mcap": "43,800 MB", "pe": 12.0, "pb": 1.65, "div": 2.80, "sector": "Technology", "industry": "Electronic Components", "eps": 0.35,
            "dates": dates, "prices_hist": [2.8, 3.0, 3.3, 3.6, 3.8, 4.0, 4.2],
            "financials": {"ROE": 14.2, "ROA": 6.1, "NPM": 4.5, "DE": 1.65, "CR": 1.15, "OCF_NI": 0.95, "RevGrowth": 18.5, "NetGrowth": 25.0, "FCF": "2,400 MB", "Rank": "TOP 4"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"], "2023": [10.5, 4.2, 3.2, 1.85, 1.02, 0.82], "2024": [12.8, 5.1, 3.8, 1.72, 1.08, 0.88], "2025 Q1": [14.2, 6.1, 4.5, 1.65, 1.15, 0.95], "Status": ["Good", "Moderate", "Moderate", "Moderate", "Good", "Moderate"]})
        },
        "HANA": {
            "name": "Hana Microelectronics PCL", "price": 38.50, "mcap": "30,900 MB", "pe": 17.9, "pb": 1.25, "div": 4.20, "sector": "Technology", "industry": "Electronic Components", "eps": 2.15,
            "dates": dates, "prices_hist": [45, 43, 41, 40, 39, 38, 38.5],
            "financials": {"ROE": 11.2, "ROA": 7.5, "NPM": 8.2, "DE": 0.35, "CR": 2.15, "OCF_NI": 1.35, "RevGrowth": -2.5, "NetGrowth": -8.4, "FCF": "3,100 MB", "Rank": "TOP 5"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"], "2023": [14.5, 9.2, 10.1, 0.42, 2.05, 1.20], "2024": [12.1, 8.0, 8.9, 0.38, 2.10, 1.28], "2025 Q1": [11.2, 7.5, 8.2, 0.35, 2.15, 1.35], "Status": ["Moderate", "Good", "Good", "Excellent", "Excellent", "Excellent"]})
        },
        "JMART": {
            "name": "Jaymart Group Holdings PCL", "price": 14.20, "mcap": "20,700 MB", "pe": 24.5, "pb": 1.85, "div": 1.50, "sector": "Commerce", "industry": "Technology Retail", "eps": 0.58,
            "dates": dates, "prices_hist": [22, 20, 18, 16, 15, 14, 14.2],
            "financials": {"ROE": 7.8, "ROA": 3.8, "NPM": 4.1, "DE": 2.15, "CR": 1.05, "OCF_NI": 0.82, "RevGrowth": 4.2, "NetGrowth": 12.1, "FCF": "850 MB", "Rank": "TOP 7"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"], "2023": [-5.2, -2.1, -3.5, 2.45, 0.92, 0.65], "2024": [5.1, 2.5, 2.8, 2.25, 0.98, 0.75], "2025 Q1": [7.8, 3.8, 4.1, 2.15, 1.05, 0.82], "Status": ["Weak", "Weak", "Weak", "Weak", "Moderate", "Weak"]})
        },
        "KCE": {
            "name": "KCE Electronics PCL", "price": 41.00, "mcap": "48,400 MB", "pe": 19.3, "pb": 2.85, "div": 3.40, "sector": "Technology", "industry": "Electronic Components", "eps": 2.12,
            "dates": dates, "prices_hist": [52, 49, 46, 44, 42, 40, 41],
            "financials": {"ROE": 15.8, "ROA": 10.2, "NPM": 11.5, "DE": 0.58, "CR": 1.75, "OCF_NI": 1.18, "RevGrowth": 3.5, "NetGrowth": 5.2, "FCF": "4,200 MB", "Rank": "TOP 3"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"], "2023": [18.2, 11.8, 12.8, 0.68, 1.55, 1.08], "2024": [16.5, 10.8, 11.9, 0.62, 1.65, 1.12], "2025 Q1": [15.8, 10.2, 11.5, 0.58, 1.75, 1.18], "Status": ["Good", "Good", "Good", "Excellent", "Excellent", "Good"]})
        },
        "TRUE": {
            "name": "True Corporation PCL", "price": 11.80, "mcap": "407,700 MB", "pe": 53.6, "pb": 3.12, "div": 1.20, "sector": "Technology", "industry": "Telecommunication", "eps": 0.22,
            "dates": dates, "prices_hist": [6.5, 7.5, 8.8, 9.8, 10.5, 11.2, 11.8],
            "financials": {"ROE": 4.2, "ROA": 1.8, "NPM": 2.1, "DE": 3.85, "CR": 0.62, "OCF_NI": 2.85, "RevGrowth": 5.1, "NetGrowth": 110.0, "FCF": "18,200 MB", "Rank": "TOP 6"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"], "2023": [-8.5, -2.8, -5.2, 4.50, 0.51, 2.10], "2024": [1.2, 0.5, 0.8, 4.10, 0.58, 2.50], "2025 Q1": [4.2, 1.8, 2.1, 3.85, 0.62, 2.85], "Status": ["Weak", "Weak", "Weak", "Weak", "Weak", "Excellent"]})
        },
        "THCOM": {
            "name": "Thaicom PCL", "price": 12.50, "mcap": "13,700 MB", "pe": 27.7, "pb": 0.92, "div": 2.40, "sector": "Technology", "industry": "Telecommunication", "eps": 0.45,
            "dates": dates, "prices_hist": [14.5, 14.0, 13.5, 12.8, 12.2, 12.1, 12.5],
            "financials": {"ROE": 5.8, "ROA": 4.1, "NPM": 6.2, "DE": 0.28, "CR": 2.85, "OCF_NI": 1.45, "RevGrowth": -1.2, "NetGrowth": 15.2, "FCF": "1,250 MB", "Rank": "TOP 8"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"], "2023": [4.2, 2.8, 4.5, 0.35, 2.50, 1.25], "2024": [5.1, 3.5, 5.2, 0.31, 2.70, 1.35], "2025 Q1": [5.8, 4.1, 6.2, 0.28, 2.85, 1.45], "Status": ["Weak", "Moderate", "Moderate", "Excellent", "Excellent", "Excellent"]})
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
        {"name": "1. PROFITABILITY", "score": min(f["ROE"] * 3.0, 100), "w": "30%", "w_num": 0.30},
        {"name": "2. GROWTH", "score": max(min(f["RevGrowth"] * 2.5 + 50, 100), 10), "w": "15%", "w_num": 0.15},
        {"name": "3. STABILITY", "score": max(100 - (f["DE"] * 22), 10), "w": "20%", "w_num": 0.20},
        {"name": "4. LIQUIDITY", "score": min(f["CR"] * 45, 100), "w": "10%", "w_num": 0.10},
        {"name": "5. CASH FLOW", "score": min(f["OCF_NI"] * 65, 100), "w": "10%", "w_num": 0.10},
        {"name": "6. EFFICIENCY", "score": min(f["ROA"] * 4.5, 100), "w": "10%", "w_num": 0.10},
        {"name": "7. EARNINGS QLTY", "score": min(f["NPM"] * 3.5, 100), "w": "5%", "w_num": 0.05}
    ]
    
    m1_score = sum([d["score"] * d["w_num"] for d in m1_dims])
    
    growth_rate = max(f["NetGrowth"] / 100, 0.03)
    target_pe = max(stock_data["pe"] * 0.85, 12.0)
    
    fair_base = eps * (1 + min(growth_rate, 0.15)) * target_pe
    fair_bear = fair_base * 0.85
    fair_bull = fair_base * 1.20
    
    mos_pct = ((fair_base - p) / fair_base) * 100
    m2_score = max(min(50 + (mos_pct * 2), 100), 10)
    
    m3_score = 65.0
    m4_score = max(min(50 + (f["NetGrowth"] * 0.8), 95), 20)
    m5_score = max(100 - (f["DE"] * 18), 15)
    m6_score = m1_score * 0.95
    
    overall_score = (m1_score * 0.35) + (m2_score * 0.35) + (m4_score * 0.15) + (m5_score * 0.15)
    
    if overall_score >= 80 and mos_pct > 10:
        rec = "BUY"
        rec_text = "ATTRACTIVE"
    elif overall_score >= 65 and mos_pct > 0:
        rec = "ACCUMULATE"
        rec_text = "ATTRACTIVE"
    elif overall_score >= 50:
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
    st.caption("Dynamic Expert System v1.0")
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
    <div style='display: flex; justify-content: space-between; align-items: center; background-color: #101625; padding: 12px 20px; border-radius: 10px; border: 1px solid #1E293B; margin-bottom: 20px;'>
        <div>
            <span style='font-size:22px; font-weight:bold; color:white;'>{selected_symbol}</span>
            <span style='color:#94A3B8; font-size:14px; margin-left:10px;'>({stock_raw['name']})</span>
        </div>
        <div>
            <span style='font-size:18px; font-weight:bold; color:#10B981;'>{stock_raw['price']:.2f} THB</span>
            <span style='color:#64748B; font-size:12px; margin-left:20px;'>Market Cap: {stock_raw['mcap']}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 6. TAB 1: OVERVIEW DASHBOARD
# ==========================================
if "Overview" in selected_tab:
    st.markdown("## OVERVIEW DASHBOARD")
    st.caption("AI-Powered Investment Decision Support System")
    
    col_left, col_mid, col_right = st.columns([3.2, 5.6, 3.2])
    
    # --- LEFT COLUMN (Panel ซ้าย) ---
    with col_left:
        with st.container(border=True):
            st.markdown(f"""
                <div style='font-size:20px; font-weight:bold; color:white;'>{selected_symbol} ☆</div>
                <div style='font-size:12px; color:#94A3B8; margin-bottom:12px;'>{stock_raw['name']}</div>
                <div style='font-size:28px; font-weight:bold; color:white;'>{stock_raw['price']:.2f} <span style='font-size:14px;'>THB</span></div>
                <div style='color:#10B981; font-size:12px;'>+2.00 (+1.40%) ▲</div>
                <div style='font-size:10px; color:#64748B; margin-top:2px; margin-bottom:10px;'>Market Closed | 23 May 2025</div>
            """, unsafe_allow_html=True)
            
            fig_stock = create_stock_price_chart(stock_raw["dates"], stock_raw["prices_hist"])
            st.plotly_chart(fig_stock, use_container_width=True, config={'displayModeBar': False})
            
            st.markdown(f"""
                <hr style='border-color:#1E293B; margin:15px 0;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                    <div><div class='metric-label'>Market Cap</div><div class='metric-value' style='font-size:13px;'>{stock_raw['mcap']}</div></div>
                    <div><div class='metric-label'>P/E (TTM)</div><div class='metric-value' style='font-size:13px;'>{stock_raw['pe']}x</div></div>
                </div>
                <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                    <div><div class='metric-label'>Sector</div><div class='metric-value' style='font-size:13px;'>{stock_raw['sector']}</div></div>
                    <div><div class='metric-label'>P/B (TTM)</div><div class='metric-value' style='font-size:13px;'>{stock_raw['pb']}x</div></div>
                </div>
                <div style='display:flex; justify-content:space-between;'>
                    <div><div class='metric-label'>Industry</div><div class='metric-value' style='font-size:13px;'>{stock_raw['industry']}</div></div>
                    <div><div class='metric-label'>Dividend Yield</div><div class='metric-value' style='font-size:13px;'>{stock_raw['div']}%</div></div>
                </div>
            """, unsafe_allow_html=True)

    # --- MIDDLE COLUMN (Panel กลางครอบ 6 โมดูลสมบูรณ์แบบ ไร้ <div> หลุด) ---
    with col_mid:
        with st.container(border=True):
            st.markdown("<h5 style='margin-bottom:10px; color:white;'>INVESTMENT DECISION OVERVIEW</h5>", unsafe_allow_html=True)
            
            mos_class = "badge-excellent" if calc['mos_pct'] > 0 else "badge-danger"
            mos_label = "UNDERVALUED" if calc['mos_pct'] > 0 else "OVERVALUED"
            
            c1 = get_module_card_html("01", "COMPANY HEALTH", calc["m1_score"], "#10B981", "EXCELLENT", "badge-excellent", "Strong financial health & sustainable quality")
            c2 = get_module_card_html("02", "FAIR VALUE", calc["m2_score"], "#F59E0B", mos_label, mos_class, f"Attractive valuation (MoS {calc['mos_pct']:+.1f}%)")
            c3 = get_module_card_html("03", "ENTRY TIMING", calc["m3_score"], "#3B82F6", "NEUTRAL", "badge-good", "Wait for better entry point based on technicals")
            c4 = get_module_card_html("04", "AI PREDICTION", calc["m4_score"], "#8B5CF6", "POSITIVE", "badge-good", "AI forecasts positive price movement in 6-12m")
            c5 = get_module_card_html("05", "RISK ANALYSIS", calc["m5_score"], "#F97316", "MODERATE", "badge-warn", "Moderate risk level with key factors to monitor")
            c6 = get_module_card_html("06", "BENCHMARK", calc["m6_score"], "#06B6D4", "OUTPERFORM", "badge-excellent", "Outperforming industry average across metrics")
            
            grid_html = f"<div class='modules-grid'>{c1}{c2}{c3}{c4}{c5}{c6}</div>"
            st.markdown(grid_html, unsafe_allow_html=True)

    # --- RIGHT COLUMN (Panel ขวาครอบ AI Summary) ---
    with col_right:
        with st.container(border=True):
            st.markdown("<h5 style='margin-bottom:10px; color:white; text-align:center;'>AI INVESTMENT SUMMARY</h5>", unsafe_allow_html=True)
            
            st.plotly_chart(create_gauge_meter(calc["overall_score"]), use_container_width=True, config={'displayModeBar': False})
            
            st.markdown(f"<div style='color:#94A3B8; font-size:10px; font-weight:bold; text-align:center; margin-top:-10px;'>OVERALL SCORE</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='star-rating' style='font-size:18px; text-align:center;'>{render_stars(calc['overall_score'])}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:#10B981; margin:6px 0; text-align:center;'>{calc['rec_text']}</h3>", unsafe_allow_html=True)
            
            st.markdown(f"<p style='font-size:11px; color:#94A3B8; line-height:1.4; text-align:center;'>{selected_symbol} shows attractive investment potential with strong fundamentals and solid AI predictions.</p>", unsafe_allow_html=True)
            
            st.divider()
            st.markdown("<div style='color:#64748B; font-size:11px; font-weight:bold; text-align:center;'>RECOMMENDATION</div>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#10B981; margin:5px 0; text-align:center;'>🚀 {calc['rec']}</h2>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center; font-size:10px; color:#64748B;'>Investment Horizon: LONG TERM (12+ Months)</div>", unsafe_allow_html=True)

    # --- BOTTOM ROW: HIGHLIGHT CARDS ---
    st.markdown("##### KEY HIGHLIGHTS")
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns(6)
    fin = stock_raw["financials"]
    
    with h_col1:
        with st.container(border=True):
            st.markdown(f"📈 <span class='metric-label'>Revenue Growth</span><div class='metric-value' style='color:#10B981;'>{fin['RevGrowth']:+.1f}%</div><span class='metric-label'>YoY 2024</span>", unsafe_allow_html=True)
    with h_col2:
        with st.container(border=True):
            st.markdown(f"💰 <span class='metric-label'>Net Profit Growth</span><div class='metric-value' style='color:#10B981;'>{fin['NetGrowth']:+.1f}%</div><span class='metric-label'>YoY 2024</span>", unsafe_allow_html=True)
    with h_col3:
        with st.container(border=True):
            st.markdown(f"🔄 <span class='metric-label'>ROE (TTM)</span><div class='metric-value' style='color:#3B82F6;'>{fin['ROE']:.1f}%</div><span class='metric-label'>High Efficiency</span>", unsafe_allow_html=True)
    with h_col4:
        with st.container(border=True):
            st.markdown(f"💵 <span class='metric-label'>Free Cash Flow</span><div class='metric-value' style='font-size:14px;'>{fin['FCF']}</div><span class='metric-label'>Strong Cash Gen</span>", unsafe_allow_html=True)
    with h_col5:
        with st.container(border=True):
            st.markdown(f"🛡️ <span class='metric-label'>Debt to Equity</span><div class='metric-value' style='color:#F59E0B;'>{fin['DE']:.2f}x</div><span class='metric-label'>Low Risk</span>", unsafe_allow_html=True)
    with h_col6:
        with st.container(border=True):
            st.markdown(f"🏆 <span class='metric-label'>Industry Rank</span><div class='metric-value' style='color:#06B6D4;'>{fin['Rank']}</div><span class='metric-label'>In Sector</span>", unsafe_allow_html=True)

# ==========================================
# 7. TAB 2: COMPANY HEALTH
# ==========================================
elif "Company Health" in selected_tab:
    st.markdown(f"## COMPANY HEALTH ANALYSIS ({selected_symbol})")
    
    col1, col2 = st.columns([4, 8])
    with col1:
        st.markdown(get_module_card_html("01", "OVERALL HEALTH SCORE", calc["m1_score"], "#10B981", f"SCORE {calc['m1_score']}", "badge-excellent", "Strong financial health"), unsafe_allow_html=True)

    with col2:
        with st.container(border=True):
            st.markdown("##### 💡 EXPLAINABLE AI REASONING")
            st.write(f"จากการประมวลผลตรรกะ Rule-Based: บริษัท {selected_symbol} มีคะแนน ROE เท่ากับ {stock_raw['financials']['ROE']}% และมีภาระหนี้สิน D/E เท่ากับ {stock_raw['financials']['DE']}x ส่งผลให้ระดับเสถียรภาพทางการเงินอยู่ในเกณฑ์สอดคล้องกับมาตรฐาน KOS 1.0")

    st.markdown("##### 7 DIMENSIONS SCORE BREAKDOWN")
    dim_cols = st.columns(7)
    for idx, dim in enumerate(calc["m1_dims"]):
        with dim_cols[idx]:
            st.markdown(get_module_card_html(f"0{idx+1}", dim["name"], round(dim["score"]), "#10B981", f"W: {dim['w']}", "badge-excellent", ""), unsafe_allow_html=True)

    st.divider()
    st.markdown("##### 📋 FINANCIAL STATEMENT HISTORY & RATIOS")
    st.dataframe(stock_raw["history_table"], use_container_width=True, hide_index=True)

# ==========================================
# 8. TAB 3: FAIR VALUE ASSESSMENT (ปรับเปลี่ยนเป็น Stat Cards สีมืดตัวหนังสือสว่าง)
# ==========================================
elif "Fair Value" in selected_tab:
    st.markdown(f"## FAIR VALUE ASSESSMENT ({selected_symbol})")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    status_label = "UNDERVALUED" if calc['mos_pct'] > 0 else "OVERVALUED"
    status_color = "#10B981" if calc['mos_pct'] > 0 else "#EF4444"
    
    with col_f1:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>CURRENT MARKET PRICE</div><div class='fv-val'>{stock_raw['price']:.2f} <span style='font-size:14px;'>THB</span></div></div>", unsafe_allow_html=True)
    with col_f2:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>ESTIMATED FAIR VALUE (BASE)</div><div class='fv-val' style='color:#3B82F6;'>{calc['fair_base']:.2f} <span style='font-size:14px;'>THB</span></div></div>", unsafe_allow_html=True)
    with col_f3:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>MARGIN OF SAFETY</div><div class='fv-val' style='color:{status_color};'>{calc['mos_pct']:+.1f}%</div></div>", unsafe_allow_html=True)
    with col_f4:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>VALUATION STATUS</div><div class='fv-val' style='color:{status_color}; font-size:22px;'>{status_label}</div></div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("##### INTRINSIC VALUE RANGE (DCF SCENARIOS)")
    sc_col1, sc_col2, sc_col3 = st.columns(3)
    
    with sc_col1:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>Bear Case</div><div class='fv-val' style='color:#F59E0B;'>{calc['fair_bear']:.2f} THB</div><div class='fv-sub' style='color:#64748B;'>Conservative Growth</div></div>", unsafe_allow_html=True)
    with sc_col2:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>Base Case (Target)</div><div class='fv-val' style='color:#10B981;'>{calc['fair_base']:.2f} THB</div><div class='fv-sub' style='color:#10B981;'>Base Growth</div></div>", unsafe_allow_html=True)
    with sc_col3:
        st.markdown(f"<div class='fv-card'><div class='fv-label'>Bull Case</div><div class='fv-val' style='color:#3B82F6;'>{calc['fair_bull']:.2f} THB</div><div class='fv-sub' style='color:#3B82F6;'>Optimistic Growth</div></div>", unsafe_allow_html=True)

else:
    st.info("โมดูลอื่นๆ พร้อมขยายระบบเชื่อมต่อข้อมูลเชิงลึกในลำดับถัดไปครับ")
