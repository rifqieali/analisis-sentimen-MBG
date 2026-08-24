"""
Modul Desain UI & Estetika Swiss Technical Print / Industrial Brutalist (Light Theme Edition) untuk Streamlit
"""

import streamlit as st
import matplotlib.pyplot as plt

def inject_custom_css():
    """
    Menyuntikkan CSS kustom Swiss Technical Print / Light Industrial:
    - High-contrast crisp typography (Space Grotesk & JetBrains Mono)
    - Clean white/off-white background (#FFFFFF, #F8FAFC)
    - Sharp technical 1px borders (#CBD5E1, #94A3B8)
    - Deep readable obsidian text (#0F172A)
    - Utilitarian high-contrast accents (Emerald #16A34A, Crimson #DC2626, Azure #0284C7, Amber #D97706)
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }

    /* Main Viewport Container */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1280px;
    }

    /* Swiss Print Terminal Hero Banner */
    .hero-banner {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 3px solid #0F172A;
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
        color: #0284C7;
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
        background: #0284C7;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A !important;
        letter-spacing: -0.03em;
        margin: 0 0 8px 0;
        line-height: 1.2;
        text-transform: uppercase;
    }

    .hero-subtitle {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.92rem;
        color: #475569;
        margin-bottom: 16px;
        line-height: 1.5;
    }

    /* Technical Rectangular Badges (Light) */
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
        background: #F1F5F9;
        color: #1E293B;
        border: 1px solid #CBD5E1;
    }

    .badge-haki {
        background: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }

    .badge-unnes {
        background: #F0F9FF;
        color: #0369A1;
        border: 1px solid #BAE6FD;
    }

    .badge-model {
        background: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
    }

    /* Telemetry Bento Grid (Light) */
    .metric-grid-4 {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin: 16px 0 20px 0;
    }

    .metric-card-pro {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 2px;
        padding: 16px 18px;
        text-align: left;
        position: relative;
        transition: border-color 0.15s ease;
    }

    .metric-card-pro:hover {
        border-color: #64748B;
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
        color: #64748B;
    }

    /* High-Contrast Technical Accents (Light) */
    .txt-emerald { color: #16A34A; }
    .txt-rose { color: #DC2626; }
    .txt-indigo { color: #0284C7; }
    .txt-amber { color: #D97706; }

    /* Inputs & Form Controls */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 2px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
        color: #0F172A !important;
        padding: 12px 14px !important;
    }

    .stTextArea textarea:focus {
        border-color: #0F172A !important;
        box-shadow: none !important;
    }

    /* Utilitarian Action Buttons (Light) */
    .stButton button, .stDownloadButton button {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #94A3B8 !important;
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
        background: #0F172A !important;
        color: #FFFFFF !important;
        border-color: #0F172A !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* Technical Rigid Tabs (Light) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #CBD5E1;
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
        color: #0F172A !important;
        border-bottom: 2px solid #0F172A !important;
        background: #F8FAFC !important;
    }

    /* Technical Sidebar Spec Sheet (Light) */
    .sidebar-haki-box {
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 3px solid #0F172A;
        border-radius: 2px;
        padding: 12px 14px;
        margin-top: 18px;
        font-family: 'JetBrains Mono', monospace;
    }

    .sidebar-haki-title {
        font-size: 0.72rem;
        font-weight: 800;
        color: #0F172A;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }

    .sidebar-haki-text {
        font-size: 0.73rem;
        color: #475569;
        line-height: 1.45;
    }

    .sidebar-haki-text b {
        color: #0F172A;
    }
    </style>
    """, unsafe_allow_html=True)


def render_hero_banner(title: str, subtitle: str, is_demo: bool = False):
    """
    Renders a Swiss Print technical research terminal hero banner in Light Mode.
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
    Displays HAKI credentials as an industrial technical specification manifest in Light Mode.
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
    Sets high-contrast crisp light styling for Matplotlib plots.
    """
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Space Grotesk', 'DejaVu Sans', 'Arial']
    plt.rcParams['text.color'] = '#0F172A'
    plt.rcParams['axes.labelcolor'] = '#334155'
    plt.rcParams['xtick.color'] = '#334155'
    plt.rcParams['ytick.color'] = '#334155'
    plt.rcParams['axes.edgecolor'] = '#CBD5E1'
    plt.rcParams['axes.linewidth'] = 1.0
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['grid.color'] = '#F1F5F9'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.9
    plt.rcParams['figure.facecolor'] = 'none'
    plt.rcParams['axes.facecolor'] = 'none'
