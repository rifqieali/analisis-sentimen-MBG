"""
Modul Desain UI & Estetika Minimalist (Clean Monochrome & Muted Pastels) untuk Streamlit
"""

import streamlit as st
import matplotlib.pyplot as plt

def inject_custom_css():
    """
    Menyuntikkan CSS kustom dengan desain Minimalist UI:
    warm monochrome palette, flat bento grids, muted pastels, tipografi editorial,
    tanpa gradient warna-warni dan tanpa drop shadow tebal.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #18181B;
    }

    /* Main Container */
    .block-container {
        padding-top: 1.75rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Minimalist Hero Banner */
    .hero-banner {
        background: #FFFFFF;
        border: 1px solid #E4E4E7;
        border-radius: 12px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: none;
    }

    .hero-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #18181B !important;
        letter-spacing: -0.03em;
        margin: 0 0 8px 0;
        line-height: 1.25;
    }

    .hero-subtitle {
        font-size: 0.92rem;
        color: #71717A;
        margin-bottom: 16px;
        line-height: 1.5;
    }

    /* Minimalist Badges */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-top: 12px;
    }

    .badge-item {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        background: #F4F4F5;
        color: #3F3F46;
        border: 1px solid #E4E4E7;
    }

    .badge-haki {
        background: #F0FDF4;
        color: #166534;
        border: 1px solid #DCFCE7;
    }

    .badge-unnes {
        background: #F8FAFC;
        color: #334155;
        border: 1px solid #E2E8F0;
    }

    .badge-model {
        background: #F4F4F5;
        color: #18181B;
        border: 1px solid #E4E4E7;
    }

    /* Flat Bento Grid */
    .metric-grid-4 {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        margin: 16px 0 24px 0;
    }

    .metric-card-pro {
        background: #FFFFFF;
        border: 1px solid #E4E4E7;
        border-radius: 10px;
        padding: 16px 18px;
        text-align: left;
        box-shadow: none;
        transition: border-color 0.15s ease;
    }

    .metric-card-pro:hover {
        border-color: #A1A1AA;
    }

    .metric-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 700;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }

    .metric-txt {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
        color: #71717A;
    }

    /* Muted Text Colors */
    .txt-emerald { color: #2D6A4F; }
    .txt-rose { color: #A63D40; }
    .txt-indigo { color: #334155; }
    .txt-amber { color: #B45309; }

    /* Form & Input Styling */
    .stTextArea textarea {
        border-radius: 8px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 12px 14px !important;
        border: 1px solid #E4E4E7 !important;
        background-color: #FFFFFF !important;
        box-shadow: none !important;
    }

    .stTextArea textarea:focus {
        border-color: #18181B !important;
        box-shadow: none !important;
    }

    /* Minimalist Buttons */
    .stButton button, .stDownloadButton button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 8px 18px !important;
        border: 1px solid #D4D4D8 !important;
        background: #FFFFFF !important;
        color: #18181B !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }

    .stButton button:hover, .stDownloadButton button:hover {
        background: #18181B !important;
        color: #FFFFFF !important;
        border-color: #18181B !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* Minimalist Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #E4E4E7;
        padding-bottom: 0px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #71717A;
    }

    .stTabs [aria-selected="true"] {
        color: #18181B !important;
        border-bottom-color: #18181B !important;
    }

    /* Sidebar Footer Info */
    .sidebar-haki-box {
        background: #F4F4F5;
        border: 1px solid #E4E4E7;
        border-radius: 8px;
        padding: 12px 14px;
        margin-top: 20px;
    }

    .sidebar-haki-title {
        font-size: 0.74rem;
        font-weight: 700;
        color: #27272A;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }

    .sidebar-haki-text {
        font-size: 0.76rem;
        color: #52525B;
        line-height: 1.45;
    }
    </style>
    """, unsafe_allow_html=True)


def render_hero_banner(title: str, subtitle: str, is_demo: bool = False):
    """
    Renders an editorial minimalist hero banner without emojis.
    """
    demo_badge = '<span class="badge-item badge-model">Demo Real-Time</span>' if is_demo else '<span class="badge-item badge-model">Pipeline Skripsi</span>'
    
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
        <div class="badge-container">
            <span class="badge-item badge-haki">HAKI No. 001265752</span>
            <span class="badge-item badge-unnes">Universitas Negeri Semarang</span>
            {demo_badge}
            <span class="badge-item badge-model">MultinomialNB & LinearSVC</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_haki():
    """
    Displays HAKI credentials cleanly in the sidebar without emojis.
    """
    st.sidebar.markdown("""
    <div class="sidebar-haki-box">
        <div class="sidebar-haki-title">Surat Pencatatan Ciptaan</div>
        <div class="sidebar-haki-text">
            <b>No. HAKI:</b> 001265752<br>
            <b>EC:</b> EC002026079870<br>
            <b>Pencipta:</b> Rifqie Alimul Haq, Dr. Nur Iksan, S.T., M.Kom., Dr. Djuniadi, M.T.<br>
            <b>Pemegang:</b> Universitas Negeri Semarang
        </div>
    </div>
    """, unsafe_allow_html=True)


def apply_matplotlib_style():
    """
    Sets clean minimalist styling for Matplotlib plots.
    """
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Plus Jakarta Sans', 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.edgecolor'] = '#E4E4E7'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['grid.color'] = '#F4F4F5'
    plt.rcParams['grid.linestyle'] = '-'
    plt.rcParams['grid.alpha'] = 1.0
