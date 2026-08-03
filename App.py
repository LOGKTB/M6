import sys
import subprocess

# สั่งติดตั้ง plotly อัตโนมัติหากระบบยังไม่มี
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
# 1. SYSTEM CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="CIS - Investment Knowledge Base System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS เพื่อตกแต่งหน้าตา Dashboard
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #0F172A; }
    .sub-header { font-size: 15px; color: #475569; margin-bottom: 15px; }
    .card-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .xai-card {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        border-radius: 8px;
        padding: 15px;
        color: #1E3A8A;
        font-size: 14px;
    }
    .status-strong-buy { color: #15803D; font-weight: bold; }
    .status-accumulate { color: #0369A1; font-weight: bold; }
    .status-hold { color: #B45309; font-weight: bold; }
    .status-sell { color: #B91C1C; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE: 8 TARGET STOCKS (KO-01 to KO-40)
# ==========================================
stock_list = ["ADVANC", "CCET", "DELTA", "HANA", "JMART", "KCE", "TRUE", "THCOM"]

@st.cache_data
def load_data():
    return {
        "ADVANC": {
            "m1": {"roe": 28.5, "npm": 22.1, "roa": 14.2, "rev_growth": 6.2, "eps_growth": 9.5, "de": 1.25, "cr": 0.95, "ocf_ni": 1.25, "health_score": 88},
            "m2": {"price": 285.0, "eps": 11.2, "pe": 25.4, "pbv": 8.2, "ev_ebitda": 11.5, "dcf_base": 310.0, "dcf_bear": 275.0, "dcf_bull": 340.0, "rim_value": 298.0, "fair_value": 305.0, "mos": 6.56},
            "m3": {"trend": "Strong Uptrend", "rsi": 62.5, "adx": 28.4, "stoch": "Neutral", "vol_trend": "Strong Accumulation", "support": 275.0, "resistance": 295.0, "signal": "BULLISH (Wait for Pullback)"},
            "m4": {"pred_7d": 288.5, "pred_30d": 298.0, "pred_90d": 315.0, "confidence": 85, "top_pos": ["ROE (KO-01)", "OCF Quality (KO-07)"], "top_neg": ["D/E Ratio (KO-06)"], "accuracy": 87.5},
            "m5": {"beta": 0.65, "volatility": 16.2, "icr": 8.5, "var_95": -2.1, "sharpe": 1.25, "stress_impact": -8.5, "risk_score": 22, "risk_class": "Low Risk"},
            "m6": {"percentile": 88, "quadrant": "Quality Compounder (Q1)", "cis_score": 86, "grade": "Grade A", "action": "ACCUMULATE", "sizing": "Equal Weight (5-8%)"}
        },
        "CCET": {
            "m1": {"roe": 14.2, "npm": 4.5, "roa": 6.1, "rev_growth": 18.5, "eps_growth": 25.0, "de": 1.65, "cr": 1.15, "ocf_ni": 0.95, "health_score": 71},
            "m2": {"price": 4.20, "eps": 0.35, "pe": 12.0, "pbv": 1.65, "ev_ebitda": 8.2, "dcf_base": 4.80, "dcf_bear": 3.90, "dcf_bull": 5.40, "rim_value": 4.50, "fair_value": 4.70, "mos": 10.64},
            "m3": {"trend": "Strong Uptrend", "rsi": 68.1, "adx": 32.1, "stoch": "Overbought", "vol_trend": "Strong Accumulation", "support": 3.95, "resistance": 4.50, "signal": "BULLISH (Strong Buy)"},
            "m4": {"pred_7d": 4.35, "pred_30d": 4.65, "pred_90d": 5.10, "confidence": 78, "top_pos": ["Revenue Growth (KO-04)", "EV/EBITDA (KO-10)"], "top_neg": ["D/E Ratio (KO-06)"], "accuracy": 81.2},
            "m5": {"beta": 1.35, "volatility": 38.5, "icr": 3.2, "var_95": -4.8, "sharpe": 0.85, "stress_impact": -22.4, "risk_score": 52, "risk_class": "Moderate Risk"},
            "m6": {"percentile": 65, "quadrant": "Quality Compounder (Q1)", "cis_score": 75, "grade": "Grade B", "action": "STRONG BUY", "sizing": "Equal Weight (5-8%)"}
        },
        "DELTA": {
            "m1": {"roe": 32.1, "npm": 16.8, "roa": 21.5, "rev_growth": 22.0, "eps_growth": 28.4, "de": 0.42, "cr": 1.85, "ocf_ni": 1.12, "health_score": 94},
            "m2": {"price": 160.0, "eps": 2.45, "pe": 65.3, "pbv": 18.2, "ev_ebitda": 48.0, "dcf_base": 125.0, "dcf_bear": 105.0, "dcf_bull": 145.0, "rim_value": 118.0, "fair_value": 129.0, "mos": -24.03},
            "m3": {"trend": "Strong Uptrend", "rsi": 74.2, "adx": 41.2, "stoch": "Overbought", "vol_trend": "Strong Accumulation", "support": 148.0, "resistance": 168.0, "signal": "BULLISH (Wait for Pullback)"},
            "m4": {"pred_7d": 163.0, "pred_30d": 155.0, "pred_90d": 142.0, "confidence": 72, "top_pos": ["ROE (KO-01)", "Revenue Growth (KO-04)"], "top_neg": ["P/E Valuation (KO-08)", "P/BV (KO-09)"], "accuracy": 79.5},
            "m5": {"beta": 1.62, "volatility": 42.1, "icr": 25.0, "var_95": -5.2, "sharpe": 0.92, "stress_impact": -35.2, "risk_score": 58, "risk_class": "Moderate Risk"},
            "m6": {"percentile": 92, "quadrant": "Growth at a Premium (Q2)", "cis_score": 81, "grade": "Grade A", "action": "HOLD", "sizing": "Underweight (Max 5%)"}
        },
        "HANA": {
            "m1": {"roe": 11.2, "npm": 8.2, "roa": 7.5, "rev_growth": -2.5, "eps_growth": -8.4, "de": 0.35, "cr": 2.15, "ocf_ni": 1.35, "health_score": 74},
            "m2": {"price": 38.5, "eps": 2.15, "pe": 17.9, "pbv": 1.25, "ev_ebitda": 9.5, "dcf_base": 45.0, "dcf_bear": 38.0, "dcf_bull": 51.0, "rim_value": 42.0, "fair_value": 44.0, "mos": 12.50},
            "m3": {"trend": "Sideways", "rsi": 45.2, "adx": 18.2, "stoch": "Neutral", "vol_trend": "Volume Divergence", "support": 36.0, "resistance": 42.0, "signal": "Neutral"},
            "m4": {"pred_7d": 38.8, "pred_30d": 41.2, "pred_90d": 44.5, "confidence": 81, "top_pos": ["P/BV Valuation (KO-09)", "Financial Stability (KO-06)"], "top_neg": ["Earnings Growth (KO-05)"], "accuracy": 83.0},
            "m5": {"beta": 1.15, "volatility": 28.4, "icr": 12.4, "var_95": -3.5, "sharpe": 0.42, "stress_impact": -14.2, "risk_score": 34, "risk_class": "Moderate Risk"},
            "m6": {"percentile": 54, "quadrant": "Quality Compounder (Q1)", "cis_score": 68, "grade": "Grade B", "action": "ACCUMULATE", "sizing": "Equal Weight (5-8%)"}
        },
        "JMART": {
            "m1": {"roe": 7.8, "npm": 4.1, "roa": 3.8, "rev_growth": 4.2, "eps_growth": 12.1, "de": 2.15, "cr": 1.05, "ocf_ni": 0.82, "health_score": 58},
            "m2": {"price": 14.2, "eps": 0.58, "pe": 24.5, "pbv": 1.85, "ev_ebitda": 14.2, "dcf_base": 13.0, "dcf_bear": 10.5, "dcf_bull": 15.2, "rim_value": 12.2, "fair_value": 13.5, "mos": -5.19},
            "m3": {"trend": "Downtrend", "rsi": 38.4, "adx": 26.5, "stoch": "Neutral", "vol_trend": "Strong Distribution", "support": 13.0, "resistance": 15.8, "signal": "BEARISH (Avoid)"},
            "m4": {"pred_7d": 13.9, "pred_30d": 13.2, "pred_90d": 12.5, "confidence": 84, "top_pos": ["Revenue Growth (KO-04)"], "top_neg": ["D/E Ratio (KO-06)", "Interest Coverage (KO-30)"], "accuracy": 85.1},
            "m5": {"beta": 1.55, "volatility": 45.2, "icr": 1.45, "var_95": -5.8, "sharpe": -0.12, "stress_impact": -28.5, "risk_score": 72, "risk_class": "High Risk"},
            "m6": {"percentile": 28, "quadrant": "Value Trap (Q3)", "cis_score": 48, "grade": "Grade D/F", "action": "SELL / AVOID", "sizing": "0% Position"}
        },
        "KCE": {
            "m1": {"roe": 15.8, "npm": 11.5, "roa": 10.2, "rev_growth": 3.5, "eps_growth": 5.2, "de": 0.58, "cr": 1.75, "ocf_ni": 1.18, "health_score": 81},
            "m2": {"price": 41.0, "eps": 2.12, "pe": 19.3, "pbv": 2.85, "ev_ebitda": 12.1, "dcf_base": 48.5, "dcf_bear": 41.0, "dcf_bull": 55.0, "rim_value": 45.2, "fair_value": 46.5, "mos": 11.83},
            "m3": {"trend": "Moderate Uptrend", "rsi": 54.1, "adx": 22.4, "stoch": "Neutral", "vol_trend": "Normal Volume", "support": 39.0, "resistance": 44.5, "signal": "BULLISH (Wait for Pullback)"},
            "m4": {"pred_7d": 41.5, "pred_30d": 44.0, "pred_90d": 48.0, "confidence": 82, "top_pos": ["NPM (KO-02)", "Financial Stability (KO-06)"], "top_neg": ["Revenue Growth (KO-04)"], "accuracy": 84.2},
            "m5": {"beta": 1.22, "volatility": 31.2, "icr": 11.2, "var_95": -3.8, "sharpe": 0.65, "stress_impact": -16.8, "risk_score": 38, "risk_class": "Moderate Risk"},
            "m6": {"percentile": 72, "quadrant": "Quality Compounder (Q1)", "cis_score": 78, "grade": "Grade B", "action": "ACCUMULATE", "sizing": "Equal Weight (5-8%)"}
        },
        "TRUE": {
            "m1": {"roe": 4.2, "npm": 2.1, "roa": 1.8, "rev_growth": 5.1, "eps_growth": 110.0, "de": 3.85, "cr": 0.62, "ocf_ni": 2.85, "health_score": 52},
            "m2": {"price": 11.8, "eps": 0.22, "pe": 53.6, "pbv": 3.12, "ev_ebitda": 8.1, "dcf_base": 12.5, "dcf_bear": 9.8, "dcf_bull": 14.8, "rim_value": 10.5, "fair_value": 11.9, "mos": 0.84},
            "m3": {"trend": "Strong Uptrend", "rsi": 66.5, "adx": 34.5, "stoch": "Neutral", "vol_trend": "Strong Accumulation", "support": 10.8, "resistance": 12.5, "signal": "BULLISH (Strong Buy)"},
            "m4": {"pred_7d": 12.1, "pred_30d": 12.8, "pred_90d": 13.5, "confidence": 76, "top_pos": ["EV/EBITDA (KO-10)", "Earnings Growth (KO-05)"], "top_neg": ["D/E Ratio (KO-06)", "Current Ratio (KO-07)"], "accuracy": 78.0},
            "m5": {"beta": 1.12, "volatility": 32.5, "icr": 1.35, "var_95": -4.1, "sharpe": 0.52, "stress_impact": -24.5, "risk_score": 68, "risk_class": "High Risk"},
            "m6": {"percentile": 45, "quadrant": "Growth at a Premium (Q2)", "cis_score": 62, "grade": "Grade C", "action": "HOLD", "sizing": "Underweight (Max 5%)"}
        },
        "THCOM": {
            "m1": {"roe": 5.8, "npm": 6.2, "roa": 4.1, "rev_growth": -1.2, "eps_growth": 15.2, "de": 0.28, "cr": 2.85, "ocf_ni": 1.45, "health_score": 72},
            "m2": {"price": 12.5, "eps": 0.45, "pe": 27.7, "pbv": 0.92, "ev_ebitda": 7.8, "dcf_base": 14.5, "dcf_bear": 12.0, "dcf_bull": 16.8, "rim_value": 13.8, "fair_value": 14.2, "mos": 11.97},
            "m3": {"trend": "Sideways", "rsi": 48.5, "adx": 16.2, "stoch": "Neutral", "vol_trend": "Normal Volume", "support": 11.8, "resistance": 13.2, "signal": "Neutral"},
            "m4": {"pred_7d": 12.6, "pred_30d": 13.2, "pred_90d": 14.1, "confidence": 80, "top_pos": ["P/BV (KO-09)", "Financial Stability (KO-06)"], "top_neg": ["ROE (KO-01)", "Revenue Growth (KO-04)"], "accuracy": 82.5},
            "m5": {"beta": 0.85, "volatility": 24.5, "icr": 8.2, "var_95": -3.1, "sharpe": 0.35, "stress_impact": -11.2, "risk_score": 28, "risk_class": "Low Risk"},
            "m6": {"percentile": 48, "quadrant": "Quality Compounder (Q1)", "cis_score": 66, "grade": "Grade B", "action": "ACCUMULATE", "sizing": "Equal Weight (5-8%)"}
        }
    }

db = load_data()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.title("🛡️ CIS Expert System")
    st.caption("Investment Knowledge Base (IKB) KOS 1.0")
    st.divider()
    
    view_mode = st.radio("📌 Select View Mode", ["🌐 Overview (8 Stocks)", "🔍 Single Stock Deep-Dive"])
    st.divider()
    
    if view_mode == "🔍 Single Stock Deep-Dive":
        selected_stock = st.selectbox("📌 Select Target Stock", stock_list)
        selected_module = st.selectbox("🎯 Select Module (KO-01 to KO-40)", [
            "Module 1: Company Health (KO-01 to KO-07)",
            "Module 2: Fair Value (KO-08 to KO-14)",
            "Module 3: Entry Timing (KO-15 to KO-21)",
            "Module 4: AI Prediction (KO-22 to KO-27)",
            "Module 5: Risk Analysis (KO-28 to KO-34)",
            "Module 6: Strategic Matrix (KO-35 to KO-40)"
        ])
    else:
        st.info("💡 Overview Mode displays composite metrics for all 8 target stocks.")

# ==========================================
# 4. VIEW MODE 1: OVERVIEW (8 STOCKS)
# ==========================================
if view_mode == "🌐 Overview (8 Stocks)":
    st.markdown("<div class='main-header'>🌐 Executive Overview: 8 Target Stocks Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Synthesized decision results across Module 1 - 6 (KOS 1.0 Framework)</div>", unsafe_allow_html=True)
    
    summary_list = []
    for s in stock_list:
        d = db[s]
        summary_list.append({
            "Stock Symbol": s,
            "CIS Score (KO-38)": d["m6"]["cis_score"],
            "Grade": d["m6"]["grade"],
            "Health Score (M1)": d["m1"]["health_score"],
            "Fair Value (KO-11)": f"{d['m2']['fair_value']:.2f}",
            "Market Price": f"{d['m2']['price']:.2f}",
            "Margin of Safety (KO-14)": f"{d['m2']['mos']:+.1f}%",
            "Technical Signal (KO-21)": d["m3"]["signal"],
            "Risk Class (KO-34)": d["m5"]["risk_class"],
            "Strategic Quadrant (KO-37)": d["m6"]["quadrant"],
            "Final Action (KO-39)": d["m6"]["action"],
            "Position Size (KO-40)": d["m6"]["sizing"]
        })
    
    df_summary = pd.DataFrame(summary_list)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Stocks Analyzed", "8 Stocks")
    col2.metric("Top CIS Score", "DELTA (81 / Grade A)")
    col3.metric("Highest MoS", "HANA (+12.5%)")
    col4.metric("Lowest Risk", "ADVANC (Score 22/100)")
    
    st.divider()
    
    st.subheader("📋 CIS Benchmark Leaderboard")
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    st.divider()
    
    st.subheader("📌 Strategic Position Matrix (KO-37: Fundamental vs Valuation)")
    
    fig_matrix = px.scatter(
        df_summary,
        x="Health Score (M1)",
        y="Margin of Safety (KO-14)",
        text="Stock Symbol",
        color="Final Action (KO-39)",
        size=[20]*8,
        color_discrete_map={
            "STRONG BUY": "#15803D",
            "ACCUMULATE": "#0369A1",
            "HOLD": "#B45309",
            "SELL / AVOID": "#B91C1C"
        }
    )
    
    fig_matrix.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_matrix.add_vline(x=70, line_dash="dash", line_color="gray")
    
    fig_matrix.update_traces(textposition='top center', textfont=dict(size=14, family="Arial Black"))
    fig_matrix.update_layout(
        xaxis_title="Fundamental Health Score (X-Axis)",
        yaxis_title="Margin of Safety % (Y-Axis)",
        height=500
    )
    
    st.plotly_chart(fig_matrix, use_container_width=True)

# ==========================================
# 5. VIEW MODE 2: SINGLE STOCK DEEP-DIVE
# ==========================================
else:
    s = selected_stock
    d = db[s]
    
    st.markdown(f"<div class='main-header'>🔍 Deep-Dive Analysis: {s}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>Full Knowledge Object Evaluation (KO-01 to KO-40) | Market Price: {d['m2']['price']:.2f} THB</div>", unsafe_allow_html=True)
    
    hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns(5)
    hcol1.metric("CIS Score (KO-38)", f"{d['m6']['cis_score']}/100", d['m6']['grade'])
    hcol2.metric("Fair Value (KO-11)", f"{d['m2']['fair_value']:.2f} THB", f"{d['m2']['mos']:+.1f}% MoS")
    hcol3.metric("Tech Signal (KO-21)", d['m3']['signal'].split(" ")[0])
    hcol4.metric("Risk Level (KO-34)", d['m5']['risk_class'])
    hcol5.metric("Final Verdict (KO-39)", d['m6']['action'])
    
    st.divider()

    # ------------------------------------------
    # MODULE 1: COMPANY HEALTH (KO-01 to KO-07)
    # ------------------------------------------
    if "Module 1" in selected_module:
        st.subheader("🛡️ Module 1: Company Health Analysis (KO-01 to KO-07)")
        
        m1 = d["m1"]
        col_chart, col_xai = st.columns([6, 5])
        
        with col_chart:
            categories = ['ROE (KO-01)', 'NPM (KO-02)', 'ROA (KO-03)', 'Rev Growth (KO-04)', 'EPS Growth (KO-05)', 'D/E Stability (KO-06)', 'Cash Flow (KO-07)']
            values = [
                min(m1["roe"] * 3, 100),
                min(m1["npm"] * 4, 100),
                min(m1["roa"] * 5, 100),
                max(min(m1["rev_growth"] * 3 + 50, 100), 0),
                max(min(m1["eps_growth"] * 2 + 50, 100), 0),
                max(100 - (m1["de"] * 25), 10),
                min(m1["ocf_ni"] * 50, 100)
            ]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(59, 130, 246, 0.2)',
                line=dict(color='#3B82F6', width=2)
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_xai:
            st.markdown("<div class='xai-card'>", unsafe_allow_html=True)
            st.markdown(f"<b>💡 Explainable Reasoning (XAI Engine - Module 1):</b><br>", unsafe_allow_html=True)
            st.markdown(f"* <b>KO-01 (ROE):</b> ROE อยู่ที่ {m1['roe']}% ซึ่ง {'สูงกว่า' if m1['roe'] > 15 else 'ต่ำกว่า'} เกณฑ์อุตสาหกรรม")
            st.markdown(f"* <b>KO-02 (NPM):</b> อัตรากำไรสุทธิอยู่ที่ {m1['npm']}% สะท้อน Pricing Power")
            st.markdown(f"* <b>KO-06 (D/E Ratio):</b> หนี้สินต่อทุนอยู่ที่ {m1['de']} เท่า {'อยู่ในระดับปลอดภัย' if m1['de'] < 1.5 else 'เสี่ยงสูง'}")
            st.markdown(f"* <b>KO-07 (Cash Flow Quality):</b> OCF/NI = {m1['ocf_ni']} เท่า {'กำไรมีคุณภาพเป็นเงินสดจริง' if m1['ocf_ni'] >= 1.0 else 'ระวัง Accrual Items'}")
            st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # MODULE 2: FAIR VALUE (KO-08 to KO-14)
    # ------------------------------------------
    elif "Module 2" in selected_module:
        st.subheader("💎 Module 2: Fair Value Assessment (KO-08 to KO-14)")
        
        m2 = d["m2"]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Market Price", f"{m2['price']:.2f} THB")
        col2.metric("Consensus Fair Value", f"{m2['fair_value']:.2f} THB")
        col3.metric("Margin of Safety (KO-14)", f"{m2['mos']:+.1f}%")
        col4.metric("Valuation Status", "UNDERVALUED" if m2['mos'] > 10 else ("OVERVALUED" if m2['mos'] < -10 else "FAIRLY VALUED"))
        
        st.divider()
        
        col_chart, col_xai = st.columns([6, 5])
        with col_chart:
            models = ['Market Price', 'DCF Bear (KO-12)', 'DCF Base (KO-11)', 'DCF Bull (KO-12)', 'RIM Value (KO-13)', 'Fair Value']
            vals = [m2['price'], m2['dcf_bear'], m2['dcf_base'], m2['dcf_bull'], m2['rim_value'], m2['fair_value']]
            
            fig = go.Figure(data=[go.Bar(x=models, y=vals, marker_color=['#64748B', '#EF4444', '#3B82F6', '#22C55E', '#8B5CF6', '#10B981'])])
            fig.update_layout(yaxis_title="Price (THB)", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_xai:
            st.markdown("<div class='xai-card'>", unsafe_allow_html=True)
            st.markdown("<b>💡 Valuation Reasoning (KO-08 to KO-14):</b><br>", unsafe_allow_html=True)
            st.markdown(f"* <b>KO-08 (P/E):</b> Current P/E = {m2['pe']}x (EPS = {m2['eps']} THB)")
            st.markdown(f"* <b>KO-09 (P/BV):</b> P/BV = {m2['pbv']}x")
            st.markdown(f"* <b>KO-10 (EV/EBITDA):</b> EV/EBITDA = {m2['ev_ebitda']}x")
            st.markdown(f"* <b>KO-11 & 12 (DCF Scenario):</b> Base Case {m2['dcf_base']:.2f} THB (Range: {m2['dcf_bear']:.2f} - {m2['dcf_bull']:.2f})")
            st.markdown(f"* <b>KO-14 (Margin of Safety):</b> {m2['mos']:+.1f}% {'มีเกราะป้องกันความเสี่ยงหนา' if m2['mos'] > 15 else 'ไร้เกราะคุ้มกันความเสี่ยง'}")
            st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # MODULE 3: ENTRY TIMING (KO-15 to KO-21)
    # ------------------------------------------
    elif "Module 3" in selected_module:
        st.subheader("⏱️ Module 3: Entry Timing & Technicals (KO-15 to KO-21)")
        
        m3 = d["m3"]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Trend (KO-15)", m3['trend'])
        col2.metric("RSI Momentum (KO-16)", f"{m3['rsi']}")
        col3.metric("ADX Strength (KO-17)", f"{m3['adx']}")
        col4.metric("Volume Pattern (KO-19)", m3['vol_trend'])
        
        st.divider()
        
        st.markdown("<div class='xai-card'>", unsafe_allow_html=True)
        st.markdown(f"<b>💡 Technical Signal Synthesis (KO-21):</b><br>", unsafe_allow_html=True)
        st.markdown(f"* <b>Integrated Verdict:</b> <span class='status-strong-buy'>{m3['signal']}</span>", unsafe_allow_html=True)
        st.markdown(f"* <b>KO-20 Key Levels:</b> Support = {m3['support']} THB | Resistance = {m3['resistance']} THB")
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # MODULE 4: AI PREDICTION (KO-22 to KO-27)
    # ------------------------------------------
    elif "Module 4" in selected_module:
        st.subheader("🤖 Module 4: AI Horizon Prediction & XAI (KO-22 to KO-27)")
        
        m4 = d["m4"]
        p = d["m2"]["price"]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("7D Forecast (KO-22)", f"{m4['pred_7d']:.2f} THB", f"{((m4['pred_7d']-p)/p)*100:+.1f}%")
        col2.metric("30D Forecast (KO-23)", f"{m4['pred_30d']:.2f} THB", f"{((m4['pred_30d']-p)/p)*100:+.1f}%")
        col3.metric("90D Forecast (KO-24)", f"{m4['pred_90d']:.2f} THB", f"{((m4['pred_90d']-p)/p)*100:+.1f}%")
        col4.metric("Model Confidence (KO-25)", f"{m4['confidence']}%")
        
        st.divider()
        
        st.subheader("📌 SHAP Feature Importance (KO-26: Opening the AI Black-Box)")
        col_pos, col_neg = st.columns(2)
        with col_pos:
            st.success(f"🟢 **Top Positive Drivers:** {', '.join(m4['top_pos'])}")
        with col_neg:
            st.error(f"🔴 **Top Negative Drivers:** {', '.join(m4['top_neg'])}")

    # ------------------------------------------
    # MODULE 5: RISK ANALYSIS (KO-28 to KO-34)
    # ------------------------------------------
    elif "Module 5" in selected_module:
        st.subheader("⚠️ Module 5: Risk Analysis & Stress Testing (KO-28 to KO-34)")
        
        m5 = d["m5"]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Market Beta (KO-28)", f"{m5['beta']} x")
        col2.metric("Annual Volatility (KO-29)", f"{m5['volatility']}%")
        col3.metric("Interest Coverage (KO-30)", f"{m5['icr']} x")
        col4.metric("1D VaR 95% (KO-31)", f"{m5['var_95']}%")
        
        st.divider()
        
        st.markdown("<div class='xai-card'>", unsafe_allow_html=True)
        st.markdown(f"<b>💡 Risk Aggregation Synthesis (KO-34):</b><br>", unsafe_allow_html=True)
        st.markdown(f"* <b>Overall Risk Score:</b> {m5['risk_score']}/100 ({m5['risk_class']})")
        st.markdown(f"* <b>KO-32 Sharpe Ratio:</b> {m5['sharpe']} x")
        st.markdown(f"* <b>KO-33 Macro Stress Test Impact:</b> {m5['stress_impact']}% Valuation Reduction under Recession Scenario")
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # MODULE 6: STRATEGIC MATRIX (KO-35 to KO-40)
    # ------------------------------------------
    elif "Module 6" in selected_module:
        st.subheader("🎯 Module 6: Strategic Matrix & Execution (KO-35 to KO-40)")
        
        m6 = d["m6"]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sector Percentile (KO-35)", f"{m6['percentile']}th")
        col2.metric("Strategic Quadrant (KO-37)", m6['quadrant'])
        col3.metric("Final Verdict (KO-39)", m6['action'])
        col4.metric("Position Size (KO-40)", m6['sizing'])
        
        st.divider()
        
        st.markdown("<div class='xai-card'>", unsafe_allow_html=True)
        st.markdown(f"<b>💡 Final Execution Logic (KO-38 to KO-40):</b><br>", unsafe_allow_html=True)
        st.markdown(f"* <b>KO-38 Composite Score:</b> {m6['cis_score']}/100 ({m6['grade']})")
        st.markdown(f"* <b>Actionable Recommendation:</b> <span class='status-strong-buy'>{m6['action']}</span>", unsafe_allow_html=True)
        st.markdown(f"* <b>Capital Allocation Strategy:</b> Allocation set to <b>{m6['sizing']}</b> based on Risk Parity Principles.")
        st.markdown("</div>", unsafe_allow_html=True)
