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
# 1. SYSTEM CONFIG & DARK THEME CSS
# ==========================================
st.set_page_config(
    page_title="AI Investment Decision Support System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS ถอดแบบธีม Dark Mode ตามรูปภาพ UI
st.markdown("""
    <style>
    /* Global Background & Font */
    .stApp {
        background-color: #0A0E17;
        color: #E2E8F0;
    }
    
    /* Card Container Style */
    .dashboard-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    /* Badges & Colors */
    .badge-excellent { background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid #10B981; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
    .badge-good { background-color: rgba(59, 130, 246, 0.15); color: #3B82F6; border: 1px solid #3B82F6; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
    .badge-warn { background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid #F59E0B; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
    
    /* Text Hierarchy */
    .text-title { font-size: 24px; font-weight: 800; color: #FFFFFF; }
    .text-subtitle { font-size: 13px; color: #94A3B8; }
    .star-rating { font-size: 18px; color: #F59E0B; font-weight: bold; letter-spacing: 2px; }
    .metric-value { font-size: 22px; font-weight: bold; color: #FFFFFF; }
    .metric-label { font-size: 12px; color: #64748B; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER COMPONENTS (GRAPH GENERATORS)
# ==========================================
def render_stars(score_100):
    """แปลงคะแนน 0-100 ให้เป็นดาว 5 ดวง"""
    stars = round(score_100 / 20)
    return "★" * stars + "☆" * (5 - stars)

def create_donut_ring(score, label="", color="#10B981", height=150):
    """สร้าง Donut Progress Circle ตามรูปแบบในรูปภาพ"""
    fig = go.Figure(data=[go.Pie(
        labels=['Score', 'Remaining'],
        values=[score, max(100 - score, 0)],
        hole=0.78,
        marker_colors=[color, "#1F2937"],
        textinfo='none',
        hoverinfo='none'
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=5, b=5, l=5, r=5),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(
            text=f"<b style='font-size:24px;color:white;'>{score}</b><br><span style='font-size:11px;color:#94A3B8;'>/100</span>",
            x=0.5, y=0.5, showarrow=False
        )]
    )
    return fig

def create_gauge_meter(score, title="OVERALL SCORE"):
    """สร้าง Semi-Gauge Meter สำหรับ AI Investment Summary"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': "/100", 'font': {'size': 28, 'color': 'white'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 0, 'tickcolor': "rgba(0,0,0,0)", 'showticklabels': False},
            'bar': {'color': "#10B981"},
            'bgcolor': "#1F2937",
            'bordercolor': "rgba(0,0,0,0)"
        }
    ))
    fig.update_layout(
        height=160,
        margin=dict(t=20, b=0, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_mini_sparkline(prices, color="#10B981"):
    """สร้าง Mini Price Chart ฝั่งซ้ายมือ"""
    fig = go.Figure(data=go.Scatter(y=prices, mode='lines', fill='tozeroy', line=dict(color=color, width=2)))
    fig.update_layout(
        height=90,
        margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# ==========================================
# 3. SINGLE STOCK DATA ENGINE (8 STOCKS)
# ==========================================
stock_list = ["ADVANC", "CCET", "DELTA", "HANA", "JMART", "KCE", "TRUE", "THCOM"]

@st.cache_data
def get_stock_data(symbol):
    # Base Template สำหรับสลับดูทีละบริษัท
    db = {
        "ADVANC": {
            "name": "Advanced Info Service PCL", "price": 145.00, "change": "+2.00 (+1.40%)", "mcap": "611,408 MB", "pe": "20.35", "sector": "Technology", "pb": "7.35", "industry": "Telecommunication", "div": "3.45%",
            "sparkline": [135, 138, 142, 140, 145, 143, 148, 145],
            "overall": 75, "rec": "BUY", "rec_text": "ATTRACTIVE", "rec_desc": "ADVANC shows attractive investment potential with strong fundamentals, undervalued price, and positive AI prediction.",
            "m1_score": 92, "m2_score": 78, "m3_score": 65, "m4_score": 72, "m5_score": 60, "m6_score": 85,
            "highlights": {"rev": "+14.2%", "net": "+18.7%", "roe": "36.2%", "fcf": "25,041 MB", "de": "0.58", "rank": "TOP 3"},
            "m1_dims": [
                {"name": "1. PROFITABILITY", "score": 94, "status": "EXCELLENT", "w": "30%"},
                {"name": "2. GROWTH", "score": 85, "status": "VERY GOOD", "w": "15%"},
                {"name": "3. STABILITY", "score": 90, "status": "EXCELLENT", "w": "20%"},
                {"name": "4. LIQUIDITY", "score": 87, "status": "VERY GOOD", "w": "10%"},
                {"name": "5. CASH FLOW", "score": 89, "status": "VERY GOOD", "w": "10%"},
                {"name": "6. EFFICIENCY", "score": 88, "status": "VERY GOOD", "w": "10%"},
                {"name": "7. EARNINGS QLTY", "score": 93, "status": "EXCELLENT", "w": "5%"}
            ],
            "m1_trend": [75, 76, 81, 86, 90, 92],
            "m1_table": pd.DataFrame({
                "Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"],
                "2023": [35.2, 15.8, 24.6, 0.45, 2.25, 1.28],
                "2024": [37.1, 16.9, 26.1, 0.41, 2.35, 1.31],
                "2025 Q1": [36.2, 16.3, 25.4, 0.40, 2.41, 1.35],
                "Status": ["Excellent", "Excellent", "Excellent", "Excellent", "Excellent", "Excellent"]
            }),
            "m2_fair": 172.00, "m2_mos": "15.7%", "m2_bear": 156.00, "m2_base": 172.00, "m2_bull": 191.00
        },
        "DELTA": {
            "name": "Delta Electronics (Thailand) PCL", "price": 160.00, "change": "+3.50 (+2.24%)", "mcap": "1,996,000 MB", "pe": "65.30", "sector": "Technology", "pb": "18.20", "industry": "Electronic Components", "div": "0.85%",
            "sparkline": [120, 130, 140, 135, 150, 155, 160],
            "overall": 82, "rec": "ACCUMULATE", "rec_text": "OUTPERFORM", "rec_desc": "Strong profitability and global EV/AI Server demand support long-term growth momentum.",
            "m1_score": 94, "m2_score": 68, "m3_score": 80, "m4_score": 85, "m5_score": 58, "m6_score": 92,
            "highlights": {"rev": "+22.0%", "net": "+28.4%", "roe": "32.1%", "fcf": "18,500 MB", "de": "0.42", "rank": "TOP 1"},
            "m1_dims": [
                {"name": "1. PROFITABILITY", "score": 96, "status": "EXCELLENT", "w": "30%"},
                {"name": "2. GROWTH", "score": 92, "status": "EXCELLENT", "w": "15%"},
                {"name": "3. STABILITY", "score": 95, "status": "EXCELLENT", "w": "20%"},
                {"name": "4. LIQUIDITY", "score": 85, "status": "VERY GOOD", "w": "10%"},
                {"name": "5. CASH FLOW", "score": 88, "status": "VERY GOOD", "w": "10%"},
                {"name": "6. EFFICIENCY", "score": 90, "status": "EXCELLENT", "w": "10%"},
                {"name": "7. EARNINGS QLTY", "score": 92, "status": "EXCELLENT", "w": "5%"}
            ],
            "m1_trend": [80, 84, 88, 90, 92, 94],
            "m1_table": pd.DataFrame({
                "Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)", "OCF / Net Income (x)"],
                "2023": [26.2, 18.2, 14.1, 0.55, 1.65, 1.10],
                "2024": [29.5, 19.8, 15.5, 0.48, 1.75, 1.12],
                "2025 Q1": [32.1, 21.5, 16.8, 0.42, 1.85, 1.15],
                "Status": ["Excellent", "Excellent", "Excellent", "Excellent", "Excellent", "Excellent"]
            }),
            "m2_fair": 129.00, "m2_mos": "-19.3%", "m2_bear": 105.00, "m2_base": 125.00, "m2_bull": 145.00
        }
    }
    
    # Fallback สำหรับตัวเลือกอื่น
    if symbol not in db:
        data = db["ADVANC"].copy()
        data["name"] = f"{symbol} Corporation PCL"
        return data
    return db[symbol]

# ==========================================
# 4. SIDEBAR NAVIGATION & COMPANY SELECTOR
# ==========================================
with st.sidebar:
    st.title("🧠 AI Investment System")
    st.caption("Decision Support System v1.0")
    st.divider()
    
    # 📌 ช่องเลือกบริษัทสำหรับดูทีละตัว
    selected_company = st.selectbox("📌 เลือกบริษัทที่ต้องการดู (Select Company):", stock_list, index=0)
    st.divider()
    
    # เมนูเลือกแท็บ
    selected_tab = st.radio("🎯 เมนูการวิเคราะห์ (Modules):", [
        " Overview",
        " Company Health",
        " Fair Value",
        " Entry Timing",
        " AI Prediction",
        " Risk Analysis",
        " Industry Benchmark"
    ])

# โหลดข้อมูลบริษัทที่เลือก
stock = get_stock_data(selected_company)

# Header Bar บนหน้าจอหลัก
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; background-color: #111827; padding: 12px 20px; border-radius: 10px; border: 1px solid #1F2937; margin-bottom: 20px;'>
        <div>
            <span style='font-size:22px; font-weight:bold; color:white;'>{selected_company}</span>
            <span style='color:#94A3B8; font-size:14px; margin-left:10px;'>({stock['name']})</span>
        </div>
        <div>
            <span style='font-size:18px; font-weight:bold; color:#10B981;'>{stock['price']:.2f} THB</span>
            <span style='color:#10B981; font-size:12px; margin-left:8px;'>{stock['change']}</span>
            <span style='color:#64748B; font-size:12px; margin-left:20px;'>Market Cap: {stock['mcap']}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. TAB 1: OVERVIEW DASHBOARD
# ==========================================
if "Overview" in selected_tab:
    st.markdown("## OVERVIEW DASHBOARD")
    st.caption("AI-Powered Investment Decision Support System")
    
    # Grid 3 คอลัมน์หลักตามรูปภาพ 1
    col_left, col_mid, col_right = st.columns([3, 5, 3])
    
    # --- LEFT COLUMN: Stock Price Card & Info ---
    with col_left:
        st.markdown(f"""
            <div class='dashboard-card'>
                <div style='font-size:20px; font-weight:bold; color:white;'>{selected_company} ☆</div>
                <div style='font-size:12px; color:#94A3B8;'>{stock['name']}</div>
                <div style='font-size:28px; font-weight:bold; color:white; margin-top:10px;'>{stock['price']:.2f} <span style='font-size:14px;'>THB</span></div>
                <div style='color:#10B981; font-size:13px;'>{stock['change']} ▲</div>
                <div style='font-size:10px; color:#64748B; margin-top:5px;'>Market Closed</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Mini Price Chart
        fig_spark = create_mini_sparkline(stock["sparkline"])
        st.plotly_chart(fig_spark, use_container_width=True)
        
        # Stats List
        st.markdown(f"""
            <div class='dashboard-card'>
                <div style='display:flex; justify-size:space-between; margin-bottom:8px;'>
                    <div><div class='metric-label'>Market Cap</div><div class='metric-value' style='font-size:14px;'>{stock['mcap']}</div></div>
                    <div><div class='metric-label'>P/E (TTM)</div><div class='metric-value' style='font-size:14px;'>{stock['pe']}</div></div>
                </div>
                <div style='display:flex; justify-size:space-between; margin-bottom:8px;'>
                    <div><div class='metric-label'>Sector</div><div class='metric-value' style='font-size:14px;'>{stock['sector']}</div></div>
                    <div><div class='metric-label'>P/B (TTM)</div><div class='metric-value' style='font-size:14px;'>{stock['pb']}</div></div>
                </div>
                <div style='display:flex; justify-size:space-between;'>
                    <div><div class='metric-label'>Industry</div><div class='metric-value' style='font-size:14px;'>{stock['industry']}</div></div>
                    <div><div class='metric-label'>Dividend Yield</div><div class='metric-value' style='font-size:14px;'>{stock['div']}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- MIDDLE COLUMN: 6 Modules Grid Cards ---
    with col_mid:
        st.markdown("##### INVESTMENT DECISION OVERVIEW")
        
        m_row1_col1, m_row1_col2, m_row1_col3 = st.columns(3)
        with m_row1_col1:
            st.markdown("<div class='dashboard-card' style='text-align:center;'>", unsafe_allow_html=True)
            st.caption("01 COMPANY HEALTH")
            st.plotly_chart(create_donut_ring(stock["m1_score"], color="#10B981", height=110), use_container_width=True)
            st.markdown(f"<div class='star-rating'>{render_stars(stock['m1_score'])}</div>", unsafe_allow_html=True)
            st.markdown("<div class='badge-excellent'>EXCELLENT</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with m_row1_col2:
            st.markdown("<div class='dashboard-card' style='text-align:center;'>", unsafe_allow_html=True)
            st.caption("02 FAIR VALUE")
            st.plotly_chart(create_donut_ring(stock["m2_score"], color="#F59E0B", height=110), use_container_width=True)
            st.markdown(f"<div class='star-rating'>{render_stars(stock['m2_score'])}</div>", unsafe_allow_html=True)
            st.markdown("<div class='badge-warn'>UNDERVALUED</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with m_row1_col3:
            st.markdown("<div class='dashboard-card' style='text-align:center;'>", unsafe_allow_html=True)
            st.caption("03 ENTRY TIMING")
            st.plotly_chart(create_donut_ring(stock["m3_score"], color="#3B82F6", height=110), use_container_width=True)
            st.markdown(f"<div class='star-rating'>{render_stars(stock['m3_score'])}</div>", unsafe_allow_html=True)
            st.markdown("<div class='badge-good'>NEUTRAL</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        m_row2_col1, m_row2_col2, m_row2_col3 = st.columns(3)
        with m_row2_col1:
            st.markdown("<div class='dashboard-card' style='text-align:center;'>", unsafe_allow_html=True)
            st.caption("04 AI PREDICTION")
            st.plotly_chart(create_donut_ring(stock["m4_score"], color="#8B5CF6", height=110), use_container_width=True)
            st.markdown(f"<div class='star-rating'>{render_stars(stock['m4_score'])}</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:#8B5CF6; font-weight:bold;'>POSITIVE</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with m_row2_col2:
            st.markdown("<div class='dashboard-card' style='text-align:center;'>", unsafe_allow_html=True)
            st.caption("05 RISK ANALYSIS")
            st.plotly_chart(create_donut_ring(stock["m5_score"], color="#F97316", height=110), use_container_width=True)
            st.markdown(f"<div class='star-rating'>{render_stars(stock['m5_score'])}</div>", unsafe_allow_html=True)
            st.markdown("<div class='badge-warn'>MODERATE</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with m_row2_col3:
            st.markdown("<div class='dashboard-card' style='text-align:center;'>", unsafe_allow_html=True)
            st.caption("06 INDUSTRY BENCHMARK")
            st.plotly_chart(create_donut_ring(stock["m6_score"], color="#06B6D4", height=110), use_container_width=True)
            st.markdown(f"<div class='star-rating'>{render_stars(stock['m6_score'])}</div>", unsafe_allow_html=True)
            st.markdown("<div class='badge-excellent'>OUTPERFORM</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- RIGHT COLUMN: AI Investment Summary ---
    with col_right:
        st.markdown("<div class='dashboard-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("##### AI INVESTMENT SUMMARY")
        st.plotly_chart(create_gauge_meter(stock["overall"]), use_container_width=True)
        st.markdown(f"<div class='star-rating' style='font-size:24px;'>{render_stars(stock['overall'])}</div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#10B981; margin:5px 0;'>{stock['rec_text']}</h3>", unsafe_allow_html=True)
        st.caption(stock["rec_desc"])
        st.divider()
        st.markdown("<div style='color:#94A3B8; font-size:12px;'>RECOMMENDATION</div>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:#10B981; margin:0;'>🚀 {stock['rec']}</h2>", unsafe_allow_html=True)
        st.caption("Investment Horizon: LONG TERM (12+ Months)")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- BOTTOM ROW: KEY HIGHLIGHTS 6 CARDS ---
    st.markdown("##### KEY HIGHLIGHTS")
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns(6)
    hl = stock["highlights"]
    
    with h_col1:
        st.markdown(f"<div class='dashboard-card'>📈 <span class='metric-label'>Revenue Growth</span><div class='metric-value' style='color:#10B981;'>{hl['rev']}</div><span class='metric-label'>YoY 2024</span></div>", unsafe_allow_html=True)
    with h_col2:
        st.markdown(f"<div class='dashboard-card'>💰 <span class='metric-label'>Net Profit Growth</span><div class='metric-value' style='color:#10B981;'>{hl['net']}</div><span class='metric-label'>YoY 2024</span></div>", unsafe_allow_html=True)
    with h_col3:
        st.markdown(f"<div class='dashboard-card'>🔄 <span class='metric-label'>ROE (TTM)</span><div class='metric-value' style='color:#3B82F6;'>{hl['roe']}</div><span class='metric-label'>High Efficiency</span></div>", unsafe_allow_html=True)
    with h_col4:
        st.markdown(f"<div class='dashboard-card'>💵 <span class='metric-label'>Free Cash Flow</span><div class='metric-value' style='font-size:16px;'>{hl['fcf']}</div><span class='metric-label'>Strong Cash Gen</span></div>", unsafe_allow_html=True)
    with h_col5:
        st.markdown(f"<div class='dashboard-card'>🛡️ <span class='metric-label'>Debt to Equity</span><div class='metric-value' style='color:#F59E0B;'>{hl['de']}</div><span class='metric-label'>Low Risk</span></div>", unsafe_allow_html=True)
    with h_col6:
        st.markdown(f"<div class='dashboard-card'>🏆 <span class='metric-label'>Industry Rank</span><div class='metric-value' style='color:#06B6D4;'>{hl['rank']}</div><span class='metric-label'>In Sector</span></div>", unsafe_allow_html=True)

# ==========================================
# 6. TAB 2: COMPANY HEALTH
# ==========================================
elif "Company Health" in selected_tab:
    st.markdown("## COMPANY HEALTH ANALYSIS")
    st.caption("ประเมินสุขภาพทางการเงินของบริษัทจาก 7 มิติสำคัญ")
    
    col1, col2, col3 = st.columns([3, 5, 4])
    
    with col1:
        st.markdown("<div class='dashboard-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.plotly_chart(create_donut_ring(stock["m1_score"], color="#10B981", height=140), use_container_width=True)
        st.markdown("<h3 style='color:#10B981;'>EXCELLENT</h3>", unsafe_allow_html=True)
        st.caption("บริษัทมีสุขภาพทางการเงินแข็งแกร่งมาก มีศักยภาพในการเติบโตอย่างยั่งยืน")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("##### 💡 EXPLAINABLE AI SUMMARY")
        st.write("บริษัทมีความสามารถในการทำกำไรที่ยอดเยี่ยม สภาพคล่องแข็งแกร่ง ฐานะการเงินมั่นคง กระแสเงินสดจากการดำเนินงานดีและต่อเนื่อง ใช้สินทรัพย์อย่างมีประสิทธิภาพ และกำไรมีคุณภาพสูง")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("##### COMPANY HEALTH SCORE TREND")
        fig_trend = px.line(x=["2023", "2023 Q4", "2024 Q2", "2024 Q4", "2025 Q1"], y=stock["m1_trend"], markers=True)
        fig_trend.update_layout(height=160, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("##### 7 DIMENSIONS OVERVIEW")
    dim_cols = st.columns(7)
    for idx, dim in enumerate(stock["m1_dims"]):
        with dim_cols[idx]:
            st.markdown("<div class='dashboard-card' style='text-align:center; padding:10px;'>", unsafe_allow_html=True)
            st.caption(dim["name"])
            st.caption(f"Weight {dim['w']}")
            st.plotly_chart(create_donut_ring(dim["score"], color="#10B981", height=90), use_container_width=True)
            st.markdown(f"<div style='font-size:10px; color:#10B981;'>{dim['status']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='star-rating' style='font-size:10px;'>{render_stars(dim['score'])}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    
    col_tb, col_info = st.columns([7, 5])
    with col_tb:
        st.markdown("##### KEY FINANCIAL HIGHLIGHTS (ล่าสุด 2025 Q1)")
        st.dataframe(stock["m1_table"], use_container_width=True, hide_index=True)
        
    with col_info:
        st.markdown("##### 🟢 STRENGTHS & ⚠️ WATCH OUT")
        st.success("✔ ความสามารถในการทำกำไรอยู่ในระดับสูงและต่อเนื่อง\n\n✔ การเติบโตของรายได้และกำไรเติบโตอย่างสม่ำเสมอ")
        st.warning("⚠️ อัตราการเติบโตเริ่มชะลอตัวลงเล็กน้อยจากปีก่อน\n\n⚠️ ต้องติดตามการลงทุนโครงข่าย 5G ในระยะต่อไป")

# ==========================================
# 7. TAB 3: FAIR VALUE ASSESSMENT
# ==========================================
elif "Fair Value" in selected_tab:
    st.markdown("## FAIR VALUE ASSESSMENT")
    st.caption("ประเมินมูลค่าที่เหมาะสมของหุ้นโดยใช้ 4 มิติหลัก 7 ตัวชี้วัด")
    
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    with col_f1:
        st.markdown("<div class='dashboard-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.caption("FAIR VALUE SUMMARY")
        st.plotly_chart(create_donut_ring(stock["m2_score"], color="#F59E0B", height=100), use_container_width=True)
        st.markdown("<div class='badge-warn'>UNDERVALUED</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_f2:
        st.metric("CURRENT PRICE", f"{stock['price']:.2f} THB")
    with col_f3:
        st.metric("ESTIMATED FAIR VALUE", f"{stock['m2_fair']:.2f} THB")
    with col_f4:
        st.metric("MARGIN OF SAFETY", stock['m2_mos'], delta="Base Case")
    with col_f5:
        st.metric("CONFIDENCE LEVEL", "HIGH", delta="Target 6-12 Months")

    st.divider()
    
    col_sc, col_drv = st.columns([6, 6])
    with col_sc:
        st.markdown("##### INTRINSIC VALUE RANGE (DCF - SCENARIO ANALYSIS)")
        sc_col1, sc_col2, sc_col3 = st.columns(3)
        sc_col1.metric("Bear Case", f"{stock['m2_bear']:.2f} THB", "g = 1.5%")
        sc_col2.metric("Base Case", f"{stock['m2_base']:.2f} THB", "g = 3.0%")
        sc_col3.metric("Bull Case", f"{stock['m2_bull']:.2f} THB", "g = 4.5%")
        
    with col_drv:
        st.markdown("##### VALUATION DRIVERS (KEY INSIGHTS)")
        st.success("✔ DCF (Base Case) สูงกว่าราคาปัจจุบัน 18.6%\n\n✔ PE ต่ำกว่า Industry Average 20.3%")

else:
    st.info("โมดูลส่วนนี้พร้อมสำหรับการขยายผลเชื่อมต่อใน Phase ถัดไปครับ")
