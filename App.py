import sys
import subprocess

# Auto-install plotly if not found in environment
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
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="CIS - Executive Investment Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern UI, Badges, and Star Ratings
st.markdown("""
    <style>
    .main-header { font-size: 28px; font-weight: 800; color: #0F172A; margin-bottom: 5px; }
    .sub-header { font-size: 15px; color: #64748B; margin-bottom: 20px; }
    .card-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .badge-good { background-color: #DCFCE7; color: #15803D; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 13px; }
    .badge-warn { background-color: #FEF9C3; color: #A16207; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 13px; }
    .badge-danger { background-color: #FEE2E2; color: #B91C1C; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 13px; }
    .star-rating { font-size: 22px; color: #F59E0B; font-weight: bold; }
    .xai-card {
        background-color: #F0F9FF;
        border-left: 5px solid #0284C7;
        border-radius: 8px;
        padding: 15px;
        color: #0C4A6E;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS FOR VISUALS
# ==========================================
def render_stars(score_out_of_100):
    """แปลงคะแนน 0-100 ให้เป็นดาว 5 ดวง"""
    stars = round(score_out_of_100 / 20, 1)
    full_stars = int(stars)
    half_star = 1 if (stars - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    return "★" * full_stars + ("½" if half_star else "") + "☆" * empty_stars + f" ({stars}/5.0)"

def create_donut_chart(score, title="", height=160):
    """สร้างกราฟวงกลม Donut Chart แสดงคะแนนตรงกลาง"""
    color = "#22C55E" if score >= 75 else ("#EAB308" if score >= 55 else "#EF4444")
    fig = go.Figure(data=[go.Pie(
        labels=['Score', 'Remaining'],
        values=[score, max(100 - score, 0)],
        hole=0.75,
        marker_colors=[color, "#E2E8F0"],
        textinfo='none',
        hoverinfo='none'
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=height,
        annotations=[dict(
            text=f"<b>{score}</b><br><span style='font-size:10px;color:gray;'>{title}</span>",
            x=0.5, y=0.5, font_size=18, showarrow=False
        )]
    )
    return fig

def create_gauge_chart(value, title="Score", min_v=0, max_v=100, suffix=""):
    """สร้างกราฟ Gauge แบบเข็มวัด"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        number={'suffix': suffix, 'font': {'size': 22}},
        title = {'text': title, 'font': {'size': 14}},
        gauge = {
            'axis': {'range': [min_v, max_v]},
            'bar': {'color': "#0284C7"},
            'steps': [
                {'range': [0, 50], 'color': "#FEE2E2"},
                {'range': [50, 75], 'color': "#FEF9C3"},
                {'range': [75, 100], 'color': "#DCFCE7"}
            ]
        }
    ))
    fig.update_layout(height=180, margin=dict(t=30, b=10, l=25, r=25))
    return fig

# ==========================================
# 3. COMPREHENSIVE DATASET (8 STOCKS)
# ==========================================
stock_list = ["ADVANC", "CCET", "DELTA", "HANA", "JMART", "KCE", "TRUE", "THCOM"]

@st.cache_data
def load_full_database():
    return {
        "DELTA": {
            "profile": {"name": "Delta Electronics (Thailand)", "sector": "Technology", "industry": "Electronic Components", "mcap": "1.99T THB", "price": 160.0, "pe": 65.3, "pb": 18.2, "div_yield": 0.85, "rank": "1 / 8"},
            "highlights": {"rev_growth": "+22.0%", "net_growth": "+28.4%", "roe": "32.1%", "fcf": "18.5B THB", "de": "0.42x"},
            "overall_score": 91,
            "m1": {
                "overall": 94, "verdict": "GOOD (ความแข็งแกร่งระดับเลิศ)", "desc": "โครงสร้างทางการเงินแข็งแกร่งมาก Profitability และ ROE สูงสุดในกลุ่ม",
                "sub_scores": [
                    {"name": "Profitability (ROE)", "score": 95, "weight": "20%", "status": "GOOD", "desc": "ROE > 30% สูงกว่าค่าเฉลี่ยอุตสาหกรรม"},
                    {"name": "Net Profit Margin", "score": 90, "weight": "15%", "status": "GOOD", "desc": "Pricing Power สูง บริหารต้นทุนได้ดี"},
                    {"name": "Return on Assets", "score": 92, "weight": "15%", "status": "GOOD", "desc": "ประสิทธิภาพการใช้สินทรัพย์สร้างกำไรสูง"},
                    {"name": "Revenue Growth", "score": 88, "weight": "15%", "status": "GOOD", "desc": "เติบโตตามอุปสงค์ชิ้นส่วน EV & AI Server"},
                    {"name": "Earnings Growth", "score": 90, "weight": "10%", "status": "GOOD", "desc": "กำไรสุทธิโตสอดคล้องกับรายได้"},
                    {"name": "D/E Stability", "score": 96, "weight": "15%", "status": "GOOD", "desc": "หนี้สินต่ำมาก เสถียรภาพทางการเงินสูง"},
                    {"name": "Cash Flow Quality", "score": 88, "weight": "10%", "status": "GOOD", "desc": "กระแสเงินสดจากการดำเนินงานเป็นบวกสม่ำเสมอ"}
                ],
                "ratios_history": pd.DataFrame({
                    "Financial Metric": ["ROE (%)", "Net Margin (%)", "ROA (%)", "Revenue Growth (%)", "D/E Ratio (x)", "Current Ratio (x)"],
                    "2023": [26.2, 14.1, 18.2, 18.5, 0.55, 1.65],
                    "2024": [29.5, 15.5, 19.8, 20.1, 0.48, 1.75],
                    "2025 (TTM)": [32.1, 16.8, 21.5, 22.0, 0.42, 1.85],
                    "Trend": ["📈 +5.9%", "📈 +2.7%", "📈 +3.3%", "📈 +3.5%", "📉 -0.13x", "📈 +0.20x"]
                }),
                "swot": {"strengths": "ผู้นำเทคโนโลยี Power Management สำหรับ Data Center & EV, ROE สูงเกิน 30%", "weaknesses": "พึ่งพาอุปสงค์ต่างประเทศสูง มีความผันผวนของอัตราแลกเปลี่ยน"},
                "industry_comp": pd.DataFrame({
                    "Financial Ratio": ["ROE (%)", "Net Margin (%)", "D/E Ratio (x)", "PE (x)", "PBV (x)", "Div Yield (%)"],
                    "DELTA": [32.1, 16.8, 0.42, 65.3, 18.2, 0.85],
                    "Industry Avg": [14.5, 7.2, 1.15, 22.4, 2.8, 2.45],
                    "SET Index Avg": [9.8, 5.8, 1.45, 17.5, 1.4, 3.20],
                    "Status vs Market": ["🟢 Outperform", "🟢 Outperform", "🟢 Safer", "🔴 Premium/Expensive", "🔴 Premium", "🟡 Lower"]
                })
            },
            "m2": {
                "fair_value": 129.0, "current_price": 160.0, "mos": -24.03, "status": "OVERVALUED (ราคาแพงกว่ามูลค่าเหมาะสม)",
                "confidence": 78, "verdict": "ราคาตลาดสะท้อนการเติบโตล่วงหน้าไปมาก ควรตั้งรับเมื่อเกิด Correction",
                "range": {"bear": 105.0, "base": 125.0, "bull": 145.0},
                "drivers": ["ความต้องการชิ้นส่วน AI Server", "อัตรากำไรขั้นต้นขั้นสูง", "ต้นทุน WACC ที่ 8.2%"],
                "breakdown": pd.DataFrame({
                    "Valuation Model": ["Relative Valuation (P/E & P/BV)", "Intrinsic DCF Model", "Growth-Adjusted (PEG & RIM)", "Consensus Weighted Avg"],
                    "Estimated Value (THB)": [145.0, 125.0, 118.0, 129.0],
                    "Upside / Downside (%)": [-9.3, -21.8, -26.2, -19.37],
                    "Weight Assigned": ["30%", "50%", "20%", "100%"]
                }),
                "dcf_params": {"WACC": "8.2%", "Terminal Growth Rate": "3.5%", "5Y Rev CAGR": "18.0%", "Target Operating Margin": "17.5%"},
                "sensitivity": pd.DataFrame({
                    "WACC \ Terminal Growth": ["2.5%", "3.0%", "3.5%", "4.0%"],
                    "7.5%": ["128 THB", "136 THB", "145 THB", "158 THB"],
                    "8.2% (Base)": ["112 THB", "118 THB", "125 THB", "134 THB"],
                    "9.0%": ["98 THB", "104 THB", "110 THB", "117 THB"]
                }),
                "price_history": pd.DataFrame({
                    "Date": ["Q1-2024", "Q2-2024", "Q3-2024", "Q4-2024", "Q1-2025"],
                    "Market Price": [115.0, 130.0, 148.0, 155.0, 160.0],
                    "Fair Value": [110.0, 115.0, 120.0, 125.0, 129.0]
                })
            }
        },
        "ADVANC": {
            "profile": {"name": "Advanced Info Service PCL", "sector": "ICT", "industry": "Telecommunications", "mcap": "847B THB", "price": 285.0, "pe": 25.4, "pb": 8.2, "div_yield": 3.85, "rank": "2 / 8"},
            "highlights": {"rev_growth": "+6.2%", "net_growth": "+9.5%", "roe": "28.5%", "fcf": "42.1B THB", "de": "1.25x"},
            "overall_score": 88,
            "m1": {
                "overall": 90, "verdict": "GOOD (หุ้นปันผลและเสถียรภาพสูง)", "desc": "เป็น Cash Cow ที่มีกระแสเงินสดมั่นคง ตลาดผูกขาดกระตุกกำไรสม่ำเสมอ",
                "sub_scores": [
                    {"name": "Profitability (ROE)", "score": 92, "weight": "20%", "status": "GOOD", "desc": "ROE แข็งแกร่งจาก ARPU ที่เพิ่มขึ้น"},
                    {"name": "Net Profit Margin", "score": 88, "weight": "15%", "status": "GOOD", "desc": "บริหารจัดการต้นทุนโครงข่ายได้ดี"},
                    {"name": "Return on Assets", "score": 82, "weight": "15%", "status": "GOOD", "desc": "การใช้งานโครงข่าย 5G คุ้มทุน"},
                    {"name": "Revenue Growth", "score": 75, "weight": "15%", "status": "MODERATE", "desc": "เติบโตตามการใช้งานเน็ตบ้านและองค์กร"},
                    {"name": "Earnings Growth", "score": 80, "weight": "10%", "status": "GOOD", "desc": "กำไรขยายตัวต่อเนื่องจาก synergy 3BB"},
                    {"name": "D/E Stability", "score": 82, "weight": "15%", "status": "GOOD", "desc": "หนี้สินอยู่ในระดับบริหารจัดการได้"},
                    {"name": "Cash Flow Quality", "score": 95, "weight": "10%", "status": "GOOD", "desc": "กระแสเงินสดแข็งแกร่งที่สุดในกลุ่ม"}
                ],
                "ratios_history": pd.DataFrame({
                    "Financial Metric": ["ROE (%)", "Net Margin (%)", "ROA (%)", "Revenue Growth (%)", "D/E Ratio (x)", "Current Ratio (x)"],
                    "2023": [24.1, 19.5, 12.1, 4.5, 1.45, 0.82],
                    "2024": [26.2, 20.8, 13.2, 5.8, 1.32, 0.88],
                    "2025 (TTM)": [28.5, 22.1, 14.2, 6.2, 1.25, 0.95],
                    "Trend": ["📈 +4.4%", "📈 +2.6%", "📈 +2.1%", "📈 +1.7%", "📉 -0.20x", "📈 +0.13x"]
                }),
                "swot": {"strengths": "ส่วนแบ่งตลาดอันดับ 1 ในธุรกิจมือถือ กระแสเงินสดสม่ำเสมอ ปันผลดี", "weaknesses": "การแข่งขันด้านราคาและงบลงทุน 5G/6G ในอนาคต"},
                "industry_comp": pd.DataFrame({
                    "Financial Ratio": ["ROE (%)", "Net Margin (%)", "D/E Ratio (x)", "PE (x)", "PBV (x)", "Div Yield (%)"],
                    "ADVANC": [28.5, 22.1, 1.25, 25.4, 8.2, 3.85],
                    "Industry Avg": [12.1, 8.5, 2.45, 28.1, 3.2, 2.10],
                    "SET Index Avg": [9.8, 5.8, 1.45, 17.5, 1.4, 3.20],
                    "Status vs Market": ["🟢 Outperform", "🟢 Outperform", "🟢 Safer", "🟡 Fair Value", "🔴 Premium", "🟢 High Yield"]
                })
            },
            "m2": {
                "fair_value": 305.0, "current_price": 285.0, "mos": 6.56, "status": "UNDERVALUED (มีส่วนต่างความปลอดภัย)",
                "confidence": 85, "verdict": "ราคาตลาดต่ำกว่า Fair Value เล็กน้อย เหมาะสะสมลงทุนระยะยาว",
                "range": {"bear": 275.0, "base": 305.0, "bull": 340.0},
                "drivers": ["การโตของธุรกิจองค์กร Enterprise Data", "ARPU ปรับตัวขึ้น", "WACC ต่ำที่ 6.8%"],
                "breakdown": pd.DataFrame({
                    "Valuation Model": ["Relative Valuation (P/E & P/BV)", "Intrinsic DCF Model", "Dividend Discount Model (DDM)", "Consensus Weighted Avg"],
                    "Estimated Value (THB)": [295.0, 310.0, 300.0, 305.0],
                    "Upside / Downside (%)": [+3.5, +8.7, +5.2, +7.01],
                    "Weight Assigned": ["20%", "50%", "30%", "100%"]
                }),
                "dcf_params": {"WACC": "6.8%", "Terminal Growth Rate": "2.0%", "5Y Rev CAGR": "5.5%", "Target Operating Margin": "32.0%"},
                "sensitivity": pd.DataFrame({
                    "WACC \ Terminal Growth": ["1.5%", "2.0%", "2.5%"],
                    "6.2%": ["318 THB", "332 THB", "350 THB"],
                    "6.8% (Base)": ["292 THB", "305 THB", "318 THB"],
                    "7.5%": ["268 THB", "278 THB", "288 THB"]
                }),
                "price_history": pd.DataFrame({
                    "Date": ["Q1-2024", "Q2-2024", "Q3-2024", "Q4-2024", "Q1-2025"],
                    "Market Price": [240.0, 255.0, 270.0, 280.0, 285.0],
                    "Fair Value": [280.0, 288.0, 295.0, 300.0, 305.0]
                })
            }
        }
    }

# Load stock dataset
raw_db = load_full_database()

# Mock fallback for remaining stocks
for s in stock_list:
    if s not in raw_db:
        raw_db[s] = raw_db["DELTA"]

# ==========================================
# 4. SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.title("🛡️ CIS Expert System")
    st.caption("Decision Support Platform v1.0")
    st.divider()
    
    view_mode = st.radio("📌 Select View Mode", ["🌐 Executive Overview", "🎯 Module Deep-Dive"])
    st.divider()
    
    if view_mode == "🎯 Module Deep-Dive":
        selected_stock = st.selectbox("📌 Select Target Stock (8 Stocks)", stock_list)
        selected_module = st.selectbox("🎯 Select Module", [
            "Module 1: Company Health Analysis",
            "Module 2: Fair Value Assessment",
            "Module 3: Entry Timing (Technical)",
            "Module 4: AI Prediction",
            "Module 5: Risk Analysis",
            "Module 6: Strategic Execution"
        ])
    else:
        st.info("💡 Overview Mode displays executive summary for all 8 target stocks.")

# ==========================================
# 5. VIEW MODE 1: EXECUTIVE OVERVIEW
# ==========================================
if view_mode == "🌐 Executive Overview":
    st.markdown("<div class='main-header'>🌐 Executive Overview: 8 Target Stocks Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>สรุปภาพรวมและดัชนีชี้วัดสำคัญของหุ้น 8 ตัวหลักย่อในรูปแบบกราฟและ Dashboard</div>", unsafe_allow_html=True)
    
    # Render Stock Cards Grid
    for s in stock_list:
        data = raw_db[s]
        prof = data["profile"]
        high = data["highlights"]
        overall = data["overall_score"]
        
        with st.container():
            st.markdown(f"### 🏢 {s} - {prof['name']}")
            c1, c2, c3, c4 = st.columns([2.5, 2.5, 3.5, 3.5])
            
            with c1:
                # Gauge Overall Score
                fig_g = create_gauge_chart(overall, title="Overall CIS Score", max_v=100)
                st.plotly_chart(fig_g, use_container_width=True)
                st.caption(f"Industry Rank: **{prof['rank']}**")

            with c2:
                # Market Statistics Column
                st.markdown(f"**Market Price:** `{prof['price']:.2f} THB`")
                st.markdown(f"**Market Cap:** `{prof['mcap']}`")
                st.markdown(f"**Sector:** `{prof['sector']}`")
                st.markdown(f"**P/E Ratio:** `{prof['pe']}x` | **P/BV:** `{prof['pb']}x`")
                st.markdown(f"**Dividend Yield:** `{prof['div_yield']}%`")

            with c3:
                # Key Highlight Metrics
                st.markdown("**📊 Financial Highlights:**")
                st.markdown(f"- Revenue Growth: **{high['rev_growth']}**")
                st.markdown(f"- Net Profit Growth: **{high['net_growth']}**")
                st.markdown(f"- ROE (TTM): **{high['roe']}**")
                st.markdown(f"- Free Cash Flow: **{high['fcf']}**")
                st.markdown(f"- D/E Ratio: **{high['de']}**")

            with c4:
                # Donut Chart module scores
                m1_score = data["m1"]["overall"]
                mos_val = data["m2"]["mos"]
                
                fig_d = create_donut_chart(m1_score, title="Health Score", height=140)
                st.plotly_chart(fig_d, use_container_width=True)
                
                mos_color = "badge-good" if mos_val > 0 else "badge-danger"
                st.markdown(f"Margin of Safety: <span class='{mos_color}'>{mos_val:+.1f}%</span>", unsafe_allow_html=True)
            
            st.divider()

# ==========================================
# 6. VIEW MODE 2: MODULE DEEP-DIVE
# ==========================================
else:
    s = selected_stock
    data = raw_db[s]
    prof = data["profile"]
    
    st.markdown(f"<div class='main-header'>🔍 Deep-Dive: {s} ({prof['name']})</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>Sector: {prof['sector']} | Industry: {prof['industry']} | Current Price: {prof['price']:.2f} THB</div>", unsafe_allow_html=True)
    
    # ------------------------------------------
    # MODULE 1: COMPANY HEALTH ANALYSIS
    # ------------------------------------------
    if "Module 1" in selected_module:
        st.subheader("🛡️ Module 1: Company Health Analysis")
        m1 = data["m1"]
        
        # Section 1: Overall Donut & Star Rating
        top_col1, top_col2, top_col3 = st.columns([3, 4, 5])
        
        with top_col1:
            fig_donut = create_donut_chart(m1["overall"], title="M1 Health Score", height=180)
            st.plotly_chart(fig_donut, use_container_width=True)
            
        with top_col2:
            st.markdown("#### Overall Rating")
            stars_html = render_stars(m1["overall"])
            st.markdown(f"<div class='star-rating'>{stars_html}</div>", unsafe_allow_html=True)
            st.markdown(f"**Verdict:** `{m1['verdict']}`")
            st.write(m1["desc"])
            
        with top_col3:
            st.markdown("#### 💡 Strengths & Weaknesses")
            st.success(f"**จุดแข็ง:** {m1['swot']['strengths']}")
            st.warning(f"**จุดอ่อน/ข้อควรระวัง:** {m1['swot']['weaknesses']}")

        st.divider()
        
        # Section 2: Sub-Dimension Donut Scores Grid
        st.subheader("📊 Sub-Dimensions Score Breakdown & Weights")
        
        sub_cols = st.columns(4)
        for idx, sub in enumerate(m1["sub_scores"]):
            col_target = sub_cols[idx % 4]
            with col_target:
                fig_sub = create_donut_chart(sub["score"], title=f"Weight: {sub['weight']}", height=130)
                st.plotly_chart(fig_sub, use_container_width=True)
                st.markdown(f"**{sub['name']}**")
                st.markdown(f"Rating: `{render_stars(sub['score'])}`")
                st.caption(sub["desc"])
                st.write("")

        st.divider()
        
        # Section 3: Financial Ratios History with Trend
        st.subheader("📋 Key Financial Ratios History (3-Year History & Trend)")
        st.dataframe(
            m1["ratios_history"],
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        
        # Section 4: Industry Comparison Table
        st.subheader("🏛️ Industry Comparison Table (Stock vs Market & Industry Avg)")
        st.dataframe(
            m1["industry_comp"],
            use_container_width=True,
            hide_index=True
        )

    # ------------------------------------------
    # MODULE 2: FAIR VALUE ASSESSMENT
    # ------------------------------------------
    elif "Module 2" in selected_module:
        st.subheader("💎 Module 2: Fair Value Assessment")
        m2 = data["m2"]
        
        # Section 1: Summary KPI Cards
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        f_col1.metric("Current Market Price", f"{m2['current_price']:.2f} THB")
        f_col2.metric("Estimated Fair Value", f"{m2['fair_value']:.2f} THB", delta=f"{m2['mos']:+.2f}% MoS")
        f_col3.metric("Margin of Safety (MoS)", f"{m2['mos']:.1f}%")
        f_col4.metric("Valuation Status", m2['status'].split(" ")[0])
        
        st.divider()
        
        # Section 2: Gauge & Intrinsic Range Scenarios
        col_gauge, col_range = st.columns([5, 7])
        
        with col_gauge:
            fig_conf = create_gauge_chart(m2["confidence"], title="Valuation Confidence Level", suffix="%")
            st.plotly_chart(fig_conf, use_container_width=True)
            st.info(f"💡 **Recommendation:** {m2['verdict']}")
            
        with col_range:
            st.subheader("🎯 Intrinsic Value Range (Bear / Base / Bull)")
            range_df = pd.DataFrame({
                "Scenario": ["Bear Case", "Base Case (Target)", "Bull Case", "Current Market Price"],
                "Fair Value (THB)": [m2['range']['bear'], m2['range']['base'], m2['range']['bull'], m2['current_price']]
            })
            
            fig_range = px.bar(
                range_df,
                x="Fair Value (THB)",
                y="Scenario",
                orientation='h',
                color="Scenario",
                text="Fair Value (THB)",
                color_discrete_map={
                    "Bear Case": "#EF4444",
                    "Base Case (Target)": "#3B82F6",
                    "Bull Case": "#22C55E",
                    "Current Market Price": "#64748B"
                }
            )
            fig_range.update_layout(height=260, showlegend=False, margin=dict(t=10, b=10))
            st.plotly_chart(fig_range, use_container_width=True)

        st.divider()
        
        # Section 3: Key Drivers & Model Breakdown Table
        st.subheader("📊 Fair Value Detail Breakdown & Weights")
        
        col_dr, col_tbl = st.columns([4, 8])
        with col_dr:
            st.markdown("#### 🔑 Key Valuation Drivers")
            for dr in m2["drivers"]:
                st.markdown(f"- ✅ {dr}")
            st.write("")
            st.markdown("#### ⚙️ DCF Key Assumptions")
            for k, v in m2["dcf_params"].items():
                st.markdown(f"* **{k}:** `{v}`")

        with col_tbl:
            st.markdown("#### 📋 Valuation Models Summary")
            st.dataframe(m2["breakdown"], use_container_width=True, hide_index=True)

        st.divider()
        
        # Section 4: Sensitivity Analysis & Historical Price vs Fair Value
        col_sens, col_hist = st.columns(2)
        
        with col_sens:
            st.subheader("🎛️ Sensitivity Matrix (WACC vs Growth)")
            st.dataframe(m2["sensitivity"], use_container_width=True, hide_index=True)
            
        with col_hist:
            st.subheader("📈 Historical Price vs Fair Value Trend")
            fig_hist = px.line(
                m2["price_history"],
                x="Date",
                y=["Market Price", "Fair Value"],
                markers=True,
                color_discrete_map={"Market Price": "#64748B", "Fair Value": "#0284C7"}
            )
            fig_hist.update_layout(height=280, margin=dict(t=10, b=10))
            st.plotly_chart(fig_hist, use_container_width=True)

    else:
        st.info(f"โมดูล {selected_module} กำลังอยู่ในช่วงเตรียมเชื่อมต่อชุดข้อมูลกราฟเพิ่มเติม")
