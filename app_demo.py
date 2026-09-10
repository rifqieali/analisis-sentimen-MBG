"""
ABSA MBG — Realtime Inference Console (Professional Edition).
Loads the trained model from joblib (auto-download on Streamlit Cloud).
Run: streamlit run app_demo.py
"""

import warnings
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score

from src.resources import load_nlp_resources, load_normalization_dict
from src.model_utils import load_saved_model, analyze_texts
from src.csv_io import read_uploaded_csv, canon_label
from src.ui import (
    inject_custom_css, render_hero_banner, render_sidebar_haki,
    apply_matplotlib_style, section_header, render_kpi_grid, kpi_card, PALETTE,
    INK, MUTED,
)

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="ABSA MBG — Realtime Inference Console",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
apply_matplotlib_style()

stemmer, final_stopwords, _negation_words = load_nlp_resources()
norm_dict = load_normalization_dict()
model_data = load_saved_model()

# ---------------------------------------------------------------- Hero
render_hero_banner(
    title="Aspect-Based Sentiment Analysis — Program MBG",
    subtitle="Realtime opinion mining console benchmarking Multinomial Naïve Bayes "
             "against LinearSVC. Paste sentences or upload a CSV, run inference, "
             "then inspect segments, aspects, and accuracy.",
    is_demo=True,
)

# ------------------------------------------------------------- Sidebar
with st.sidebar:
    st.markdown("### Inference guide")
    st.caption(
        "1. Choose an input mode below.\n"
        "2. For automatic accuracy, append a label per line (`… | Positif`).\n"
        "3. Run inference, then review the Results, Analytics, and Evaluation tabs."
    )
    st.divider()
    render_sidebar_haki()

if model_data is None:
    st.error(
        "Model unavailable — `saved_model_data.joblib` could not be loaded. "
        "Make sure the file exists locally or the release download URL is reachable.",
        icon="⚠️",
    )
    st.stop()

nb_model = model_data['model_nb']
svm_model = model_data['model_svm']
vec = model_data['vectorizer']

vocab_size = len(vec.vocabulary_)
classes = list(nb_model.classes_)

# ------------------------------------------------------- System status
st.markdown(f"""
<div class="pro-card" style="display:flex; flex-wrap:wrap; gap:8px 28px; align-items:center; padding:16px 22px;">
    <div>
        <div class="section-eyebrow">Active architectures</div>
        <div style="font-family:'JetBrains Mono',monospace; font-weight:700; font-size:0.95rem;">MultinomialNB · LinearSVC</div>
    </div>
    <div style="border-left:1px solid var(--border); padding-left:28px;">
        <div class="section-eyebrow">TF-IDF vocabulary</div>
        <div style="font-family:'JetBrains Mono',monospace; font-weight:700; font-size:0.95rem; color:{PALETTE['info']};">{vocab_size:,} features</div>
    </div>
    <div style="border-left:1px solid var(--border); padding-left:28px;">
        <div class="section-eyebrow">Target classes</div>
        <div style="font-family:'JetBrains Mono',monospace; font-weight:700; font-size:0.95rem; color:{PALETTE['positive']};">{' · '.join(classes)}</div>
    </div>
    <div style="margin-left:auto;">
        <span class="pill pill--success"><span style="width:7px;height:7px;border-radius:50%;background:{PALETTE['positive']};display:inline-block;"></span> Model ready</span>
    </div>
</div>
""", unsafe_allow_html=True)

for key, default in [
    ('rt_analyzed', False),
    ('rt_texts', []),
    ('rt_labels', []),
    ('rt_has_labels', False),
    ('df_results', None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================== INPUT
if not st.session_state['rt_analyzed']:
    section_header(
        "Step 1 — Input",
        "Choose how to feed the inference engine",
        "Two equivalent paths. Manual entry is fastest for spot checks; CSV upload is best for batch evaluation.",
    )

    mode = st.radio(
        "Input mode",
        ("Manual text batch", "CSV upload"),
        horizontal=True,
        help="Manual: one sentence per line. CSV: must contain a `full_text` column.",
    )
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if mode == "Manual text batch":
        with st.container():
            st.info(
                "One sentence per line. To enable automatic accuracy, append a label "
                "after a pipe — e.g. `menu MBG sangat lezat dan bergizi | Positif`.",
                icon="ℹ️",
            )
            raw = st.text_area(
                "Sentences (one per line)",
                height=190,
                placeholder=(
                    "makanan bergizi enak dan porsinya cukup untuk anak sekolah | Positif\n"
                    "distribusi makanan sering telat siswa menunggu berjam-jam | Negatif\n"
                    "dana MBG dikorupsi dan dimarkup oknum tidak bertanggung jawab | Negatif\n"
                    "menu MBG lezat dan higienis sangat membantu gizi siswa | Positif"
                ),
            )
            col_run, col_hint = st.columns([1.2, 2.8])
            with col_run:
                run = st.button("Run inference", type="primary", use_container_width=True)
            with col_hint:
                st.caption("Inference runs locally on the loaded TF-IDF + classifier bundle. No data leaves this session.")

            if run:
                if raw.strip():
                    texts, labels, has_labels = [], [], False
                    for line in raw.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        if '|' in line:
                            parts = line.split('|', 1)
                            texts.append(parts[0].strip())
                            labels.append(canon_label(parts[1]))
                        else:
                            texts.append(line)
                            labels.append(None)
                    has_labels = any(lab is not None for lab in labels)
                    st.session_state.update({
                        'rt_texts': texts, 'rt_labels': labels,
                        'rt_has_labels': has_labels, 'rt_analyzed': True,
                    })
                    st.rerun()
                else:
                    st.warning("Input is empty — paste at least one sentence to run inference.", icon="⚠️")
    else:
        with st.container():
            st.info(
                "CSV schema: required column `full_text`. Optional column `label` "
                "(`Positif` / `Negatif`) enables the accuracy benchmark.",
                icon="ℹ️",
            )
            template_df = pd.DataFrame({
                "full_text": [
                    "makanan bergizi enak dan porsinya cukup untuk anak sekolah",
                    "distribusi makanan sering telat siswa menunggu berjam-jam",
                    "dana MBG dikorupsi dan dimarkup oknum tidak bertanggung jawab",
                    "kualitas makanan bagus dan anak kenyang setelah makan",
                ],
                "label": ["Positif", "Negatif", "Negatif", "Positif"],
            })
            col_dl, col_up = st.columns([1, 2])
            with col_dl:
                st.download_button(
                    "Download CSV template",
                    data=template_df.to_csv(index=False).encode('utf-8'),
                    file_name="template_pengujian_mbg.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
                st.caption("UTF-8, comma-separated, header row included.")
            with col_up:
                uploaded_test = st.file_uploader("Upload CSV file", type="csv")

            run_batch = st.button("Run batch inference", type="primary", use_container_width=True)
            if run_batch:
                if uploaded_test:
                    try:
                        df_csv = read_uploaded_csv(uploaded_test)
                    except ValueError as e:
                        st.error(str(e), icon="⚠️")
                        df_csv = None
                    if df_csv is not None:
                        if 'full_text' not in df_csv.columns:
                            st.error(
                                f"Kolom `full_text` tak ketemu. Kolom tersedia: {', '.join(map(str, df_csv.columns))}.",
                                icon="⚠️",
                            )
                        else:
                            df_csv = df_csv[df_csv['full_text'].notna()].copy()
                            df_csv['full_text'] = df_csv['full_text'].astype(str).str.strip()
                            df_csv = df_csv[df_csv['full_text'] != ''].reset_index(drop=True)
                            if df_csv.empty:
                                st.error("Kolom `full_text` kosong semua — isi minimal 1 baris teks.", icon="⚠️")
                            else:
                                texts = df_csv['full_text'].tolist()
                                if 'label' in df_csv.columns:
                                    labels = [canon_label(v) for v in df_csv['label'].tolist()]
                                    has_labels = any(lab is not None for lab in labels)
                                else:
                                    labels = [None] * len(texts)
                                    has_labels = False
                                st.session_state.update({
                                    'rt_texts': texts, 'rt_labels': labels,
                                    'rt_has_labels': has_labels, 'rt_analyzed': True,
                                })
                                st.rerun()
                else:
                    st.warning("Upload a CSV file first.", icon="⚠️")

# ============================================================= RESULTS
else:
    col_reset, col_summary = st.columns([1.6, 4.4])
    with col_reset:
        if st.button("← New session", type="secondary", use_container_width=True):
            st.session_state.update({
                'rt_analyzed': False, 'rt_texts': [],
                'rt_labels': [], 'rt_has_labels': False, 'df_results': None,
            })
            st.rerun()
    with col_summary:
        st.caption(
            f"Evaluating **{len(st.session_state['rt_texts'])}** input sentence(s). "
            "Conjunction segmentation may expand these into multiple opinion segments."
        )

    texts = st.session_state['rt_texts']
    labels = st.session_state['rt_labels']
    has_labels = st.session_state['rt_has_labels']

    if st.session_state['df_results'] is None:
        progress_bar = st.progress(0, text=f"Analyzing {len(texts)} sample(s)…")
        df_res = analyze_texts(texts, nb_model, svm_model, vec, norm_dict, final_stopwords, stemmer, progress_bar)
        progress_bar.empty()
        st.session_state['df_results'] = df_res
    else:
        df_res = st.session_state['df_results']

    if df_res.empty:
        st.warning("No valid opinion segments detected. Try longer, complete sentences.", icon="⚠️")
        st.stop()

    total_seg = len(df_res)
    pos_svm = int((df_res['Prediksi SVM'] == 'Positif').sum())
    neg_svm = int((df_res['Prediksi SVM'] == 'Negatif').sum())
    pos_nb = int((df_res['Prediksi NB'] == 'Positif').sum())
    neg_nb = int((df_res['Prediksi NB'] == 'Negatif').sum())
    unique_texts = int(df_res['Teks Asli'].nunique())
    pos_rate = pos_svm / total_seg if total_seg else 0

    section_header("Step 2 — Results", "Inference overview",
                   "Counts below are opinion segments after conjunction splitting — not raw input lines.")

    render_kpi_grid([
        kpi_card(f"{unique_texts}", "Samples evaluated", f"{len(texts)} input line(s)", "blue", PALETTE["info"]),
        kpi_card(f"{total_seg}", "Opinion segments", "after conjunction split", "amber", PALETTE["warning"]),
        kpi_card(f"{pos_svm}", "Positive · LinearSVC", f"{pos_rate:.0%} of segments", "green", PALETTE["positive"]),
        kpi_card(f"{neg_svm}", "Negative · LinearSVC", f"{1 - pos_rate:.0%} of segments", "red", PALETTE["negative"]),
        kpi_card(f"{pos_nb}", "Positive · MNB", "MultinomialNB", "green", PALETTE["positive"]),
        kpi_card(f"{neg_nb}", "Negative · MNB", "MultinomialNB", "red", PALETTE["negative"]),
    ])

    tab_table, tab_charts, tab_eval = st.tabs(["Results table", "Visual analytics", "Model evaluation"])

    with tab_table:
        section_header("Results", "Segmentation detail & aspect-sentiment predictions",
                       "Each row is one opinion segment. `Aspek` is keyword-derived; probabilities come from MultinomialNB.")
        st.dataframe(df_res, use_container_width=True, height=380)

    with tab_charts:
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            section_header("Analytics", "Sentiment distribution",
                           "Donut share per architecture. Green = positive, red = negative.")
            fig_pie, axes = plt.subplots(1, 2, figsize=(8, 3.9))
            fig_pie.patch.set_alpha(0.0)
            for ax, col_pred, name in [(axes[0], 'Prediksi SVM', 'LinearSVC'), (axes[1], 'Prediksi NB', 'MultinomialNB')]:
                counts = df_res[col_pred].value_counts()
                colors = [PALETTE['positive'] if lab == 'Positif' else PALETTE['negative'] for lab in counts.index]
                wedges, _, autotexts = ax.pie(
                    counts.values, labels=counts.index, autopct='%1.1f%%',
                    colors=colors, startangle=90,
                    textprops=dict(color=INK, fontsize=9, fontweight='bold'),
                    wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2),
                )
                for t in autotexts:
                    t.set_fontsize(8)
                    t.set_color("#FFFFFF" if max(counts.values) > 0 else INK)
                ax.set_title(name, fontsize=11, fontweight='bold', color=INK)
            fig_pie.tight_layout()
            st.pyplot(fig_pie, use_container_width=True)
            plt.close(fig_pie)

        with c_chart2:
            section_header("Analytics", "Aspect polarity (LinearSVC)",
                           "Segments grouped by detected aspect. `Lainnya` excluded.")
            df_asp = df_res[~df_res['Aspek'].str.contains('Lainnya', na=False)].copy()
            if not df_asp.empty:
                pivot = df_asp.groupby(['Aspek', 'Prediksi SVM']).size().unstack(fill_value=0)
                # Stable column order + palette
                for col in ['Positif', 'Negatif']:
                    if col not in pivot.columns:
                        pivot[col] = 0
                pivot = pivot[['Positif', 'Negatif']]
                fig_bar, ax_bar = plt.subplots(figsize=(6.2, 3.9))
                fig_bar.patch.set_alpha(0.0)
                pivot.plot(
                    kind='bar', ax=ax_bar,
                    color=[PALETTE['positive'], PALETTE['negative']],
                    width=0.55, edgecolor='white', linewidth=1,
                )
                ax_bar.set_title("Segments per aspect", fontweight='bold', fontsize=11, color=INK)
                ax_bar.set_xlabel('')
                ax_bar.set_ylabel('Segments', color=MUTED)
                ax_bar.tick_params(axis='x', rotation=0, colors=INK)
                ax_bar.tick_params(axis='y', colors=MUTED)
                ax_bar.yaxis.grid(True, linestyle='--', alpha=0.9)
                ax_bar.set_axisbelow(True)
                for spine in ['top', 'right']:
                    ax_bar.spines[spine].set_visible(False)
                fig_bar.tight_layout()
                st.pyplot(fig_bar, use_container_width=True)
                plt.close(fig_bar)
            else:
                st.info("No specific aspect segments detected yet. Aspects trigger on quality, service, and budget keywords.", icon="ℹ️")

    with tab_eval:
        if has_labels and any(lab is not None for lab in labels):
            section_header("Evaluation", "Accuracy benchmark & error analysis",
                           "Compares the first segment prediction per input against the provided label.")
            eval_data = []
            for i, text in enumerate(texts):
                if labels[i] is None:
                    continue
                rows_t = df_res[df_res['Teks Asli'] == text]
                if rows_t.empty:
                    continue
                ps = canon_label(rows_t.iloc[0]['Prediksi SVM'])
                pn = canon_label(rows_t.iloc[0]['Prediksi NB'])
                lab = canon_label(labels[i])
                eval_data.append({
                    'Text': text[:65] + '…' if len(text) > 65 else text,
                    'True label': lab,
                    'LinearSVC': ps,
                    'NaiveBayes': pn,
                    'SVC match': '✓ Match' if ps == lab else '✗ Miss',
                    'NB match': '✓ Match' if pn == lab else '✗ Miss',
                })

            if eval_data:
                df_eval = pd.DataFrame(eval_data)
                acc_svm = accuracy_score(df_eval['True label'], df_eval['LinearSVC'])
                acc_nb = accuracy_score(df_eval['True label'], df_eval['NaiveBayes'])
                f1_svm = f1_score(df_eval['True label'], df_eval['LinearSVC'], average='weighted', zero_division=0)
                f1_nb = f1_score(df_eval['True label'], df_eval['NaiveBayes'], average='weighted', zero_division=0)

                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Accuracy · LinearSVC", f"{acc_svm:.1%}")
                with m2:
                    st.metric("Accuracy · MNB", f"{acc_nb:.1%}")
                with m3:
                    st.metric("F1-score · LinearSVC", f"{f1_svm:.1%}")
                with m4:
                    st.metric("F1-score · MNB", f"{f1_nb:.1%}")

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.dataframe(df_eval, use_container_width=True)
                st.caption("✓ / ✗ prefixes are static text cues — status never relies on color alone.")
        else:
            st.info(
                "Add labels to enable automatic evaluation — append `| Positif` / `| Negatif` "
                "per line, or upload a CSV with a `label` column.",
                icon="ℹ️",
            )

    st.divider()
    dl_col, _ = st.columns([1.6, 4.4])
    with dl_col:
        st.download_button(
            "Download results (CSV)",
            data=df_res.to_csv(index=False).encode('utf-8'),
            file_name="hasil_analisis_realtime_mbg.csv",
            mime="text/csv",
            type="secondary",
            use_container_width=True,
        )
    st.caption("ABSA MBG · Realtime console · MultinomialNB + LinearSVC · TF-IDF (1–2 grams)")
