import html

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import requests

from auth import register, verify_user

# ---------------- CONFIG ----------------
BACKEND_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="Disease Prediction Hub", layout="wide", page_icon="🩺")

def apply_global_styles(auth_screen=False):
    background = (
        "linear-gradient(180deg, #eef2ff 0%, #edf1fb 100%)"
        if auth_screen
        else "#F0F8FF"
    )

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {background};
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0d8fc7 0%, #43b9ea 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.18);
            padding-bottom: 0 !important;
            overflow: hidden !important;
        }}
        [data-testid="stSidebarContent"] {{
            overflow: hidden !important;
        }}
        [data-testid="stSidebarUserContent"] {{
            min-height: 100vh;
            overflow: hidden !important;
        }}
        [data-testid="stSidebarUserContent"] > div:first-child {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden !important;
        }}
        [data-testid="stSidebar"] h2 {{
            display: none !important;
        }}
        h1, h2, h3 {{
            color: #0d5f7a !important;
            font-weight: 800 !important;
        }}
        label {{
            color: #073b4c !important;
            font-weight: 700 !important;
        }}
        div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.92) !important;
            border-radius: 14px !important;
            border: 1px solid rgba(80, 162, 208, 0.35) !important;
        }}
        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"] > div,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input {{
            background: transparent !important;
            color: #073b4c !important;
            -webkit-text-fill-color: #073b4c !important;
            caret-color: #0d5f7a !important;
        }}
        div[data-baseweb="input"] svg,
        div[data-baseweb="base-input"] svg {{
            fill: #0d5f7a !important;
            color: #0d5f7a !important;
        }}
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] *:not(svg),
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li,
        div[data-baseweb="menu"] ul,
        div[data-baseweb="menu"] li,
        div[role="listbox"] ul,
        div[role="listbox"] li,
        div[role="option"] {{
            color: #073b4c !important;
            -webkit-text-fill-color: #073b4c !important;
        }}
        div[data-baseweb="select"] svg {{
            fill: #0d5f7a !important;
            color: #0d5f7a !important;
        }}
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        div[role="listbox"],
        div[role="option"] {{
            background: rgba(255, 255, 255, 0.98) !important;
            color: #073b4c !important;
        }}
        div[data-baseweb="popover"] ul,
        div[data-baseweb="menu"] ul,
        div[role="listbox"] {{
            background: rgba(255, 255, 255, 0.98) !important;
        }}
        div[data-baseweb="popover"] li,
        div[data-baseweb="menu"] li,
        div[role="option"] {{
            background: rgba(255, 255, 255, 0.98) !important;
            border-bottom: 1px solid rgba(80, 162, 208, 0.12) !important;
        }}
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="menu"] li:hover,
        div[role="option"]:hover {{
            background: rgba(194, 232, 248, 0.85) !important;
        }}
        div[aria-selected="true"],
        li[aria-selected="true"] {{
            background: rgba(173, 220, 241, 0.9) !important;
            color: #073b4c !important;
        }}
        div[data-baseweb="popover"] *,
        div[data-baseweb="menu"] *,
        div[role="listbox"] *,
        div[role="option"] * {{
            color: #073b4c !important;
            -webkit-text-fill-color: #073b4c !important;
        }}
        [data-testid="stTextArea"] textarea {{
            background: rgba(255, 255, 255, 0.96) !important;
            color: #073b4c !important;
            -webkit-text-fill-color: #073b4c !important;
            caret-color: #0d5f7a !important;
            border: 1px solid rgba(80, 162, 208, 0.35) !important;
            border-radius: 16px !important;
        }}
        [data-testid="stTextArea"] label,
        [data-testid="stTextArea"] p {{
            color: #073b4c !important;
        }}
        [data-testid="stAlert"] {{
            background: rgba(194, 232, 248, 0.75) !important;
            border: 1px solid rgba(80, 162, 208, 0.28) !important;
            color: #073b4c !important;
        }}
        [data-testid="stAlert"] * {{
            color: #073b4c !important;
            -webkit-text-fill-color: #073b4c !important;
        }}
        [data-testid="stTable"] table,
        [data-testid="stTable"] th,
        [data-testid="stTable"] td,
        [data-testid="stDataFrame"] table,
        [data-testid="stDataFrame"] th,
        [data-testid="stDataFrame"] td {{
            color: #073b4c !important;
            -webkit-text-fill-color: #073b4c !important;
        }}
        [data-testid="stTable"] table,
        [data-testid="stDataFrame"] table {{
            background: rgba(255, 255, 255, 0.88) !important;
            border-radius: 16px !important;
            overflow: hidden;
            border: 1px solid rgba(122, 190, 226, 0.24) !important;
            box-shadow: 0 16px 34px rgba(93, 159, 192, 0.08) !important;
        }}
        [data-testid="stTable"] th,
        [data-testid="stDataFrame"] th {{
            background: linear-gradient(180deg, rgba(182, 227, 246, 0.82) 0%, rgba(163, 217, 241, 0.72) 100%) !important;
            font-weight: 700 !important;
            border-bottom: 1px solid rgba(122, 190, 226, 0.24) !important;
        }}
        [data-testid="stTable"] td,
        [data-testid="stDataFrame"] td {{
            background: rgba(255, 255, 255, 0.94) !important;
            border-bottom: 1px solid rgba(222, 239, 248, 0.95) !important;
        }}
        [data-testid="stDataFrame"] [role="grid"] {{
            border-radius: 20px !important;
            overflow: hidden !important;
            border: 1px solid rgba(122, 190, 226, 0.24) !important;
            box-shadow: 0 16px 34px rgba(93, 159, 192, 0.08) !important;
        }}
        [data-testid="stDataFrame"] [role="row"]:nth-child(even) [role="gridcell"] {{
            background: rgba(246, 252, 255, 0.98) !important;
        }}
        [data-testid="stDataFrame"] [role="row"]:nth-child(odd) [role="gridcell"] {{
            background: rgba(255, 255, 255, 0.94) !important;
        }}
        [data-testid="stDataFrame"] [role="columnheader"] {{
            background: linear-gradient(180deg, rgba(182, 227, 246, 0.82) 0%, rgba(163, 217, 241, 0.72) 100%) !important;
            border-bottom: 1px solid rgba(122, 190, 226, 0.24) !important;
        }}
        [data-testid="stSidebar"] .stButton > button {{
            text-align: left !important;
            justify-content: flex-start !important;
            box-shadow: none !important;
            padding: 0.65rem 1rem !important;
            min-height: 3.2rem !important;
            background: rgba(255, 255, 255, 0.16) !important;
            color: #f3fbff !important;
            margin-bottom: 0.7rem !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: rgba(255, 255, 255, 0.24) !important;
            color: #ffffff !important;
        }}
        [data-testid="stSidebar"] .stButton > button:disabled {{
            background: rgba(255, 255, 255, 0.34) !important;
            color: #ffffff !important;
            opacity: 1 !important;
            font-weight: 700 !important;
            cursor: default !important;
        }}
        [data-testid="stSidebar"] .stButton:last-child > button {{
            justify-content: center !important;
            text-align: center !important;
            background: rgba(255, 255, 255, 0.26) !important;
            font-weight: 800 !important;
            box-shadow: 0 14px 28px rgba(8, 76, 111, 0.18) !important;
        }}
        [data-testid="stSidebar"] .stButton:last-child > button:hover {{
            background: rgba(255, 255, 255, 0.34) !important;
        }}
        .sidebar-logout-block {{
            margin-top: auto;
            padding-top: 1rem;
            padding-bottom: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.18);
            flex-shrink: 0;
        }}
        .sidebar-profile-card {{
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 24px;
            padding: 1rem 1rem 0.95rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 18px 36px rgba(8, 76, 111, 0.16);
        }}
        .sidebar-profile-top {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }}
        .sidebar-profile-avatar {{
            width: 3.2rem;
            height: 3.2rem;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, rgba(255,255,255,0.88) 0%, rgba(214,242,255,0.82) 100%);
            color: #0a5270 !important;
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.55);
        }}
        .sidebar-profile-name {{
            color: #ffffff !important;
            font-size: 1.1rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.2rem;
        }}
        .sidebar-profile-role {{
            color: rgba(244, 252, 255, 0.86) !important;
            font-size: 0.9rem;
        }}
        .sidebar-profile-status {{
            margin-top: 0.85rem;
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.14);
            color: #f6fdff !important;
            font-size: 0.82rem;
            font-weight: 700;
        }}
        .sidebar-profile-dot {{
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 999px;
            background: #8df0b4;
            box-shadow: 0 0 0 4px rgba(141, 240, 180, 0.18);
        }}
        [data-testid="stNumberInputContainer"] {{
            border: 1px solid rgba(122, 190, 226, 0.55) !important;
            border-radius: 14px !important;
            overflow: hidden !important;
            background: rgba(255, 255, 255, 0.94) !important;
            box-shadow: 0 8px 18px rgba(93, 159, 192, 0.08) !important;
        }}
        [data-testid="stNumberInputContainer"]:focus-within {{
            border-color: rgba(91, 178, 218, 0.82) !important;
            box-shadow: 0 0 0 3px rgba(135, 206, 235, 0.22), 0 10px 22px rgba(93, 159, 192, 0.12) !important;
        }}
        [data-testid="stNumberInputContainer"] div[data-baseweb="input"] {{
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            background: transparent !important;
        }}
        [data-testid="stNumberInputContainer"] input {{
            background: transparent !important;
            color: #073b4c !important;
            -webkit-text-fill-color: #073b4c !important;
        }}
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"],
        [data-testid="stNumberInputContainer"] button {{
            background: rgba(135, 206, 235, 0.35) !important;
            color: #0d5f7a !important;
            border: none !important;
            box-shadow: none !important;
        }}
        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        [data-testid="stNumberInputContainer"] button:hover {{
            background: rgba(135, 206, 235, 0.55) !important;
            color: #083f52 !important;
        }}
        .stButton > button, .stFormSubmitButton > button {{
            border-radius: 999px !important;
            border: none !important;
            background: linear-gradient(135deg, #0d8fc7 0%, #43b9ea 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            box-shadow: 0 12px 28px rgba(12, 98, 126, 0.18);
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            background: linear-gradient(135deg, #0b7fb1 0%, #31a8dc 100%) !important;
        }}
        .auth-backdrop {{
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                radial-gradient(circle at 16% 18%, rgba(107,130,255,0.10) 0 2px, transparent 3px),
                radial-gradient(circle at 72% 16%, rgba(107,130,255,0.10) 0 2px, transparent 3px),
                radial-gradient(circle at 82% 62%, rgba(107,130,255,0.08) 0 2px, transparent 3px);
            z-index: 0;
        }}
        .auth-hero-wrap {{
            padding: 4.7rem 1.2rem 1rem 1.2rem;
        }}
        .auth-hero-eyebrow {{
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.84rem;
            font-weight: 700;
            color: #5a78ff !important;
            margin-bottom: 1rem;
        }}
        .auth-hero-title {{
            max-width: 34rem;
            font-size: 4.1rem;
            line-height: 1.02;
            font-weight: 800;
            color: #0c0f18 !important;
            margin-bottom: 1.4rem;
        }}
        .auth-hero-copy {{
            max-width: 34rem;
            font-size: 1.12rem;
            line-height: 1.8;
            color: #28384e !important;
            margin-bottom: 1rem;
        }}
        .auth-hero-link {{
            color: #4762f3 !important;
            font-size: 1.05rem;
            font-weight: 700;
            margin-top: 0.4rem;
        }}
        .auth-illustration {{
            margin-top: 2rem;
            width: 31rem;
            max-width: 100%;
            height: 21rem;
            position: relative;
        }}
        .auth-illustration-orb {{
            position: absolute;
            width: 4.2rem;
            height: 4.2rem;
            border-radius: 999px;
            border: 3px solid rgba(255, 185, 84, 0.55);
            left: 6%;
            top: 6%;
            box-shadow: 0 0 0 10px rgba(255, 185, 84, 0.12);
        }}
        .auth-illustration-card {{
            position: absolute;
            left: 26%;
            top: 30%;
            width: 15rem;
            background: rgba(255,255,255,0.96);
            border-radius: 24px;
            box-shadow: 0 20px 48px rgba(71, 98, 243, 0.14);
            padding: 1rem;
        }}
        .auth-illustration-row {{
            height: 0.95rem;
            border-radius: 999px;
            background: rgba(132, 171, 197, 0.24);
            margin-bottom: 0.85rem;
        }}
        .auth-illustration-row.short {{
            width: 70%;
        }}
        .auth-illustration-row.cta {{
            background: linear-gradient(135deg, #4762f3 0%, #5b8bff 100%);
            width: 78%;
            margin-bottom: 0;
        }}
        .auth-illustration-hill {{
            position: absolute;
            bottom: 0;
            left: 5%;
            width: 80%;
            height: 8.7rem;
            border-radius: 50% 50% 0 0;
            background: linear-gradient(180deg, rgba(74,124,200,0.26) 0%, rgba(67,185,234,0.18) 100%);
        }}
        .auth-illustration-person {{
            position: absolute;
            left: 12%;
            bottom: 0.5rem;
            width: 7rem;
            height: 10rem;
            border-radius: 28px 28px 18px 18px;
            background: linear-gradient(180deg, #ffbe72 0%, #ff9d5e 100%);
            transform: skew(-6deg);
            box-shadow: 0 18px 32px rgba(26, 59, 98, 0.18);
        }}
        .auth-nav-meta {{
            text-align: right;
            color: #0c0f18 !important;
            font-size: 1.05rem;
            margin-top: 1.4rem;
            margin-bottom: 4.2rem;
        }}
        .auth-form-title {{
            font-size: 2.15rem;
            line-height: 1.1;
            font-weight: 800;
            color: #0c0f18 !important;
            margin-bottom: 0.65rem;
        }}
        .auth-form-copy {{
            font-size: 1rem;
            line-height: 1.6;
            color: #6a7689 !important;
            margin-bottom: 1.25rem;
        }}
        .auth-top-gap {{
            height: 2.9rem;
        }}
        [data-testid="stForm"] {{
            padding: 0.35rem 0 0.2rem 0;
            border-radius: 0;
            border: none;
            background: transparent;
        }}
        .auth-note {{
            margin-top: 1.4rem;
            padding: 1rem 1rem;
            border-radius: 16px;
            background: rgba(67, 185, 234, 0.10);
            border: 1px solid rgba(67, 185, 234, 0.18);
            color: #0b5168 !important;
        }}
        .auth-form-divider {{
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 2rem 0 1.3rem 0;
            color: #7a8799 !important;
        }}
        .auth-form-divider::before,
        .auth-form-divider::after {{
            content: "";
            flex: 1;
            height: 1px;
            background: rgba(133, 145, 168, 0.28);
        }}
        .auth-footer-links {{
            margin-top: 4rem;
            font-size: 0.92rem;
            color: #617187 !important;
        }}
        .dashboard-hero {{
            background:
                radial-gradient(circle at top right, rgba(255,255,255,0.58) 0%, transparent 26%),
                linear-gradient(135deg, rgba(165, 219, 241, 0.88) 0%, rgba(118, 203, 239, 0.70) 100%);
            border: 1px solid rgba(122, 190, 226, 0.30);
            border-radius: 30px;
            padding: 1.5rem 1.6rem;
            box-shadow: 0 22px 44px rgba(93, 159, 192, 0.12);
            margin-bottom: 1rem;
        }}
        .dashboard-eyebrow {{
            color: #4c7890 !important;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.82rem;
            font-weight: 800;
            margin-bottom: 0.6rem;
        }}
        .dashboard-title {{
            color: #0b5d79 !important;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.45rem;
        }}
        .dashboard-copy {{
            color: #335f73 !important;
            font-size: 1rem;
            line-height: 1.65;
            max-width: 56rem;
        }}
        .dashboard-stat-card {{
            background: linear-gradient(180deg, rgba(255,255,255,0.82) 0%, rgba(245,252,255,0.94) 100%);
            border: 1px solid rgba(122, 190, 226, 0.22);
            border-radius: 24px;
            padding: 1.1rem 1.15rem;
            box-shadow: 0 18px 36px rgba(93, 159, 192, 0.08);
            min-height: 8.5rem;
        }}
        .dashboard-stat-label {{
            color: #5d7f90 !important;
            font-size: 0.88rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        .dashboard-stat-value {{
            color: #0c5d79 !important;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 0.55rem;
        }}
        .dashboard-stat-meta {{
            color: #456b7e !important;
            font-size: 0.95rem;
            line-height: 1.5;
        }}
        .dashboard-panel {{
            background: linear-gradient(180deg, rgba(255,255,255,0.84) 0%, rgba(245,252,255,0.96) 100%);
            border: 1px solid rgba(122, 190, 226, 0.22);
            border-radius: 26px;
            padding: 1.25rem 1.25rem 1.15rem 1.25rem;
            box-shadow: 0 18px 36px rgba(93, 159, 192, 0.08);
            height: 100%;
        }}
        .dashboard-panel-title {{
            color: #0c5d79 !important;
            font-size: 1.12rem;
            font-weight: 800;
            margin-bottom: 0.85rem;
        }}
        .dashboard-panel-copy {{
            color: #5d7f90 !important;
            font-size: 0.94rem;
            margin-bottom: 0.95rem;
        }}
        .dashboard-summary-highlight {{
            background: rgba(236, 248, 254, 0.92);
            border: 1px solid rgba(122, 190, 226, 0.26);
            border-radius: 20px;
            padding: 1rem 1rem 0.95rem 1rem;
            margin-bottom: 1rem;
        }}
        .dashboard-summary-kicker {{
            color: #6b8a9b !important;
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }}
        .dashboard-summary-value {{
            color: #0c5d79 !important;
            font-size: 1.3rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }}
        .dashboard-summary-meta {{
            color: #456b7e !important;
            font-size: 0.92rem;
            line-height: 1.5;
        }}
        .dashboard-summary-total {{
            color: #6b8a9b !important;
            font-size: 0.84rem;
            font-weight: 700;
            margin-top: 0.45rem;
        }}
        .dashboard-bar-row {{
            margin-bottom: 0.9rem;
        }}
        .dashboard-bar-label {{
            display: flex;
            justify-content: space-between;
            color: #345f73 !important;
            font-size: 0.92rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }}
        .dashboard-bar-track {{
            width: 100%;
            height: 0.72rem;
            border-radius: 999px;
            background: rgba(194, 232, 248, 0.58);
            overflow: hidden;
        }}
        .dashboard-bar-fill {{
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(135deg, #0d8fc7 0%, #43b9ea 100%);
        }}
        .dashboard-activity-item {{
            padding: 0.9rem 0;
            border-bottom: 1px solid rgba(223, 239, 247, 0.95);
        }}
        .dashboard-activity-item:last-child {{
            border-bottom: none;
            padding-bottom: 0;
        }}
        .dashboard-activity-top {{
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.25rem;
        }}
        .dashboard-activity-disease {{
            color: #0c5d79 !important;
            font-size: 0.98rem;
            font-weight: 800;
        }}
        .dashboard-activity-time {{
            color: #6d8a9a !important;
            font-size: 0.86rem;
            white-space: nowrap;
        }}
        .dashboard-activity-result {{
            color: #456b7e !important;
            font-size: 0.94rem;
            line-height: 1.5;
        }}
        .dashboard-empty {{
            background: linear-gradient(180deg, rgba(255,255,255,0.84) 0%, rgba(245,252,255,0.96) 100%);
            border: 1px dashed rgba(122, 190, 226, 0.38);
            border-radius: 26px;
            padding: 1.5rem;
            color: #456b7e !important;
        }}
        .dashboard-section-anchor + div {{
            background: linear-gradient(180deg, rgba(255,255,255,0.84) 0%, rgba(245,252,255,0.96) 100%);
            border: 1px solid rgba(122, 190, 226, 0.22);
            border-radius: 26px;
            padding: 1.25rem 1.25rem 1.1rem 1.25rem;
            box-shadow: 0 18px 36px rgba(93, 159, 192, 0.08);
            height: 100%;
        }}
        .admin-status-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 0.6rem;
        }}
        .admin-status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.55rem 0.9rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.68);
            border: 1px solid rgba(122, 190, 226, 0.20);
            color: #335f73 !important;
            font-size: 0.92rem;
            font-weight: 700;
        }}
        .admin-status-dot {{
            width: 0.58rem;
            height: 0.58rem;
            border-radius: 999px;
            background: #8ddfb1;
            box-shadow: 0 0 0 4px rgba(141, 223, 177, 0.16);
        }}
        .admin-status-dot.off {{
            background: #ff9f9f;
            box-shadow: 0 0 0 4px rgba(255, 159, 159, 0.14);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------- AUTHENTICATION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_user" not in st.session_state:
    st.session_state.chat_user = None

if not st.session_state.logged_in:
    apply_global_styles(auth_screen=True)
    st.markdown('<div class="auth-backdrop"></div>', unsafe_allow_html=True)

    shell_left, shell_right = st.columns([1.45, 1.05], gap="small")

    with shell_left:
        st.markdown(
            """
            <div class="auth-hero-wrap">
                <div class="auth-hero-eyebrow">Disease Prediction Hub</div>
                <div class="auth-hero-title">Welcome to Disease Prediction Hub</div>
                <div class="auth-hero-copy">
                    Here, we believe health screening should feel clear, modern, and supportive from the first step.
                </div>
                <div class="auth-footer-links">About · Terms of Use · Privacy Policy · Copyright Policy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with shell_right:
        nav_spacer, sign_col, reg_col = st.columns([1.1, 1.0, 1.0])
        with sign_col:
            if st.button("Sign in", key="auth_sign_in", use_container_width=True, disabled=st.session_state.auth_mode == "Login"):
                st.session_state.auth_mode = "Login"
                st.rerun()
        with reg_col:
            if st.button("Register", key="auth_register", use_container_width=True, disabled=st.session_state.auth_mode == "Register"):
                st.session_state.auth_mode = "Register"
                st.rerun()

        st.markdown('<div class="auth-top-gap"></div>', unsafe_allow_html=True)

        if st.session_state.auth_mode == "Login":
            st.markdown(
                """
                <div class="auth-form-title">Sign in</div>
                <div class="auth-form-copy">Access your saved predictions and continue from where you left off.</div>
                """,
                unsafe_allow_html=True,
            )
            with st.form("login_form"):
                login_username = st.text_input("Username", key="login_username", placeholder="Enter username")
                login_password = st.text_input("Password", type="password", key="login_password", placeholder="Password")
                login_submit = st.form_submit_button("Sign in", use_container_width=True)

            if login_submit:
                if not login_username.strip() or not login_password:
                    st.error("Enter both username and password.")
                else:
                    verified_user = verify_user(login_username.strip(), login_password)
                    if verified_user:
                        st.session_state.logged_in = True
                        st.session_state.username = verified_user["username"]
                        st.session_state.menu = "Dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        else:
            st.markdown(
                """
                <div class="auth-form-title">Register</div>
                <div class="auth-form-copy">Create your account in a minute and start using the prediction workspace.</div>
                """,
                unsafe_allow_html=True,
            )
            with st.form("register_form"):
                register_username = st.text_input("Create Username", key="register_username", placeholder="Create username")
                register_password = st.text_input("Create Password", type="password", key="register_password", placeholder="Password")
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Confirm password")
                register_submit = st.form_submit_button("Register now", use_container_width=True)

            if register_submit:
                username = register_username.strip()
                if not username or not register_password or not confirm_password:
                    st.error("Complete all registration fields.")
                elif register_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(register_password) < 4:
                    st.error("Password must be at least 4 characters.")
                else:
                    success, message = register(username, register_password)
                    if success:
                        st.success("Registration successful. You can sign in now.")
                        st.session_state.auth_mode = "Login"
                    else:
                        st.error(message)

       
    st.stop()

apply_global_styles(auth_screen=False)

# ---------------- SIDEBAR NAVIGATION ----------------
menu_options = ["Dashboard", "Diabetes", "Heart Disease", "Parkinson's", "Liver Disease", "History", "Chatbot"]
if st.session_state.menu not in menu_options:
    st.session_state.menu = "Dashboard"
profile_name = st.session_state.username.strip() or "User"
profile_parts = [part for part in profile_name.replace("_", " ").split() if part]
profile_initials = "".join(part[0].upper() for part in profile_parts[:2]) or profile_name[:2].upper()

with st.sidebar:
    st.markdown(f"## 👤 **{st.session_state.username}**")
    st.markdown(
        f"""
        <div class="sidebar-profile-card">
            <div class="sidebar-profile-top">
                <div class="sidebar-profile-avatar">{profile_initials}</div>
                <div>
                    <div class="sidebar-profile-name">{profile_name}</div>
                    <div class="sidebar-profile-role">Prediction Workspace</div>
                </div>
            </div>
            <div class="sidebar-profile-status">
                <span class="sidebar-profile-dot"></span>
                Active Session
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("Navigation")
    nav_container = st.container(height=320, border=False)
    with nav_container:
        for option in menu_options:
            is_active = option == st.session_state.menu
            if st.button(option, key=f"nav_{option}", use_container_width=True, disabled=is_active):
                if not is_active:
                    st.session_state.menu = option
                    st.rerun()

    menu = st.session_state.menu
    with st.container():
        st.markdown('<div class="sidebar-logout-block">', unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.menu = "Dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PREDICTION UTILITY ----------------
def send_prediction(endpoint, values, title):
    try:
        payload = {"username": st.session_state.username, "disease": title, "values": values}
        with st.spinner('Accessing Cloud Models...'):
            res = requests.post(f"{BACKEND_URL}/predict/{endpoint}", json=payload)
        
        if res.status_code == 200:
            data = res.json()
            st.markdown("---")
            if data['result']:
                st.error(f"### ⚠️ Result: {data['report']}")
            else:
                st.success(f"### ✅ Result: {data['report']}")
        else:
            st.error(f"Server Error: {res.text}")
    except Exception as e:
        st.error(f"Backend Connection Failed: {e}")


def get_user_history_df(username):
    try:
        res = requests.get(f"{BACKEND_URL}/history?username={username}", timeout=10)
        if res.status_code != 200:
            return pd.DataFrame()

        data = res.json()
        if not data:
            return pd.DataFrame(columns=["age", "disease", "result", "confidence", "timestamp"])

        history_df = pd.DataFrame(data)
        preferred_order = [col for col in ["age", "disease", "result", "confidence", "timestamp"] if col in history_df.columns]
        remaining_cols = [col for col in history_df.columns if col not in preferred_order]
        history_df = history_df[preferred_order + remaining_cols]

        if "timestamp" in history_df.columns:
            history_df["timestamp_dt"] = pd.to_datetime(history_df["timestamp"], errors="coerce")
            history_df = history_df.sort_values(by="timestamp_dt", ascending=False, na_position="last")

        if "confidence" in history_df.columns:
            history_df["confidence"] = pd.to_numeric(history_df["confidence"], errors="coerce")

        return history_df.reset_index(drop=True)
    except Exception:
        return pd.DataFrame()


def ensure_chat_state():
    username = st.session_state.get("username", "there")
    if st.session_state.chat_user != username or not st.session_state.chat_messages:
        st.session_state.chat_user = username
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": f"Hello, {username}! Please choose a question below, or feel free to type your own health inquiry.",
            }
        ]


def send_chat_message(question, disease="general"):
    if not question or not question.strip():
        return

    ensure_chat_state()
    prompt = question.strip()
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    try:
        res = requests.post(
            f"{BACKEND_URL}/chat",
            json={"question": prompt, "disease": disease},
            timeout=30,
        )
        if res.status_code == 200:
            answer = res.json().get("answer", "I'm here to help.")
        else:
            answer = "I'm having trouble responding right now. Please try again in a moment."
    except Exception:
        answer = "The assistant is temporarily unavailable. Please check the backend connection and try again."

    st.session_state.chat_messages.append({"role": "assistant", "content": answer})


def render_chat_history():
    ensure_chat_state()
    chat_blocks = []
    for message in st.session_state.chat_messages:
        role = message["role"]
        safe_text = html.escape(message["content"]).replace("\n", "<br>")
        bubble_class = "chatbot-assistant" if role == "assistant" else "chatbot-user"
        row_class = "chatbot-row-left" if role == "assistant" else "chatbot-row-right"
        chat_blocks.append(
            f'<div class="chatbot-row {row_class}"><div class="chatbot-bubble {bubble_class}">{safe_text}</div></div>'
        )

    st.markdown(
        f"""
        <style>
        .chatbot-layout-anchor + div {{
            background:
                radial-gradient(circle at top right, rgba(255,255,255,0.55) 0%, transparent 22%),
                linear-gradient(180deg, rgba(173, 220, 241, 0.72) 0%, rgba(135, 206, 235, 0.52) 100%);
            border: 1px solid rgba(122, 190, 226, 0.35);
            border-radius: 28px;
            padding: 1.3rem 1.2rem 1.2rem 1.2rem;
            box-shadow: 0 24px 56px rgba(59, 136, 172, 0.18);
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
        }}
        .chatbot-shell {{
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 0;
            box-shadow: none;
            display: flex;
            flex-direction: column;
            flex: 1 1 auto;
            min-height: 0;
        }}
        .chatbot-header {{
            margin-bottom: 0.8rem;
            flex-shrink: 0;
        }}
        .chatbot-title {{
            color: #0b5d79 !important;
            font-size: 1.55rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }}
        .chatbot-subtitle {{
            color: #2f6278 !important;
            font-size: 0.98rem;
            line-height: 1.6;
        }}
        .chatbot-thread {{
            display: flex;
            flex-direction: column-reverse;
            gap: 0.85rem;
            overflow-y: auto;
            padding-right: 0.35rem;
            height: 20rem;
            max-height: 20rem;
        }}
        .chatbot-row {{
            display: flex;
            width: 100%;
        }}
        .chatbot-row-left {{
            justify-content: flex-start;
        }}
        .chatbot-row-right {{
            justify-content: flex-end;
        }}
        .chatbot-bubble {{
            max-width: 76%;
            padding: 1rem 1.1rem;
            border-radius: 20px;
            line-height: 1.72;
            font-size: 1rem;
            white-space: normal;
            word-break: break-word;
            box-shadow: 0 10px 24px rgba(74, 143, 179, 0.12);
        }}
        .chatbot-assistant {{
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.72) 0%, rgba(240, 251, 255, 0.88) 100%);
            color: #114c62 !important;
            border-bottom-left-radius: 10px;
        }}
        .chatbot-user {{
            background: linear-gradient(135deg, rgba(13,143,199,0.2) 0%, rgba(67,185,234,0.34) 100%);
            color: #0a4860 !important;
            border-bottom-right-radius: 10px;
        }}
        .chatbot-quick-label {{
            color: #2f6278 !important;
            font-size: 1.02rem;
            font-weight: 800;
            margin: 0.9rem 0 0.3rem 0;
        }}
        .chatbot-input-label {{
            color: #2f6278 !important;
            font-size: 0.98rem;
            font-weight: 700;
            margin: 0 0 0.45rem 0;
        }}
        .chatbot-helper-text {{
            color: #5d7f90 !important;
            font-size: 0.9rem;
            margin-bottom: 0.6rem;
        }}
        .chatbot-footer-anchor + div {{
            margin-top: 0.35rem;
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.42) 0%, transparent 28%),
                linear-gradient(180deg, rgba(189, 229, 246, 0.56) 0%, rgba(165, 219, 241, 0.42) 100%);
            border: 1px solid rgba(122, 190, 226, 0.28);
            border-radius: 26px;
            padding: 1rem 1rem 1.1rem 1rem;
            box-shadow: 0 16px 34px rgba(59, 136, 172, 0.10);
        }}
        .chatbot-footer-anchor + div .stButton > button {{
            min-height: 3.25rem !important;
            border-radius: 20px !important;
            padding: 0.75rem 0.9rem !important;
            background: linear-gradient(135deg, rgba(13,143,199,0.95) 0%, rgba(67,185,234,0.95) 100%) !important;
            box-shadow: 0 14px 28px rgba(20, 122, 159, 0.16) !important;
        }}
        .chatbot-footer-anchor + div .stButton > button:hover {{
            background: linear-gradient(135deg, rgba(11,127,177,0.96) 0%, rgba(49,168,220,0.96) 100%) !important;
        }}
        .chatbot-footer-anchor + div .stButton > button p {{
            white-space: normal !important;
            line-height: 1.35 !important;
            font-size: 0.96rem !important;
            text-align: center !important;
        }}
        .chatbot-footer-anchor + div .stForm {{
            margin-top: 0.1rem;
        }}
        .chatbot-footer-anchor + div .stFormSubmitButton > button {{
            min-height: 3.5rem !important;
        }}
        .chatbot-footer-anchor + div [data-testid="stHorizontalBlock"] {{
            align-items: end;
        }}
        .chatbot-footer-anchor + div div[data-baseweb="input"],
        .chatbot-footer-anchor + div div[data-baseweb="base-input"] {{
            background: rgba(255, 255, 255, 0.96) !important;
            border: 1px solid rgba(137, 202, 230, 0.55) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.65), 0 8px 18px rgba(93, 159, 192, 0.08) !important;
        }}
        .chatbot-footer-anchor + div div[data-baseweb="input"]:focus-within,
        .chatbot-footer-anchor + div div[data-baseweb="base-input"]:focus-within {{
            border-color: rgba(91, 178, 218, 0.8) !important;
            box-shadow: 0 0 0 3px rgba(135, 206, 235, 0.22), 0 10px 22px rgba(93, 159, 192, 0.12) !important;
        }}
        </style>
        <div class="chatbot-shell">
            <div class="chatbot-header">
                <div class="chatbot-title">Health Assistant Chat</div>
                <div class="chatbot-subtitle">Ask about healthy habits, prevention tips, symptoms, and everyday wellness guidance.</div>
            </div>
            <div class="chatbot-thread">
                {''.join(reversed(chat_blocks))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def scroll_chat_to_bottom():
    components.html(
        """
        <script>
        const scrollChat = () => {
            const chatThreads = window.parent.document.querySelectorAll('.chatbot-thread');
            if (!chatThreads.length) return;
            const thread = chatThreads[chatThreads.length - 1];
            thread.scrollTop = thread.scrollHeight;
        };
        window.parent.requestAnimationFrame(() => {
            scrollChat();
            setTimeout(scrollChat, 120);
        });
        </script>
        """,
        height=0,
    )


def render_history_table(history_df):
    if history_df.empty:
        return

    display_df = history_df.copy()
    if "age" in display_df.columns:
        display_df["age"] = display_df["age"].apply(
            lambda value: "N/A" if pd.isna(value) else str(int(value)) if float(value).is_integer() else f"{float(value):.2f}"
        )
    if "confidence" in display_df.columns:
        display_df["confidence"] = display_df["confidence"].apply(
            lambda value: "N/A" if pd.isna(value) else f"{float(value):.2f}%"
        )
    display_df = display_df.fillna("N/A")

    header_html = "".join(
        f"<th>{html.escape(str(col).replace('_', ' ').title())}</th>"
        for col in display_df.columns
    )

    row_html = []
    for _, row in display_df.iterrows():
        cells = "".join(f"<td>{html.escape(str(value))}</td>" for value in row.tolist())
        row_html.append(f"<tr>{cells}</tr>")

    st.markdown(
        f"""
        <style>
        .history-table-card {{
            background: linear-gradient(180deg, rgba(255,255,255,0.82) 0%, rgba(245,252,255,0.92) 100%);
            border: 1px solid rgba(122, 190, 226, 0.26);
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 18px 36px rgba(93, 159, 192, 0.10);
        }}
        .history-table-wrap {{
            overflow-x: auto;
        }}
        .history-table {{
            width: 100%;
            border-collapse: collapse;
            color: #073b4c;
            min-width: 760px;
        }}
        .history-table thead th {{
            background: linear-gradient(180deg, rgba(184, 228, 246, 0.92) 0%, rgba(168, 219, 241, 0.82) 100%);
            color: #0c5d79;
            text-align: left;
            font-weight: 800;
            font-size: 0.98rem;
            padding: 1rem 1.05rem;
            border-bottom: 1px solid rgba(122, 190, 226, 0.24);
        }}
        .history-table tbody td {{
            padding: 0.95rem 1.05rem;
            border-bottom: 1px solid rgba(224, 239, 248, 0.95);
            font-size: 0.97rem;
        }}
        .history-table tbody tr:nth-child(odd) td {{
            background: rgba(255, 255, 255, 0.92);
        }}
        .history-table tbody tr:nth-child(even) td {{
            background: rgba(246, 252, 255, 0.98);
        }}
        .history-table tbody tr:hover td {{
            background: rgba(223, 243, 251, 0.88);
        }}
        </style>
        <div class="history-table-card">
            <div class="history-table-wrap">
                <table class="history-table">
                    <thead>
                        <tr>{header_html}</tr>
                    </thead>
                    <tbody>
                        {''.join(row_html)}
                    </tbody>
                </table>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def classify_prediction_result(result_text):
    text = str(result_text).strip().lower()
    negative_terms = {"not diabetic", "normal heart", "healthy liver", "healthy"}
    return "Negative" if text in negative_terms else "Positive"


def build_dashboard_breakdown_html(df, label_col, highlight_title):
    if df.empty:
        return ""

    highlight_row = df.sort_values(by=["Count", "Percent"], ascending=[False, False]).iloc[0]
    total_count = int(df["Count"].sum())

    rows = []
    for _, row in df.iterrows():
        label = html.escape(str(row[label_col]))
        count = int(row["Count"])
        percent = float(row["Percent"])
        fill_width = 0 if count == 0 else max(percent, 8)
        rows.append(
            (
                '<div class="dashboard-bar-row">'
                '<div class="dashboard-bar-label">'
                f"<span>{label}</span>"
                f"<span>{count} | {percent:.1f}%</span>"
                "</div>"
                '<div class="dashboard-bar-track">'
                f'<div class="dashboard-bar-fill" style="width: {fill_width:.1f}%;"></div>'
                "</div>"
                "</div>"
            )
        )

    return (
        '<div class="dashboard-summary-highlight">'
        f'<div class="dashboard-summary-kicker">{html.escape(highlight_title)}</div>'
        f'<div class="dashboard-summary-value">{html.escape(str(highlight_row[label_col]))}</div>'
        f'<div class="dashboard-summary-meta">{int(highlight_row["Count"])} records | {float(highlight_row["Percent"]):.1f}% share</div>'
        f'<div class="dashboard-summary-total">Total tracked: {total_count}</div>'
        "</div>"
        + "".join(rows)
    )


def render_dashboard(history_df):
    username = html.escape(st.session_state.username or "User")
    total_predictions = int(len(history_df))
    unique_diseases = int(history_df["disease"].nunique()) if "disease" in history_df.columns and not history_df.empty else 0
    avg_confidence = (
        float(history_df["confidence"].dropna().mean())
        if "confidence" in history_df.columns and history_df["confidence"].notna().any()
        else None
    )

    latest_disease = "No activity yet"
    latest_time = "No recent timestamp"

    if not history_df.empty:
        first_row = history_df.iloc[0]
        latest_disease = str(first_row.get("disease", "Recent prediction"))
        latest_time = str(first_row.get("timestamp", ""))

    st.markdown(
        f"""
        <div class="dashboard-hero">
            <div class="dashboard-eyebrow">Prediction Overview</div>
            <div class="dashboard-title">Welcome back, {username}</div>
            <div class="dashboard-copy">
                Track your recent screening activity, review prediction patterns, and jump back into the diseases you monitor most often.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    card_cols = st.columns(4, gap="medium")
    card_data = [
        ("Total Predictions", str(total_predictions), "All predictions saved in your workspace."),
        ("Tracked Categories", str(unique_diseases), "Different disease modules used so far."),
        ("Average Confidence", f"{avg_confidence:.1f}%" if avg_confidence is not None else "N/A", "Available for recent predictions."),
        ("Latest Module", latest_disease, latest_time or "Recent activity"),
    ]
    for col, (label, value, meta) in zip(card_cols, card_data):
        with col:
            st.markdown(
                f'<div class="dashboard-stat-card"><div class="dashboard-stat-label">{html.escape(label)}</div><div class="dashboard-stat-value">{html.escape(value)}</div><div class="dashboard-stat-meta">{html.escape(meta)}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("")
    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown('<div class="dashboard-section-anchor"></div>', unsafe_allow_html=True)
        with st.container(border=False):
            st.markdown('<div class="dashboard-panel-title">Disease Distribution</div>', unsafe_allow_html=True)
            st.markdown('<div class="dashboard-panel-copy">See how your saved predictions are distributed across disease modules.</div>', unsafe_allow_html=True)
            if history_df.empty or "disease" not in history_df.columns:
                st.markdown(
                    """
                    <div class="dashboard-empty">
                        <strong>No prediction activity yet.</strong><br>
                        Run a disease check to populate your dashboard with trends and recent results.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                distribution_df = history_df["disease"].value_counts().reset_index()
                distribution_df.columns = ["Disease", "Count"]
                distribution_df["Percent"] = (
                    (distribution_df["Count"] / distribution_df["Count"].sum()) * 100
                ).round(1)
                distribution_summary_html = build_dashboard_breakdown_html(
                    distribution_df,
                    "Disease",
                    "Most used module",
                )
                donut_chart = (
                    alt.Chart(distribution_df)
                    .mark_arc(innerRadius=58, outerRadius=98)
                    .encode(
                        theta=alt.Theta("Count:Q"),
                        color=alt.Color(
                            "Disease:N",
                            scale=alt.Scale(range=["#0d8fc7", "#43b9ea", "#77d3ef", "#9edff5", "#5aaed2"]),
                            legend=None,
                        ),
                        tooltip=[
                            alt.Tooltip("Disease:N", title="Disease"),
                            alt.Tooltip("Count:Q", title="Predictions"),
                            alt.Tooltip("Percent:Q", title="Share (%)"),
                        ],
                    )
                    .properties(width=250, height=250, background="transparent")
                    .configure_view(strokeOpacity=0)
                    .configure(background="transparent")
                )
                chart_col, summary_col = st.columns([1.1, 0.9], gap="medium")
                with chart_col:
                    st.altair_chart(donut_chart, use_container_width=False)
                with summary_col:
                    st.markdown(distribution_summary_html, unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="dashboard-section-anchor"></div>', unsafe_allow_html=True)
        with st.container(border=False):
            st.markdown('<div class="dashboard-panel-title">Risk By Age</div>', unsafe_allow_html=True)
            st.markdown('<div class="dashboard-panel-copy">Positive-risk predictions grouped into young, middle, and old age ranges.</div>', unsafe_allow_html=True)
            age_risk_df = pd.DataFrame()
            if not history_df.empty and "age" in history_df.columns and "result" in history_df.columns:
                age_risk_df = history_df.copy()
                age_risk_df["status_label"] = age_risk_df["result"].apply(classify_prediction_result)
                age_risk_df = age_risk_df[age_risk_df["status_label"] == "Positive"].copy()
                age_risk_df["age"] = pd.to_numeric(age_risk_df["age"], errors="coerce")
                age_risk_df = age_risk_df.dropna(subset=["age"])
                age_risk_df = age_risk_df[(age_risk_df["age"] > 0) & (age_risk_df["age"] <= 100)]
                if not age_risk_df.empty:
                    age_risk_df["age"] = age_risk_df["age"].round().astype(int)
                    age_risk_df["Age Range"] = pd.cut(
                        age_risk_df["age"],
                        bins=[0, 25, 50, 100],
                        labels=["Young (0-25)", "Middle (26-50)", "Old (51-100)"],
                        include_lowest=True,
                    )
                    age_risk_df = (
                        age_risk_df.groupby("Age Range", observed=False)
                        .size()
                        .reset_index(name="Count")
                    )
                    age_risk_df["Percent"] = (
                        (age_risk_df["Count"] / age_risk_df["Count"].sum()) * 100
                    ).round(1)

            if age_risk_df.empty:
                st.markdown('<div class="dashboard-empty">Positive-risk age data will appear here once you have saved age-based risk cases.</div>', unsafe_allow_html=True)
            else:
                age_summary_html = build_dashboard_breakdown_html(
                    age_risk_df,
                    "Age Range",
                    "Highest-risk age range",
                )
                age_chart = (
                    alt.Chart(age_risk_df)
                    .mark_arc(outerRadius=92)
                    .encode(
                        theta=alt.Theta("Count:Q", title="Positive-risk predictions"),
                        color=alt.Color(
                            "Age Range:N",
                            scale=alt.Scale(range=["#0d8fc7", "#43b9ea", "#9edff5"]),
                            legend=None,
                        ),
                        tooltip=[
                            alt.Tooltip("Age Range:N", title="Age Range"),
                            alt.Tooltip("Count:Q", title="Positive-risk predictions"),
                            alt.Tooltip("Percent:Q", title="Share (%)"),
                        ],
                    )
                    .properties(width=240, height=240, background="transparent")
                    .configure_view(strokeOpacity=0)
                    .configure(background="transparent")
                )
                chart_col, summary_col = st.columns([1.05, 0.95], gap="medium")
                with chart_col:
                    st.altair_chart(age_chart, use_container_width=False)
                with summary_col:
                    st.markdown(age_summary_html, unsafe_allow_html=True)

    st.markdown("")
    quick_actions = [
        ("Diabetes", "Open Diabetes"),
        ("Heart Disease", "Open Heart"),
        ("Parkinson's", "Open Parkinson's"),
        ("Liver Disease", "Open Liver"),
        ("History", "Open History"),
    ]
    for row_start in range(0, len(quick_actions), 2):
        action_row = quick_actions[row_start:row_start + 2]
        quick_cols = st.columns(2)
        for col, (target, label) in zip(quick_cols, action_row):
            with col:
                if st.button(label, key=f"dash_{target}", use_container_width=True):
                    st.session_state.menu = target
                    st.rerun()

# ---------------- PAGE LOGIC ----------------

if menu == "Dashboard":
    history_df = get_user_history_df(st.session_state.username)
    render_dashboard(history_df)

elif menu == "Diabetes":
    st.title("🩸 Advanced Diabetes Risk Assessment")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", 1, 120, 30)
        sex = 1 if st.selectbox("Sex", ["Male", "Female"]) == "Male" else 0
        bmi = st.number_input("BMI", 10.0, 70.0, 25.0)
        preg = st.number_input("Pregnancies", 0, 20, 0)
    with c2:
        sys_bp = st.number_input("Systolic BP", 50, 250, 120)
        dia_bp = st.number_input("Diastolic BP", 30, 150, 80)
        glu = st.number_input("Fasting Glucose", 50.0, 400.0, 100.0)
        hba1c = st.number_input("HbA1c (%)", 3.0, 15.0, 5.5)
        ins = st.number_input("Insulin", 0, 900, 80)
    with c3:
        skin = st.number_input("Skin Thickness", 0.0, 100.0, 20.0)
        fam = 1 if st.selectbox("Family History?", ["Yes", "No"]) == "Yes" else 0
        act = st.number_input("Activity (min/week)", 0, 1000, 150)
        diet = st.slider("Diet Score", 0.0, 10.0, 5.0)
        smoke = 1 if st.selectbox("Smoker?", ["Yes", "No"]) == "Yes" else 0

    if st.button("Analyze Diabetes Risk", use_container_width=True):
        feats = [age, sex, bmi, sys_bp, dia_bp, glu, hba1c, ins, skin, preg, fam, act, diet, smoke]
        send_prediction("diabetes", feats, "Diabetes")

elif menu == "Heart Disease":
    st.title("🫀 Heart Disease Prediction")
    c1, c2, c3 = st.columns(3)
    with c1:
        age = c1.number_input("Age", 1, 120, 50)
        sex = 1 if c2.selectbox("Sex", ["Male", "Female"]) == "Male" else 0
        cp = c3.selectbox("Chest Pain Type", [0, 1, 2, 3])
        rbp = c1.number_input("Resting BP", 50, 200, 120)
    with c2:
        chol = c2.number_input("Cholesterol", 100, 600, 200)
        fbs = c3.selectbox("Fasting BS > 120", [0, 1])
        ecg = c1.selectbox("Rest ECG", [0, 1, 2])
        mhr = c2.number_input("Max Heart Rate", 60, 220, 150)
    with c3:
        exang = c3.selectbox("Exercise Angina", [0, 1])
        oldp = c1.number_input("Oldpeak", 0.0, 10.0, 1.0)
        slope = c2.selectbox("Slope", [0, 1, 2])
        ca = c3.selectbox("Major Vessels", [0, 1, 2, 3])
        thal = st.selectbox("Thal", [0, 1, 2, 3])

    if st.button("Analyze Heart Risk", use_container_width=True):
        feats = [age, sex, cp, rbp, chol, fbs, ecg, mhr, exang, oldp, slope, ca, thal]
        send_prediction("heart", feats, "Heart Disease")

elif menu == "Parkinson's":
    st.title("🧠 Parkinson's Detection")
    st.info(
        "Enter values from a voice analysis report. These inputs are acoustic measurements "
        "from a sustained voice recording, not general symptoms like tremor or age."
    )
    with st.expander("What do these Parkinson's inputs mean?"):
        st.markdown(
            """
            - `Average Vocal Frequency (Fo)`: the usual pitch of the recorded voice in hertz.
            - `Highest Vocal Frequency (Fhi)`: the highest measured pitch in the sample.
            - `Lowest Vocal Frequency (Flo)`: the lowest measured pitch in the sample.
            - `Jitter (%)`: how much the pitch changes from cycle to cycle.
            - `Shimmer`: how much the loudness changes from cycle to cycle.
            - `Shimmer (dB)`: the same loudness variation measured in decibels.
            - `NHR`: noise-to-harmonics ratio, which reflects breathiness or noise in the voice.
            - `HNR`: harmonics-to-noise ratio, which reflects voice clarity.
            - `RPDE`: a voice irregularity measure used in Parkinson's voice analysis.
            - `PPE`: a pitch instability measure used in Parkinson's voice analysis.
            """
        )
        st.caption(
            "If you do not have a voice analysis report, these numbers are usually generated "
            "by speech-analysis tools such as Praat."
        )
    c1, c2 = st.columns(2)
    with c1:
        fo = st.number_input(
            "Average Vocal Frequency, Fo (Hz)",
            value=119.99,
            help="Typical pitch of the recorded voice sample.",
        )
        fhi = st.number_input(
            "Highest Vocal Frequency, Fhi (Hz)",
            value=157.30,
            help="Highest pitch measured in the voice sample.",
        )
        flo = st.number_input(
            "Lowest Vocal Frequency, Flo (Hz)",
            value=74.99,
            help="Lowest pitch measured in the voice sample.",
        )
        jit = st.number_input(
            "Jitter (%)",
            value=0.0078,
            help="Small cycle-to-cycle changes in pitch frequency.",
        )
        shim = st.number_input(
            "Shimmer",
            value=0.043,
            help="Small cycle-to-cycle changes in loudness.",
        )
    with c2:
        shdb = st.number_input(
            "Shimmer (dB)",
            value=0.426,
            help="Voice loudness variation measured in decibels.",
        )
        nhr = st.number_input(
            "Noise-to-Harmonics Ratio (NHR)",
            value=0.022,
            help="Higher values can indicate more noise in the voice signal.",
        )
        hnr = st.number_input(
            "Harmonics-to-Noise Ratio (HNR)",
            value=21.03,
            help="Higher values usually indicate a clearer, more regular voice signal.",
        )
        rpde = st.number_input(
            "Voice Irregularity (RPDE)",
            value=0.414,
            help="Recurrence Period Density Entropy, a measure of voice irregularity.",
        )
        ppe = st.number_input(
            "Pitch Instability (PPE)",
            value=0.284,
            help="Pitch Period Entropy, a measure of pitch instability.",
        )

    baseline_parkinsons_values = {
        "jita": 0.00007,
        "rap": 0.0037,
        "ppq": 0.0055,
        "ddp": 0.011,
        "apq3": 0.021,
        "apq5": 0.031,
        "apq": 0.029,
        "dda": 0.065,
        "dfa": 0.815,
        "s1": -4.81,
        "s2": 0.266,
        "d2": 2.30,
    }

    if st.button("Analyze Parkinson's Risk", use_container_width=True):
        feats = [
            fo,
            fhi,
            flo,
            jit,
            baseline_parkinsons_values["jita"],
            baseline_parkinsons_values["rap"],
            baseline_parkinsons_values["ppq"],
            baseline_parkinsons_values["ddp"],
            shim,
            shdb,
            baseline_parkinsons_values["apq3"],
            baseline_parkinsons_values["apq5"],
            baseline_parkinsons_values["apq"],
            baseline_parkinsons_values["dda"],
            nhr,
            hnr,
            rpde,
            baseline_parkinsons_values["dfa"],
            baseline_parkinsons_values["s1"],
            baseline_parkinsons_values["s2"],
            baseline_parkinsons_values["d2"],
            ppe,
        ]
        send_prediction("parkinsons", feats, "Parkinson's")

elif menu == "Liver Disease":
    st.title("🧪 Liver Disease Prediction")
    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", 1, 100, 30)
        sex = 1 if st.selectbox("Gender", ["Male", "Female"]) == "Male" else 0
        tb = st.number_input("Total Bilirubin", 0.1, 80.0, 1.0)
        db = st.number_input("Direct Bilirubin", 0.1, 40.0, 0.5)
    with c2:
        alp = st.number_input("Alkaline Phosphatase", 10, 3000, 150)
        alt = st.number_input("ALT", 10, 2500, 40)
        ast = st.number_input("AST", 10, 5000, 40)
    with c3:
        tp = st.number_input("Total Proteins", 1.0, 10.0, 6.0)
        alb = st.number_input("Albumin", 0.5, 6.0, 3.0)
        ag = st.number_input("A/G Ratio", 0.1, 3.0, 1.0)

    if st.button("Analyze Liver Risk", use_container_width=True):
        feats = [age, sex, tb, db, alp, alt, ast, tp, alb, ag]
        send_prediction("liver", feats, "Liver Disease")

elif menu == "History":
    st.title("📜 Patient Prediction History")
    history_df = get_user_history_df(st.session_state.username)
    if not history_df.empty:
        render_history_table(history_df.drop(columns=["timestamp_dt"], errors="ignore"))
    else:
        st.info("No prediction history found for this account.")

elif menu == "Chatbot":
    ensure_chat_state()
    st.markdown("## AI Health Assistant")
    st.markdown('<div class="chatbot-layout-anchor"></div>', unsafe_allow_html=True)
    with st.container(border=False):
        render_chat_history()
        scroll_chat_to_bottom()

        st.markdown('<div class="chatbot-footer-anchor"></div>', unsafe_allow_html=True)
        with st.container(border=False):
            st.markdown('<div class="chatbot-quick-label">Quick prompts</div>', unsafe_allow_html=True)
            st.markdown('<div class="chatbot-helper-text">Tap one of these suggestions or type your own question below.</div>', unsafe_allow_html=True)
            quick_cols = st.columns(3)
            quick_prompts = [
                "Reduce diabetes risk naturally",
                "Heart health prevention tips",
                "Habits that support liver health",
            ]
            for col, prompt in zip(quick_cols, quick_prompts):
                with col:
                    if st.button(prompt, key=f"quick_{prompt}", use_container_width=True):
                        send_chat_message(prompt, "general")
                        st.rerun()

            st.markdown('<div class="chatbot-input-label">Type your question</div>', unsafe_allow_html=True)
            with st.form("chatbot_form", clear_on_submit=True):
                input_col, send_col = st.columns([6, 1.4])
                with input_col:
                    q = st.text_input("Ask the assistant", placeholder="Type here...", label_visibility="collapsed")
                with send_col:
                    submitted = st.form_submit_button("Send", use_container_width=True)

    if submitted:
        send_chat_message(q, "general")
        st.rerun()

elif menu == "__legacy_chatbot__":
    st.title("💬 AI Health Assistant")
    q = st.text_area("How can I help you today?")
    if st.button("Ask Assistant"):
        res = requests.post(f"{BACKEND_URL}/chat", json={"question": q, "disease": "general"})
        if res.status_code == 200:
            st.info(res.json()["answer"])
