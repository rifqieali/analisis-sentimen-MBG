"""
Modul Desain UI & Estetika Industrial Brutalist (Swiss Print + Technical Research Terminal) untuk Streamlit
"""

import streamlit as st
import matplotlib.pyplot as plt

def inject_custom_css():
    """
    Menyuntikkan CSS kustom Industrial Brutalist:
    - Rigid geometric grids, sharp rectangular panels (0-2px border-radius)
    - Swiss Grotesk (Space Grotesk) & Technical Monospace (JetBrains Mono)
    - Dark tactical slate/charcoal (#0C0E14, #131722)
    - Utilitarian high-contrast accents (Phosphor Green #00E676, Amber #FF9100, Cyber Cyan #00D2FF, Crimson #FF334B)
    - Bracketed notation, technical data readouts, precision telemetry styling
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #E2E8F0;
    }

    /* Main Viewport Container */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1280px;
    }

    /* Industrial Terminal Hero Banner */
    .hero-banner {
        background: #11141E;
        border: 1px solid #262B38;
        border-top: 2px solid #00E676;
        border-radius: 2px;
        padding: 24px 28px;
        margin-bottom: 20px;
        position: relative;
    }

    .hero-sys-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        color: #00E676;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .hero-sys-tag::before {
        content: '';
        display: inline-block;
        width: 7px;
        height: 7px;
        background: #00E676;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.85rem;
        font-weight: 700;
        color: #F8FAFC !important;
        letter-spacing: -0.03em;
        margin: 0 0 8px 0;
        line-height: 1.2;
        text-transform: uppercase;
    }

    .hero-subtitle {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.9rem;
        color: #94A3B8;
        margin-bottom: 16px;
        line-height: 1.5;
    }

    /* Technical Rectangular Badges */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-top: 12px;
    }

    .badge-item {
        font-family: 'JetBrains Mono', monospace;
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 2px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        background: #181D2A;
        color: #CBD5E1;
        border: 1px solid #2B3346;
    }

    .badge-haki {
        background: #0E241B;
        color: #00E676;
        border: 1px solid #144933;
    }

    .badge-unnes {
        background: #121E2C;
        color: #00D2FF;
        border: 1px solid #1C354D;
    }

    .badge-model {
        background: #241D12;
        color: #FFB300;
        border: 1px solid #4D3917;
    }

    /* Telemetry Bento Grid */
    .metric-grid-4 {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin: 16px 0 20px 0;
    }

    .metric-card-pro {
        background: #11141E;
        border: 1px solid #262B38;
        border-radius: 2px;
        padding: 16px 18px;
        text-align: left;
        position: relative;
        transition: border-color 0.15s ease;
    }

    .metric-card-pro:hover {
        border-color: #4B556D;
    }

    .metric-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }

    .metric-txt {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 6px;
        color: #94A3B8;
    }

    /* High-Contrast Technical Accents */
    .txt-emerald { color: #00E676; }
    .txt-rose { color: #FF334B; }
    .txt-indigo { color: #00D2FF; }
    .txt-amber { color: #FFB300; }

    /* Inputs & Form Controls */
    .stTextArea textarea {
        background-color: #0F121B !important;
        border: 1px solid #262B38 !important;
        border-radius: 2px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
        color: #F1F5F9 !important;
        padding: 12px 14px !important;
    }

    .stTextArea textarea:focus {
        border-color: #00E676 !important;
        box-shadow: none !important;
    }

    /* Utilitarian Action Buttons */
    .stButton button, .stDownloadButton button {
        background: #181D2A !important;
        color: #E2E8F0 !important;
        border: 1px solid #333C4E !important;
        border-radius: 2px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        padding: 8px 18px !important;
        transition: all 0.12s ease !important;
    }

    .stButton button:hover, .stDownloadButton button:hover {
        background: #00E676 !important;
        color: #0C0E14 !important;
        border-color: #00E676 !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* Technical Rigid Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #262B38;
        padding-bottom: 0px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 2px 2px 0 0;
        padding: 8px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #64748B;
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        color: #00E676 !important;
        border-bottom: 2px solid #00E676 !important;
        background: #11141E !important;
    }

    /* Technical Sidebar Spec Sheet */
    .sidebar-haki-box {
        background: #11141E;
        border: 1px solid #262B38;
        border-left: 3px solid #00E676;
        border-radius: 2px;
        padding: 12px 14px;
        margin-top: 18px;
        font-family: 'JetBrains Mono', monospace;
    }

    .sidebar-haki-title {
        font-size: 0.72rem;
        font-weight: 800;
        color: #00E676;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }

    .sidebar-haki-text {
        font-size: 0.73rem;
        color: #94A3B8;
        line-height: 1.45;
    }

    .sidebar-haki-text b {
        color: #E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)


def render_hero_banner(title: str, subtitle: str, is_demo: bool = False):
    """
    Renders an Industrial Brutalist technical research terminal hero banner.
    """
    demo_badge = '<span class="badge-item badge-model">[MODE // REALTIME_INFERENCE]</span>' if is_demo else '<span class="badge-item badge-model">[MODE // RESEARCH_PIPELINE]</span>'
    
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-sys-tag">SYS.NLP // LAB.AI // ABSA.MBG // UNNES</div>
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
        <div class="badge-container">
            <span class="badge-item badge-haki">[HAKI // EC002026079870]</span>
            <span class="badge-item badge-unnes">[INST // UNNES_SEMARANG]</span>
            {demo_badge}
            <span class="badge-item badge-model">[MODELS // MNB + LSVC]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_haki():
    """
    Displays HAKI credentials as an industrial technical specification manifest.
    """
    st.sidebar.markdown("""
    <div class="sidebar-haki-box">
        <div class="sidebar-haki-title">[SPEC // CERTIFICATE_MANIFEST]</div>
        <div class="sidebar-haki-text">
            <b>REG_NO :</b> 001265752<br>
            <b>EC_CODE:</b> EC002026079870<br>
            <b>AUTHORS:</b> R. Alimul Haq, Dr. N. Iksan, Dr. Djuniadi<br>
            <b>HOLDER :</b> Universitas Negeri Semarang
        </div>
    </div>
    """, unsafe_allow_html=True)


def apply_matplotlib_style():
    """
    Sets high-precision technical dark styling for Matplotlib plots.
    """
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Space Grotesk', 'DejaVu Sans', 'Arial']
    plt.rcParams['text.color'] = '#E2E8F0'
    plt.rcParams['axes.labelcolor'] = '#94A3B8'
    plt.rcParams['xtick.color'] = '#94A3B8'
    plt.rcParams['ytick.color'] = '#94A3B8'
    plt.rcParams['axes.edgecolor'] = '#262B38'
    plt.rcParams['axes.linewidth'] = 1.0
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['grid.color'] = '#1A1F2C'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.8
    plt.rcParams['figure.facecolor'] = 'none'
    plt.rcParams['axes.facecolor'] = 'none'
