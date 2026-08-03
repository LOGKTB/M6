import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

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
            "m3": {"trend": "Sideways", "rsi": 48.5, "adx": 16.2, "stoch": "Neutral", "vol_trend": "Normal Volume", "support": 11.8, "resista
