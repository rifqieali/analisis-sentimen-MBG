"""
Modul Desain UI & Estetika Premium untuk Streamlit
"""

import streamlit as st
import matplotlib.pyplot as plt

def inject_custom_css():
    """
    Menyuntikkan CSS kustom dengan desain modern, mikro-animasi, glassmorphism,
    dan tipografi premium (Plus Jakarta Sans & JetBrains Mono).
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    /* Header Banner Premium */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.97) 0%, rgba(15, 23, 42, 0.98) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 32px 38px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
    }

    .hero-banner::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #6366F1, #10B981, #F59E0B, #EC4899);
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        color: #F8FAFC !important;
        letter-spacing: -0.5px;
        margin: 0 0 10px 0;
        line-height: 1.25;
    }

    .hero-subtitle {
        font-size: 0.98rem;
        color: #94A3B8;
        margin-bottom: 16px;
        line-height: 1.5;
    }

    /* Badges */
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
        gap: 6px;
        padding: 5px 12px;
        border-radius: 50px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        backdrop-filter: blur(4px);
    }

    .badge-haki {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }

    .badge-unnes {
        background: rgba(99, 102, 241, 0.15);
        color: #818CF8;
        border: 1px solid rgba(129, 140, 248, 0.3);
    }

    .badge-model {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }

    /* Metric Cards Grid */
    .metric-grid-4 {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 14px;
        margin: 18px 0 24px 0;
    }

    .metric-card-pro {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 14px;
        padding: 18px 22px;
        text-align: center;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .metric-card-pro:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.15);
        border-color: rgba(99, 102, 241, 0.4);
    }

    .metric-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.2;
    }

    .metric-txt {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 6px;
        opacity: 0.75;
    }

    /* Custom Color Text */
    .txt-emerald { color: #10B981; }
    .txt-rose { color: #EF4444; }
    .txt-indigo { color: #6366F1; }
    .txt-amber { color: #F59E0B; }

    /* Custom Form & Text Area Styling */
    .stTextArea textarea {
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.92rem !important;
        padding: 14px 16px !important;
        border: 1px solid rgba(128, 128, 128, 0.25) !important;
        transition: all 0.2s ease !important;
    }

    .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }

    /* Custom Buttons */
    .stButton button, .stDownloadButton button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 8px 20px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
    }

    .stButton button:hover, .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px -4px rgba(99, 102, 241, 0.3) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid rgba(128, 128, 128, 0.15);
        padding-bottom: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* Sidebar Footer Info */
    .sidebar-haki-box {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 20px;
    }

    .sidebar-haki-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #10B981;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }

    .sidebar-haki-text {
        font-size: 0.78rem;
        opacity: 0.85;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)


def render_hero_banner(title: str, subtitle: str, is_demo: bool = False):
    """
    Renders a stunning modern hero banner with badges.
    """
    demo_badge = '<span class="badge-item badge-model">⚡ DEMO REAL-TIME</span>' if is_demo else '<span class="badge-item badge-model">🔬 PIPELINE SKRIPSI</span>'
    
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
        <div class="badge-container">
            <span class="badge-item badge-haki">📜 HAKI No. 001265752</span>
            <span class="badge-item badge-unnes">🎓 Universitas Negeri Semarang</span>
            {demo_badge}
            <span class="badge-item badge-model">🤖 MultinomialNB vs LinearSVC</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_haki():
    """
    Displays HAKI credentials cleanly in the sidebar.
    """
    st.sidebar.markdown("""
    <div class="sidebar-haki-box">
        <div class="sidebar-haki-title">📜 Surat Pencatatan Ciptaan</div>
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
    Sets clean modern styling for Matplotlib plots.
    """
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Plus Jakarta Sans', 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.edgecolor'] = '#CCCCCC'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['grid.color'] = '#EEEEEE'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.7
