"""
Professional UI design system for ABSA MBG Streamlit apps.

Design language: clean analytics terminal — soft neutral canvas, white
elevated surfaces, single icon set (currentColor), restrained motion.

Polish rules applied (see skill `better-ui`):
- Concentric radius: outer 16px = inner 10px + 6px gap; small 8px = inner 6px + 2px.
- Shadows for elevation, borders for structure/state only.
- Interactive changes use CSS transitions (interruptible);
  keyframes only for one-shot staged entrances (~100ms stagger).
- Exits softer than enters: fixed 4px translateY, ease-out both ways.
- Icon swaps cross-fade opacity/scale/blur: 0->1, 0.25->1, 4px->0px,
  easing cubic-bezier(0.2, 0, 0, 1).
- Press feedback is always scale(0.96); `.is-static` opts out.
- Transitions name exact properties; high-frequency ones are <=150ms.
- will-change only transform/opacity/filter, added sparingly.
- Images get a 1px low-opacity outline (oklch, never tinted).
- Icon stroke 1.5px beside regular text, 2px beside semibold.
"""

import streamlit as st
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Shared palette (single source of truth for CSS + matplotlib)
# ---------------------------------------------------------------------------
POSITIVE = "#059669"
NEGATIVE = "#DC2626"
INFO = "#0284C7"
WARNING = "#D97706"
INK = "#0F172A"
MUTED = "#475569"
FAINT = "#64748B"
BORDER = "#E2E8F0"

EASE = "cubic-bezier(0.2, 0, 0, 1)"  # exact — do not approximate


def inject_custom_css():
    """Inject the professional design system CSS."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {{
        --bg: #F8FAFC;
        --surface: #FFFFFF;
        --border: {BORDER};
        --border-strong: #CBD5E1;
        --ink: {INK};
        --muted: {MUTED};
        --faint: {FAINT};
        --positive: {POSITIVE};
        --negative: {NEGATIVE};
        --info: {INFO};
        --warning: {WARNING};
        --r-lg: 16px;   /* outer surface */
        --r-md: 10px;   /* inner block = 16 - 6 gap */
        --r-sm: 8px;
        --ease: {EASE};
        --shadow-sm: 0 1px 2px rgb(15 23 42 / 0.05);
        --shadow-md: 0 1px 2px rgb(15 23 42 / 0.04), 0 8px 24px -12px rgb(15 23 42 / 0.12);
        --shadow-lg: 0 2px 4px rgb(15 23 42 / 0.05), 0 16px 40px -16px rgb(15 23 42 / 0.18);
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: var(--ink);
    }}
    .stApp {{ background: var(--bg); }}

    .block-container {{
        padding-top: 1.75rem;
        padding-bottom: 3rem;
        max-width: 1240px;
    }}

    /* Tabular numbers for every metric / table */
    .metric-num, .kpi-value, .stMetric [data-testid="stMetricValue"],
    .stDataFrame, .pro-table {{
        font-variant-numeric: tabular-nums;
    }}

    /* ---------------- Hero ---------------- */
    .hero-banner, .pro-hero {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);          /* outer 16 */
        box-shadow: var(--shadow-md);
        padding: 26px 28px 22px 28px;
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
    }}
    .hero-banner::before, .pro-hero::before {{
        content: '';
        position: absolute;
        inset: 0 0 auto 0;
        height: 3px;
        background: linear-gradient(90deg, var(--info) 0%, #38BDF8 45%, var(--positive) 100%);
        opacity: 0.9;
    }}
    .hero-sys-tag, .pro-eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--info);
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .hero-sys-tag::before, .pro-eyebrow .dot {{
        content: '';
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--positive);
        box-shadow: 0 0 0 3px rgb(5 150 105 / 0.15);
    }}
    /* Optical nudge: dot sits 1px high vs caps, so pull it down */
    .hero-sys-tag::before {{ transform: translateY(1px); }}
    .hero-title, .pro-hero-title {{
        font-size: 1.7rem;
        font-weight: 700;
        color: var(--ink) !important;
        letter-spacing: -0.02em;
        margin: 0 0 6px 0;
        line-height: 1.2;
    }}
    .hero-subtitle, .pro-hero-sub {{
        font-size: 0.93rem;
        color: var(--muted);
        line-height: 1.55;
        max-width: 86ch;
        margin-bottom: 4px;
    }}

    /* ---------------- Badges / pills (single SVG-free dot, currentColor text) -- */
    .badge-container, .pill-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-top: 14px;
    }}
    .badge-item, .pill {{
        font-family: 'JetBrains Mono', monospace;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 11px;                 /* inner 6px radius + padding ≈ outer rhythm */
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        background: #F1F5F9;
        color: #1E293B;
        border: 1px solid var(--border);
        transition-property: background-color, color, border-color;
        transition-duration: 150ms;
        transition-timing-function: var(--ease);
    }}
    .badge-haki, .pill--success {{ background: #ECFDF5; color: #065F46; border-color: #A7F3D0; }}
    .badge-unnes, .pill--info {{ background: #F0F9FF; color: #0369A1; border-color: #BAE6FD; }}
    .badge-model, .pill--neutral {{ background: #FFF7ED; color: #9A3412; border-color: #FED7AA; }}
    .pill--danger {{ background: #FEF2F2; color: #991B1B; border-color: #FECACA; }}

    /* ---------------- Cards & KPI grid (concentric radius) ---------------- */
    .pro-card {{
        background: var(--surface);
        border: 1px solid var(--border);   /* structure */
        border-radius: var(--r-lg);        /* outer 16 */
        box-shadow: var(--shadow-sm);      /* elevation via shadow */
        padding: 20px 22px;
        margin-bottom: 16px;
    }}
    .pro-card--flat {{ box-shadow: none; }}
    .pro-card h3, .pro-card h4 {{ letter-spacing: -0.01em; }}

    .metric-grid-4, .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 12px;
        margin: 14px 0 18px 0;
    }}
    .metric-card-pro, .kpi-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);
        box-shadow: var(--shadow-sm);
        padding: 16px 18px 14px 18px;
        position: relative;
        overflow: hidden;
        transition-property: transform, box-shadow, border-color;
        transition-duration: 150ms;
        transition-timing-function: var(--ease);
        animation: kpi-enter 0.3s var(--ease) both;   /* one-shot staged entrance */
    }}
    /* Stagger infrequent entrances by ~100ms (enter only, never high-frequency) */
    .metric-grid-4 > *:nth-child(2), .kpi-grid > *:nth-child(2) {{ animation-delay: 100ms; }}
    .metric-grid-4 > *:nth-child(3), .kpi-grid > *:nth-child(3) {{ animation-delay: 200ms; }}
    .metric-grid-4 > *:nth-child(4), .kpi-grid > *:nth-child(4) {{ animation-delay: 300ms; }}
    .metric-grid-4 > *:nth-child(5), .kpi-grid > *:nth-child(5) {{ animation-delay: 400ms; }}
    .metric-grid-4 > *:nth-child(6), .kpi-grid > *:nth-child(6) {{ animation-delay: 500ms; }}
    @keyframes kpi-enter {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .metric-card-pro:hover, .kpi-card:hover {{
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        border-color: var(--border-strong);
    }}
    .metric-card-pro::before, .kpi-card::before {{
        content: '';
        position: absolute;
        left: 0; top: 14px; bottom: 14px;
        width: 3px;
        border-radius: 0 3px 3px 0;
        background: var(--accent-bar, var(--border-strong));
    }}
    .metric-num, .kpi-value {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.7rem;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.02em;
        color: var(--ink);
    }}
    .metric-txt, .kpi-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 6px;
        color: var(--faint);
    }}
    .kpi-hint {{ font-size: 0.78rem; color: var(--faint); margin-top: 2px; }}
    .txt-emerald {{ color: var(--positive); }}
    .txt-rose {{ color: var(--negative); }}
    .txt-indigo {{ color: var(--info); }}
    .txt-amber {{ color: var(--warning); }}

    /* Section header: eyebrow + title + description */
    .section-head {{ margin: 6px 0 12px 0; }}
    .section-eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem; font-weight: 600;
        letter-spacing: 0.1em; text-transform: uppercase;
        color: var(--faint); margin-bottom: 4px;
    }}
    .section-title {{ font-size: 1.15rem; font-weight: 700; letter-spacing: -0.015em; margin: 0; }}
    .section-desc {{ font-size: 0.88rem; color: var(--muted); margin: 4px 0 0 0; line-height: 1.55; }}

    /* Stepper (pipeline progress) */
    .stepper {{
        display: flex; flex-wrap: wrap; gap: 8px; align-items: stretch;
        margin: 4px 0 16px 0;
    }}
    .step {{
        flex: 1 1 140px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-md);        /* inner 10 */
        padding: 10px 12px;
        display: flex; gap: 10px; align-items: flex-start;
        transition-property: border-color, box-shadow;
        transition-duration: 150ms;
        transition-timing-function: var(--ease);
    }}
    .step .n {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; font-weight: 700;
        width: 24px; height: 24px; border-radius: 8px;   /* concentric: 10 outer - 2 gap */
        display: inline-flex; align-items: center; justify-content: center;
        background: #F1F5F9; color: var(--faint);
        border: 1px solid var(--border);
        flex-shrink: 0;
    }}
    .step.done .n {{ background: #ECFDF5; color: #065F46; border-color: #A7F3D0; }}
    .step.active {{ border-color: var(--ink); box-shadow: var(--shadow-sm); }}
    .step.active .n {{ background: var(--ink); color: #fff; border-color: var(--ink); }}
    .step .t {{ font-size: 0.8rem; font-weight: 600; line-height: 1.3; }}
    .step .s {{ font-size: 0.72rem; color: var(--faint); }}

    /* ---------------- Inputs & buttons ---------------- */
    .stTextArea textarea, .stTextInput input {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--r-md) !important;   /* inner 10 */
        font-size: 0.88rem !important;
        color: var(--ink) !important;
        padding: 12px 14px !important;
        box-shadow: var(--shadow-sm);
        transition-property: border-color, box-shadow;
        transition-duration: 150ms;
        transition-timing-function: var(--ease);
    }}
    .stTextArea textarea:focus, .stTextInput input:focus {{
        border-color: var(--info) !important;
        box-shadow: 0 0 0 3px rgb(2 132 199 / 0.15) !important;
    }}
    .stTextArea textarea {{ font-family: 'JetBrains Mono', monospace !important; line-height: 1.6 !important; }}

    .stButton button, .stDownloadButton button {{
        border-radius: var(--r-md) !important;   /* inner 10 inside 16 cards */
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.01em !important;
        text-transform: none !important;
        padding: 10px 18px !important;
        transition-property: transform, background-color, color, border-color, box-shadow;
        transition-duration: 150ms;
        transition-timing-function: var(--ease);
        will-change: transform;
    }}
    /* Primary buttons: first in a row or kind=primary */
    .stButton button[kind="primary"] {{
        background: var(--ink) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--ink) !important;
        box-shadow: var(--shadow-sm) !important;
    }}
    .stButton button[kind="primary"]:hover {{
        background: #1E293B !important;
        border-color: #1E293B !important;
        box-shadow: var(--shadow-md) !important;
    }}
    .stButton button[kind="secondary"], .stDownloadButton button {{
        background: var(--surface) !important;
        color: var(--ink) !important;
        border: 1px solid var(--border-strong) !important;
    }}
    .stButton button:hover, .stDownloadButton button:hover {{
        transform: translateY(-1px);
        box-shadow: var(--shadow-md) !important;
    }}
    .stButton button:active, .stDownloadButton button:active {{
        transform: scale(0.96);   /* exact press feedback */
    }}
    .stButton button.is-static:active, .stDownloadButton button.is-static:active {{
        transform: none;
    }}
    .stButton button:focus-visible, .stDownloadButton button:focus-visible,
    a:focus-visible, input:focus-visible, textarea:focus-visible {{
        outline: 2px solid var(--info) !important;
        outline-offset: 2px !important;
    }}

    /* Radio / select polish */
    .stRadio [role="radiogroup"] {{ gap: 8px; }}
    .stRadio div[data-testid="stWidgetLabel"] p,
    .stSelectbox div[data-testid="stWidgetLabel"] p {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; font-weight: 600;
        letter-spacing: 0.08em; text-transform: uppercase;
        color: var(--faint);
    }}

    /* ---------------- Tabs ---------------- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0px;
        background: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: var(--r-sm) var(--r-sm) 0 0;
        padding: 10px 16px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.83rem;
        letter-spacing: 0.01em;
        color: var(--faint);
        background: transparent;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
        transition-property: color, background-color;
        transition-duration: 150ms;
        transition-timing-function: var(--ease);
    }}
    .stTabs [data-baseweb="tab"]:hover {{ color: var(--ink); background: #F1F5F9; }}
    .stTabs [aria-selected="true"] {{
        color: var(--ink) !important;
        border-bottom: 2px solid var(--ink) !important;
        background: var(--surface) !important;
    }}

    /* ---------------- Tables ---------------- */
    .stDataFrame {{
        border: 1px solid var(--border);
        border-radius: var(--r-md);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }}

    /* ---------------- Sidebar ---------------- */
    section[data-testid="stSidebar"] {{ background: #FFFFFF; border-right: 1px solid var(--border); }}
    .sidebar-haki-box {{
        background: #F8FAFC;
        border: 1px solid var(--border);
        border-radius: var(--r-md);
        padding: 12px 14px;
        margin-top: 14px;
        font-family: 'JetBrains Mono', monospace;
        box-shadow: var(--shadow-sm);
    }}
    .sidebar-haki-title {{
        font-size: 0.68rem; font-weight: 700; color: var(--ink);
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;
    }}
    .sidebar-haki-text {{ font-size: 0.73rem; color: var(--muted); line-height: 1.55; }}
    .sidebar-haki-text b {{ color: var(--ink); font-weight: 600; }}

    /* Sidebar icons: single weight per set, currentColor */
    section[data-testid="stSidebar"] svg {{
        stroke-width: 1.5px;
        color: currentColor;
    }}
    section[data-testid="stSidebar"] strong svg,
    section[data-testid="stSidebar"] [aria-selected="true"] svg {{
        stroke-width: 2px;   /* 2px beside semibold */
    }}

    /* ---------------- Alerts: static cue + motion (never motion alone) --- */
    .stAlert {{
        border-radius: var(--r-md) !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow-sm);
        font-size: 0.87rem;
    }}

    /* ---------------- Images: 1px low-opacity outline, never tinted -------- */
    .stImage img {{
        border-radius: var(--r-md);
        outline: 1px solid oklch(0 0 0 / 0.1);
        outline-offset: -1px;
    }}
    @media (prefers-color-scheme: dark) {{
        .stImage img {{ outline-color: oklch(1 0 0 / 0.1); }}
    }}

    /* ---------------- Icon cross-fade helper (no dependency) --------------- */
    .icon-swap {{ position: relative; display: inline-flex; width: 1.25em; height: 1.25em; }}
    .icon-swap > * {{ position: absolute; inset: 0; }}
    .icon-swap > *:last-child {{
        opacity: 0; transform: scale(0.25); filter: blur(4px);
        transition-property: opacity, transform, filter;
        transition-duration: 0.3s;
        transition-timing-function: var(--ease);
    }}
    .icon-swap.is-on > *:first-child {{
        opacity: 0; transform: scale(0.25); filter: blur(4px);
    }}
    .icon-swap.is-on > *:last-child {{
        opacity: 1; transform: scale(1); filter: blur(0px);
    }}

    /* Subtle exit helper: softer than enter, fixed 4px */
    .exit-soft {{ transition-property: opacity, transform; transition-duration: 150ms; transition-timing-function: ease-out; }}
    .exit-soft.is-leaving {{ opacity: 0; transform: translateY(4px); }}

    /* Progress + spinner restraint (static label always present) */
    .stProgress > div > div {{ background-color: var(--ink) !important; }}

    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }}
    }}
    </style>

    <script>
    // Suppress transitions across a theme flip so the swap snaps instead of smearing.
    (function() {{
        function snapThemeSwap() {{
            const css = '*,*::before,*::after{{transition:none !important}}';
            const el = document.createElement('style');
            el.textContent = css;
            document.head.appendChild(el);
            void document.body.offsetHeight;  /* force reflow */
            requestAnimationFrame(() => requestAnimationFrame(() => el.remove()));
        }}
        const root = document.documentElement;
        if (root && !root.__themeSnapHooked) {{
            root.__themeSnapHooked = true;
            new MutationObserver((m) => {{
                for (const rec of m) {{
                    if (rec.attributeName === 'class' || rec.attributeName === 'data-theme') snapThemeSwap();
                }}
            }}).observe(root, {{ attributes: true }});
        }}
    }})();
    </script>
    """, unsafe_allow_html=True)


def render_hero_banner(title: str, subtitle: str, is_demo: bool = False):
    """Professional hero: eyebrow + title + subtitle + status pills."""
    mode = "Realtime Inference" if is_demo else "Research Pipeline"
    st.markdown(f"""
    <div class="pro-hero hero-banner">
        <div class="pro-eyebrow hero-sys-tag"><span class="dot"></span>ABSA &nbsp;·&nbsp; Program Makan Bergizi Gratis &nbsp;·&nbsp; UNNES</div>
        <div class="pro-hero-title hero-title">{title}</div>
        <div class="pro-hero-sub hero-subtitle">{subtitle}</div>
        <div class="pill-row badge-container">
            <span class="pill pill--success badge-item badge-haki">HAKI · EC002026079870</span>
            <span class="pill pill--info badge-item badge-unnes">Universitas Negeri Semarang</span>
            <span class="pill pill--neutral badge-item badge-model">{mode}</span>
            <span class="pill pill--neutral badge-item">MNB + LinearSVC</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_haki():
    """Certificate manifest card in the sidebar."""
    st.sidebar.markdown("""
    <div class="sidebar-haki-box">
        <div class="sidebar-haki-title">Certificate manifest</div>
        <div class="sidebar-haki-text">
            <b>Reg. no</b> &nbsp;001265752<br>
            <b>EC code</b> &nbsp;EC002026079870<br>
            <b>Authors</b> &nbsp;R. Alimul Haq · Dr. N. Iksan · Dr. Djuniadi<br>
            <b>Holder</b> &nbsp;Universitas Negeri Semarang
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(eyebrow: str, title: str, description: str = ""):
    """Consistent section heading: mono eyebrow + strong title + muted lede."""
    st.markdown(f"""
    <div class="section-head">
        <div class="section-eyebrow">{eyebrow}</div>
        <div class="section-title">{title}</div>
        {f'<div class="section-desc">{description}</div>' if description else ''}
    </div>
    """, unsafe_allow_html=True)


def render_stepper(steps: list, active: int):
    """Horizontal stepper. `steps`: [(title, subtitle)]. `active`: index."""
    cards = []
    for i, (t, s) in enumerate(steps):
        cls = "done" if i < active else ("active" if i == active else "")
        mark = "✓" if i < active else str(i + 1)
        cards.append(
            f'<div class="step {cls}"><span class="n">{mark}</span>'
            f'<span><span class="t">{t}</span><br><span class="s">{s}</span></span></div>'
        )
    st.markdown(f'<div class="stepper">{"".join(cards)}</div>', unsafe_allow_html=True)


def kpi_card(value: str, label: str, hint: str = "", tone: str = "ink", accent: str = "") -> str:
    """Single KPI card HTML. Tone: ink|green|red|blue|amber."""
    tone_cls = {"ink": "", "green": "txt-emerald", "red": "txt-rose",
                "blue": "txt-indigo", "amber": "txt-amber"}.get(tone, "")
    bar = f' style="--accent-bar: {accent};"' if accent else ""
    hint_html = f'<div class="kpi-hint">{hint}</div>' if hint else ""
    return (
        f'<div class="kpi-card metric-card-pro"{bar}>'
        f'<div class="kpi-value metric-num {tone_cls}">{value}</div>'
        f'<div class="kpi-label metric-txt">{label}</div>{hint_html}</div>'
    )


def render_kpi_grid(cards: list):
    """Render a staggered KPI grid from pre-built `kpi_card` strings."""
    st.markdown(f'<div class="kpi-grid metric-grid-4">{"".join(cards)}</div>',
                unsafe_allow_html=True)


def apply_matplotlib_style():
    """Crisp, professional light styling for Matplotlib/Seaborn."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "DejaVu Sans", "Arial"],
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.edgecolor": BORDER,
        "axes.linewidth": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": "#EEF2F7",
        "grid.linestyle": "--",
        "grid.alpha": 1.0,
        "figure.facecolor": "none",
        "axes.facecolor": "none",
        "axes.titleweight": "bold",
        "axes.titlesize": 11,
    })


# Re-export canonical palette for charts so apps stay consistent.
PALETTE = {
    "positive": POSITIVE,
    "negative": NEGATIVE,
    "info": INFO,
    "warning": WARNING,
    "ink": INK,
    "muted": MUTED,
    "faint": FAINT,
    "border": BORDER,
}
