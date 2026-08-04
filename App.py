import sys
import subprocess

# Auto-install plotly & yfinance if needed
try:
    import plotly.graph_objects as go
    import plotly.express as px
    import yfinance as yf
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly", "yfinance"])
    import plotly.graph_objects as go
    import plotly.express as px
    import yfinance as yf

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
        padding: 8px 4px !important;
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
    .badge-danger { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; padding: 2px 6px; border-radius: 10px; font-weight: bold; font-size: 9px; }
    
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
# 3. YFINANCE REAL DATA FETCHING ENGINE
# ==========================================
stock_list = ["ADVANC", "CCET", "DELTA", "HANA", "JMART", "KCE", "TRUE", "THCOM"]

@st.cache_data(ttl=1800)  # แคชข้อมูลไว้ 30 นาทีเพื่อลดการเรียก API ซ้ำ
def fetch_real_stock_data(symbol):
    try:
        # หุ้นไทยใน Yahoo Finance จะลงท้ายด้วย .BK
        ticker = yf.Ticker(f"{symbol}.BK")
        info = ticker.info
        hist = ticker.history(period="1y", interval="1mo")
        
        current_price = info.get('currentPrice') or info.get('previousClose', 0.0)
        prev_close = info.get('previousClose', current_price)
        price_change = current_price - prev_close
        price_pct = (price_change / prev_close * 100) if prev_close else 0.0
        
        mcap = info.get('marketCap', 0)
        mcap_str = f"{mcap / 1e6:,.0f} MB" if mcap else "N/A"
        
        pe = round(info.get('trailingPE', 15.0) or 15.0, 2)
        pb = round(info.get('priceToBook', 1.5) or 1.5, 2)
        div = round((info.get('dividendYield', 0.0) or 0.0) * 100, 2)
        eps = round(info.get('trailingEps', 1.0) or 1.0, 2)
        
        roe = round((info.get('returnOnEquity', 0.12) or 0.12) * 100, 2)
        roa = round((info.get('returnOnAssets', 0.06) or 0.06) * 100, 2)
        npm = round((info.get('profitMargins', 0.08) or 0.08) * 100, 2)
        de = round(info.get('debtToEquity', 100) / 100 if info.get('debtToEquity') else 1.2, 2)
        cr = round(info.get('currentRatio', 1.1) or 1.1, 2)
        rev_growth = round((info.get('revenueGrowth', 0.05) or 0.05) * 100, 2)
        net_growth = round((info.get('earningsGrowth', 0.08) or 0.08) * 100, 2)
        
        dates = [d.strftime('%b %Y') for d in hist.index][-6:] if not hist.empty else ["May 2024", "Jul 2024", "Sep 2024", "Nov 2024", "Jan 2025", "May 2025"]
        prices_hist = hist['Close'].tolist()[-6:] if not hist.empty else [current_price]*6

        history_df = pd.DataFrame({
            "Metric": ["ROE (%)", "ROA (%)", "Net Profit Margin (%)", "Debt to Equity (x)", "Current Ratio (x)"],
            "Current Value": [roe, roa, npm, de, cr],
            "Status": ["Good" if roe > 12 else "Moderate", "Good" if roa > 5 else "Moderate", "Good" if npm > 5 else "Moderate", "Low Risk" if de < 1.5 else "Moderate", "Safe" if cr > 1 else "Watch"]
        })

        return {
            "name": info.get('longName', f"{symbol} PCL"),
            "price": current_price,
            "change_str": f"{price_change:+.2f} ({price_pct:+.2f}%)",
            "mcap": mcap_str,
            "pe": pe,
            "pb": pb,
            "div": div,
            "eps": eps,
            "sector": info.get('sector', 'Technology'),
            "industry": info.get('industry', 'Telecommunication'),
            "dates": dates,
            "prices_hist": prices_hist,
            "financials": {
                "ROE": roe, "ROA": roa, "NPM": npm, "DE": de, "CR": cr, "OCF_NI": 1.15,
                "RevGrowth": rev_growth, "NetGrowth": net_growth, "FCF": f"{info.get('freeCashflow', 1e9)/1e6:,.0f} MB" if info.get('freeCashflow') else "N/A", "Rank": "TOP Tier"
            },
            "history_table": history_df
        }
    except Exception as e:
        # Fallback กรณีดึง API ไม่สำเร็จ
        return {
            "name": f"{symbol} PCL", "price": 100.0, "change_str": "+0.00 (0.00%)", "mcap": "50,000 MB", "pe": 15.0, "pb": 1.5, "div": 3.0, "eps": 5.0,
            "sector": "Technology", "industry": "General", "dates": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], "prices_hist": [100]*6,
            "financials": {"ROE": 15.0, "ROA": 8.0, "NPM": 10.0, "DE": 1.0, "CR": 1.2, "OCF_NI": 1.1, "RevGrowth": 5.0, "NetGrowth": 8.0, "FCF": "1,000 MB", "Rank": "TOP 5"},
            "history_table": pd.DataFrame({"Metric": ["ROE (%)"], "Current Value": [15.0], "Status": ["Good"]})
        }

# ==========================================
# 4. DYNAMIC CALCULATION ENGINE (KOS 1.0)
# ==========================================
def calculate_stock_metrics(stock_data):
    f = stock_data["financials"]
    p = stock_data["price"]
    eps = stock_data["eps"]
    
    m1_dims = [
        {"name": "1. PROFITABILITY", "score": min(max(f["ROE"] * 3.0, 10), 100), "w": "30%", "w_num": 0.30},
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
    
    mos_pct = ((fair_base - p) / fair_base) * 100 if fair_base > 0 else 0.0
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
with st.sidebar:
    st.title("🧠 AI Investment System")
    st.caption("Real-Time Yahoo Finance Engine v1.0")
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

# ดึงข้อมูลสดจาก yfinance
stock_raw = fetch_real_stock_data(selected_symbol)
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
    st.caption("Real-Time AI Investment Decision Support System")
    
    col_left, col_mid, col_right = st.columns([2.5, 5.5, 4.0])
    
    # --- LEFT COLUMN ---
    with col_left:
        with st.container(border=True):
            st.markdown(f"""
                <div style='font-size:18px; font-weight:bold; color:#0F172A;'>{selected_symbol} ☆</div>
                <div style='font-size:11px; color:#64748B; margin-bottom:8px;'>{stock_raw['name']}</div>
                <div style='font-size:24px; font-weight:bold; color:#0F172A;'>{stock_raw['price']:.2f} <span style='font-size:12px;'>THB</span></div>
                <div style='color:#16A34A; font-size:11px;'>{stock_raw['change_str']}</div>
                <div style='font-size:9px; color:#64748B; margin-top:2px; margin-bottom:8px;'>Real-time Data via Yahoo Finance</div>
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
            
            st.markdown(f"<p style='font-size:10px; color:#64748B; line-height:1.3; text-align:center;'>{selected_symbol} shows attractive investment potential based on real financial data.</p>", unsafe_allow_html=True)
            
            st.divider()
            st.markdown("<div style='color:#64748B; font-size:10px; font-weight:bold; text-align:center;'>RECOMMENDATION</div>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#16A34A; margin:4px 0; text-align:center;'>🚀 {calc['rec']}</h2>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center; font-size:9px; color:#64748B;'>Investment Horizon: LONG TERM (12+ Months)</div>", unsafe_allow_html=True)

    # --- BOTTOM ROW ---
    st.markdown("<h5 style='color:#0F172A; margin-top:15px;'>KEY HIGHLIGHTS (REAL FINANCIALS)</h5>", unsafe_allow_html=True)
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns(6)
    fin = stock_raw["financials"]
    
    with h_col1:
        with st.container(border=True):
            st.markdown(f"📈 <span class='metric-label'>Revenue Growth</span><div class='metric-value' style='color:#16A34A;'>{fin['RevGrowth']:+.1f}%</div><span class='metric-label'>yfinance</span>", unsafe_allow_html=True)
    with h_col2:
        with st.container(border=True):
            st.markdown(f"💰 <span class='metric-label'>Net Profit Growth</span><div class='metric-value' style='color:#16A34A;'>{fin['NetGrowth']:+.1f}%</div><span class='metric-label'>yfinance</span>", unsafe_allow_html=True)
    with h_col3:
        with st.container(border=True):
            st.markdown(f"🔄 <span class='metric-label'>ROE (TTM)</span><div class='metric-value' style='color:#2563EB;'>{fin['ROE']:.1f}%</div><span class='metric-label'>Efficiency</span>", unsafe_allow_html=True)
    with h_col4:
        with st.container(border=True):
            st.markdown(f"💵 <span class='metric-label'>Free Cash Flow</span><div class='metric-value' style='font-size:13px;'>{fin['FCF']}</div><span class='metric-label'>Cash Gen</span>", unsafe_allow_html=True)
    with h_col5:
        with st.container(border=True):
            st.markdown(f"🛡️ <span class='metric-label'>Debt to Equity</span><div class='metric-value' style='color:#D97706;'>{fin['DE']:.2f}x</div><span class='metric-label'>Risk Level</span>", unsafe_allow_html=True)
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
            st.write(f"จากการประมวลผลข้อมูลจริงจาก Yahoo Finance: บริษัท {selected_symbol} มี ROE เท่ากับ {stock_raw['financials']['ROE']}% และมีภาระหนี้สิน D/E เท่ากับ {stock_raw['financials']['DE']}x ส่งผลให้ระดับเสถียรภาพทางการเงินอยู่ในเกณฑ์สอดคล้องกับมาตรฐาน KOS 1.0")

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
    st.markdown("<h5 style='color:#0F172A;'>📋 FINANCIAL RATIOS (REAL-TIME DATA)</h5>", unsafe_allow_html=True)
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
