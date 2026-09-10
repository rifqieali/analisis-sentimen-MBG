"""
ABSA MBG — End-to-End Research Pipeline (Professional Edition).
Stages: Ingestion → Preprocessing → Labeling → Training → Evaluation → Realtime.
Run: streamlit run app_pipeline.py
"""

import time
import os
import ast
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
)

from src.constants import PAGES, TFIDF_PARAMS
from src.resources import (
    load_nlp_resources, load_normalization_dict,
    load_inset_lexicon, load_roberta_pipeline,
)
from src.preprocessing import (
    clean_text, normalize_text, segmentasi_kalimat,
    stopword_and_stem, get_aspects, determine_sentiment_roberta,
)
from src.model_utils import analyze_texts
from src.csv_io import read_uploaded_csv
from src.ui import (
    inject_custom_css, render_hero_banner, render_sidebar_haki,
    apply_matplotlib_style, section_header, render_stepper,
    render_kpi_grid, kpi_card, PALETTE,
    INK, MUTED,
)

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="ABSA MBG — Research Pipeline",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
apply_matplotlib_style()

stemmer, final_stopwords, _negation_words = load_nlp_resources()
norm_dict = load_normalization_dict()
_lexicon = load_inset_lexicon()

# ============================================================ STATE
for key, default in [
    ('current_page', PAGES[0]),
    ('df_raw', None),
    ('df_exploded', None),
    ('preprocessing_done', False),
    ('labeling_done', False),
    ('df_neutral_handled', None),
    ('neutral_action', None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def set_page(page_name):
    st.session_state['current_page'] = page_name


# ============================================================ HERO
render_hero_banner(
    title="ABSA Research Pipeline — Program Makan Bergizi Gratis",
    subtitle="End-to-end scientific workflow: ingestion, conjunction segmentation, "
             "RoBERTa annotation, multi-scenario training, and aspect-level evaluation.",
    is_demo=False,
)

# ============================================================ SIDEBAR
with st.sidebar:
    st.markdown("### Pipeline modules")
    menu = st.radio("Select a module", PAGES, key='current_page', label_visibility="collapsed")
    st.divider()
    # Checklist: static text cues alongside any color/status
    has_raw = st.session_state.get('df_raw') is not None
    has_prep = bool(st.session_state.get('preprocessing_done'))
    has_label = bool(st.session_state.get('labeling_done'))
    has_model = 'hasil_skenario' in st.session_state
    st.caption(
        f"{'✓' if has_raw else '○'} Ingested · "
        f"{'✓' if has_prep else '○'} Preprocessed · "
        f"{'✓' if has_label else '○'} Labeled · "
        f"{'✓' if has_model else '○'} Trained"
    )
    st.divider()
    render_sidebar_haki()

# Top stepper (staggered entrance handled in CSS, ~100ms per card)
try:
    active_idx = PAGES.index(menu)
except ValueError:
    active_idx = 0
render_stepper(
    [
        ("Ingestion", "Load CSV"),
        ("Preprocessing", "Segment"),
        ("Labeling", "RoBERTa + aspects"),
        ("Training", "70/80/90 splits"),
        ("Evaluation", "Per aspect"),
        ("Realtime", "Inference"),
    ],
    active=active_idx,
)

# ============================================================ 01 UPLOAD
if menu == PAGES[0]:
    section_header(
        "01 — Data ingestion",
        "Load a dataset into memory",
        "Choose the entry point that matches your file. The pipeline tracks progress automatically — "
        "each choice routes you to the correct next module.",
    )

    with st.container():
        data_type = st.radio(
            "Input type",
            (
                "Raw data (needs preprocessing)",
                "Preprocessed data (skip to labeling)",
                "Labeled data (go to visualization & modeling)",
            ),
            help="Raw: any text column. Preprocessed: must contain `segment`. Labeled: needs `segment`, `sentiment_label`, `aspect_list`.",
        )
        uploaded_file = st.file_uploader("Upload dataset (CSV)", type="csv")

    if uploaded_file:
        try:
            df = read_uploaded_csv(uploaded_file)
        except ValueError as e:
            st.error(str(e), icon="⚠️")
            df = None

        if df is None:
            pass
        elif data_type == "Raw data (needs preprocessing)":
            st.session_state['df_raw'] = df
            st.session_state['df_exploded'] = None
            st.session_state['preprocessing_done'] = False
            st.session_state['labeling_done'] = False
            st.session_state['df_neutral_handled'] = None
            st.session_state['neutral_action'] = None
            st.success(f"Raw data loaded — **{len(df):,}** rows ready.", icon="✅")
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"{len(df.columns)} column(s): {', '.join(map(str, df.columns[:8]))}" + ("…" if len(df.columns) > 8 else ""))
            st.button("Continue to preprocessing →", type="primary", on_click=set_page, args=(PAGES[1],))
        elif data_type == "Preprocessed data (skip to labeling)":
            if 'segment' not in df.columns:
                st.error("Schema error — required column `segment` was not found in this CSV.", icon="⚠️")
            else:
                st.session_state['df_exploded'] = df
                st.session_state['df_raw'] = None
                st.session_state['preprocessing_done'] = True
                st.session_state['labeling_done'] = False
                st.session_state['df_neutral_handled'] = None
                st.session_state['neutral_action'] = None
                st.success(f"Preprocessed data loaded — **{len(df):,}** opinion segments.", icon="✅")
                st.dataframe(df.head(10), use_container_width=True)
                st.button("Continue to labeling →", type="primary", on_click=set_page, args=(PAGES[2],))
        else:
            required_cols = ['segment', 'sentiment_label', 'aspect_list']
            missing_cols = [c for c in required_cols if c not in df.columns]
            if missing_cols:
                st.error(f"Schema error — missing required column(s): {', '.join(missing_cols)}.", icon="⚠️")
            else:
                def parse_aspect(x):
                    if isinstance(x, str):
                        try:
                            res = ast.literal_eval(x)
                            if isinstance(res, list):
                                return res
                            return [x]
                        except Exception:
                            return [x]
                    return x if isinstance(x, list) else [x]

                df['aspect_list'] = df['aspect_list'].apply(parse_aspect)
                st.session_state['df_exploded'] = df
                st.session_state['df_raw'] = None
                st.session_state['preprocessing_done'] = True
                st.session_state['labeling_done'] = True
                st.session_state['df_neutral_handled'] = None
                st.session_state['neutral_action'] = None
                st.success(f"Labeled data loaded — **{len(df):,}** segments ready for modeling.", icon="✅")
                st.dataframe(df.head(10), use_container_width=True)
                st.button("View visualization (labeling) →", type="primary", on_click=set_page, args=(PAGES[2],))
    else:
        st.info("Upload a CSV to begin. No file is stored outside this session.", icon="ℹ️")

# ============================================================ 02 PREPROCESSING
elif menu == PAGES[1]:
    section_header(
        "02 — Preprocessing & segmentation",
        "Conjunction-aware opinion splitting",
        "Research contribution: compound sentences containing conjunctions are split into separate "
        "opinion segments before vectorization, improving aspect-level accuracy.",
    )

    if st.session_state['df_raw'] is not None:
        df = st.session_state['df_raw'].copy()
        col_name = st.selectbox("Text column", df.columns, help="The column containing raw opinion text.")

        if st.button("Run preprocessing pipeline", type="primary"):
            with st.spinner("Cleaning → normalizing → segmenting → stopwords & stemming…"):
                count_raw = len(df)
                df = df.drop_duplicates(subset=[col_name], keep='first').copy()
                df['doc_id'] = range(len(df))
                count_awal = len(df)

                df['text_clean'] = df[col_name].apply(clean_text)
                count_clean = len(df)
                df['text_norm'] = df['text_clean'].apply(lambda x: normalize_text(x, norm_dict))
                count_norm = len(df)

                df['segmen_list'] = df['text_norm'].apply(segmentasi_kalimat)
                df_exploded = df.explode('segmen_list').dropna(subset=['segmen_list'])
                df_exploded['segment'] = df_exploded['segmen_list'].astype(str).str.strip()
                df_exploded = df_exploded[df_exploded['segment'] != '']
                count_segmentasi = len(df_exploded)

                my_bar = st.progress(0)
                total_rows = count_segmentasi
                processed_segments = []
                for i, seg in enumerate(df_exploded['segment']):
                    processed_segments.append(stopword_and_stem(seg, final_stopwords, stemmer))
                    if i % max(1, total_rows // 100) == 0:
                        my_bar.progress(min(i / total_rows, 1.0))
                my_bar.progress(1.0)

                df_exploded['segment'] = processed_segments
                df_exploded = df_exploded[df_exploded['segment'].str.strip() != ''].reset_index(drop=True)
                count_final = len(df_exploded)

                st.session_state['df_exploded'] = df_exploded
                st.session_state['preprocessing_done'] = True
                st.session_state['labeling_done'] = False
                st.session_state['df_neutral_handled'] = None
                st.session_state['neutral_action'] = None
                st.session_state['prep_stats'] = {
                    "raw": count_raw, "awal": count_awal, "clean": count_clean,
                    "norm": count_norm, "segmentasi": count_segmentasi, "final": count_final,
                }

        if st.session_state.get('preprocessing_done', False):
            stats = st.session_state.get('prep_stats', {})
            if stats:
                st.success("Preprocessing complete — the corpus below is deduplicated, normalized, and segmented.", icon="✅")
                render_kpi_grid([
                    kpi_card(f"{stats['raw']:,}", "Raw rows", "uploaded input", "blue", PALETTE["info"]),
                    kpi_card(f"{stats['awal']:,}", "Deduplicated", "anti-duplicate filter", "green", PALETTE["positive"]),
                    kpi_card(f"{stats['segmentasi']:,}", "Segments", f"×{stats['segmentasi'] / max(stats['awal'], 1):.2f} expansion", "amber", PALETTE["warning"]),
                    kpi_card(f"{stats['final']:,}", "Clean final", "non-empty after stemming", "green", PALETTE["positive"]),
                ])

            st.markdown("#### Preview — document IDs & clean segments")
            st.dataframe(
                st.session_state['df_exploded'][['doc_id', col_name, 'segment']].head(10),
                use_container_width=True,
            )
            c1, c2 = st.columns([1, 1])
            with c1:
                st.download_button(
                    "Download preprocessed CSV",
                    data=st.session_state['df_exploded'].to_csv(index=False).encode('utf-8'),
                    file_name="hasil_preprocessing_mbg.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with c2:
                st.button("Continue to labeling →", type="primary", on_click=set_page, args=(PAGES[2],), use_container_width=True)
    else:
        st.warning("Upload raw data in the Ingestion module first.", icon="⚠️")

# ============================================================ 03 LABELING
elif menu == PAGES[2]:
    section_header(
        "03 — Annotation & aspect extraction",
        "RoBERTa auto-labeling with neutral handling",
        "Polarity comes from an Indonesian RoBERTa classifier; aspects (quality, service, budget) "
        "are keyword-derived. Decide explicitly how neutral predictions are treated.",
    )

    if st.session_state['df_exploded'] is not None:
        df = st.session_state['df_exploded']

        st.markdown("#### Neutral-sentiment policy")
        handle_neutral = st.radio(
            "How should RoBERTa `Netral` outputs be treated?",
            ("Drop neutral rows (keep Positive & Negative only)", "Map neutral rows to Positive"),
            help="Dropping keeps a strict binary problem; mapping preserves coverage. The choice is recorded with the run.",
        )

        if not st.session_state['labeling_done']:
            if st.button("Run RoBERTa auto-annotation", type="primary"):
                with st.spinner("Loading Indonesian RoBERTa weights from Hugging Face Hub…"):
                    classifier = load_roberta_pipeline()
                if classifier is None:
                    st.error("RoBERTa failed to load. Check your internet connection and retry.", icon="⚠️")
                else:
                    with st.spinner("Annotating polarity & extracting aspects…"):
                        total_rows = len(df)
                        my_bar = st.progress(0)
                        sentiments = []
                        for i, seg in enumerate(df['segment']):
                            sentiments.append(determine_sentiment_roberta(seg, classifier))
                            if i % max(1, total_rows // 100) == 0:
                                my_bar.progress(min((i + 1) / total_rows, 1.0))
                        my_bar.progress(1.0)

                        df['sentiment_label'] = sentiments
                        df['aspect_list'] = df['segment'].apply(get_aspects)

                        df_neutral = df[df['sentiment_label'] == 'Netral'].copy()
                        st.session_state['df_neutral_handled'] = df_neutral
                        st.session_state['neutral_action'] = handle_neutral

                        if handle_neutral == "Drop neutral rows (keep Positive & Negative only)":
                            df = df[df['sentiment_label'] != 'Netral'].reset_index(drop=True)
                        else:
                            df['sentiment_label'] = df['sentiment_label'].replace('Netral', 'Positif')

                        st.session_state['df_exploded'] = df
                        st.session_state['labeling_done'] = True
                        st.rerun()
        else:
            df = st.session_state['df_exploded']
            st.success("Annotation complete — polarity and aspects are attached to every segment.", icon="✅")

            if st.button("Re-annotate dataset", type="secondary"):
                st.session_state['labeling_done'] = False
                st.session_state['df_neutral_handled'] = None
                st.session_state['neutral_action'] = None
                if 'sentiment_label' in st.session_state['df_exploded'].columns:
                    st.session_state['df_exploded'].drop(columns=['sentiment_label', 'aspect_list'], inplace=True, errors='ignore')
                st.rerun()

            n_pos = int((df['sentiment_label'] == 'Positif').sum())
            n_neg = int((df['sentiment_label'] == 'Negatif').sum())
            render_kpi_grid([
                kpi_card(f"{len(df):,}", "Labeled segments", "ready for training", "blue", PALETTE["info"]),
                kpi_card(f"{n_pos:,}", "Positive", f"{n_pos / max(len(df), 1):.0%} of corpus", "green", PALETTE["positive"]),
                kpi_card(f"{n_neg:,}", "Negative", f"{n_neg / max(len(df), 1):.0%} of corpus", "red", PALETTE["negative"]),
            ])

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("##### Polarity share")
                fig, ax = plt.subplots(figsize=(4, 3.4))
                fig.patch.set_alpha(0.0)
                vals = df['sentiment_label'].value_counts()
                colors_pie = [PALETTE['positive'] if lab == 'Positif' else PALETTE['negative'] for lab in vals.index]
                _w, _t, autotexts = ax.pie(
                    vals.values, labels=vals.index, autopct='%1.1f%%',
                    colors=colors_pie, startangle=90,
                    textprops=dict(color=INK, fontsize=9, fontweight='bold'),
                    wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2),
                )
                for t in autotexts:
                    t.set_fontsize(8)
                    t.set_color("#FFFFFF")
                fig.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            with c2:
                st.markdown("##### Aspect frequency")
                df_asp = df.explode('aspect_list')
                st.bar_chart(df_asp['aspect_list'].value_counts(), use_container_width=True)
            with c3:
                st.markdown("##### Class quantity")
                st.bar_chart(df['sentiment_label'].value_counts(), use_container_width=True)

            with st.expander("Preview — 10 annotated samples"):
                st.dataframe(df[['segment', 'sentiment_label', 'aspect_list']].head(10), use_container_width=True)

            neutral_df = st.session_state.get('df_neutral_handled')
            if neutral_df is not None and not neutral_df.empty:
                st.info(
                    f"**{len(neutral_df)}** neutral segment(s) handled via: {st.session_state.get('neutral_action')}.",
                    icon="ℹ️",
                )

            st.divider()
            st.download_button(
                "Download annotated CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="hasil_pelabelan_dan_aspek_mbg.csv",
                mime="text/csv",
            )

        if 'sentiment_label' in st.session_state['df_exploded'].columns:
            st.button("Continue to modeling →", type="primary", on_click=set_page, args=(PAGES[3],))
    else:
        st.warning("Complete preprocessing before labeling.", icon="⚠️")

# ============================================================ 04 MODELING
elif menu == PAGES[3]:
    section_header(
        "04 — Model training",
        "Multi-scenario TF-IDF benchmark",
        "Three stratified splits — 70:30, 80:20, 90:10 — over TF-IDF (1–2 grams) features, "
        "comparing MultinomialNB vs LinearSVC. The 80:20 split is promoted as the baseline.",
    )

    df_exp = st.session_state.get('df_exploded')
    if df_exp is not None and 'sentiment_label' in df_exp.columns:
        if 'model_nb' not in st.session_state and os.path.exists('saved_model_data.joblib'):
            try:
                saved = joblib.load('saved_model_data.joblib')
                for k in ['model_nb', 'model_svm', 'vectorizer', 'test_data_eval', 'hasil_skenario']:
                    if k in saved:
                        st.session_state[k] = saved[k]
            except Exception:
                pass

        df_model = df_exp.copy()

        if st.button("Run multi-scenario training", type="primary"):
            with st.spinner("Training MultinomialNB & LinearSVC across 3 split ratios…"):
                X = df_model['segment']
                y = df_model['sentiment_label']
                skenario_splits = {"70:30": 0.3, "80:20": 0.2, "90:10": 0.1}
                hasil_skenario = {}
                pb = st.progress(0)
                progress_step = 0

                for name, test_size in skenario_splits.items():
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=test_size, random_state=42, stratify=y
                    )
                    tfidf = TfidfVectorizer(**TFIDF_PARAMS)
                    X_train_vec = tfidf.fit_transform(X_train)
                    X_test_vec = tfidf.transform(X_test)

                    t_nb = time.perf_counter()
                    nb = MultinomialNB()
                    nb.fit(X_train_vec, y_train)
                    t_nb = time.perf_counter() - t_nb
                    y_pred_nb = nb.predict(X_test_vec)
                    progress_step += 15
                    pb.progress(progress_step)

                    t_svm = time.perf_counter()
                    svm = LinearSVC()
                    svm.fit(X_train_vec, y_train)
                    t_svm = time.perf_counter() - t_svm
                    y_pred_svm = svm.predict(X_test_vec)
                    progress_step += 15
                    pb.progress(progress_step)

                    test_df = df_model.loc[X_test.index].copy()
                    test_df['y_true'] = y_test.values
                    test_df['pred_nb'] = y_pred_nb
                    test_df['pred_svm'] = y_pred_svm

                    hasil_skenario[name] = {
                        'model_nb': nb, 'model_svm': svm, 'vectorizer': tfidf,
                        'y_test': y_test, 'y_pred_nb': y_pred_nb, 'y_pred_svm': y_pred_svm,
                        't_nb': t_nb, 't_svm': t_svm, 'test_data_eval': test_df,
                    }
                    if name == "80:20":
                        st.session_state['model_nb'] = nb
                        st.session_state['model_svm'] = svm
                        st.session_state['vectorizer'] = tfidf
                        st.session_state['test_data_eval'] = test_df

                pb.progress(100)
                st.session_state['hasil_skenario'] = hasil_skenario
                try:
                    joblib.dump({
                        'model_nb': st.session_state['model_nb'],
                        'model_svm': st.session_state['model_svm'],
                        'vectorizer': st.session_state['vectorizer'],
                        'test_data_eval': st.session_state['test_data_eval'],
                        'hasil_skenario': hasil_skenario,
                    }, 'saved_model_data.joblib')
                    st.success("Training complete — bundle saved to `saved_model_data.joblib`.", icon="✅")
                except Exception:
                    st.success("Training complete.", icon="✅")

        if 'hasil_skenario' in st.session_state:
            st.divider()
            section_header("Results", "Multi-scenario evaluation matrix",
                           "Accuracy, precision, recall, F1 (weighted), training latency, and confusion matrices per split.")
            tab70, tab80, tab90 = st.tabs(["Split 70:30", "Split 80:20 · baseline", "Split 90:10"])
            tabs_dict = {"70:30": tab70, "80:20": tab80, "90:10": tab90}

            for split_name, tab in tabs_dict.items():
                with tab:
                    data = st.session_state['hasil_skenario'][split_name]
                    y_t, p_nb, p_svm = data['y_test'], data['y_pred_nb'], data['y_pred_svm']
                    col_eval1, col_eval2 = st.columns(2)
                    labels_cm = sorted(pd.concat([pd.Series(y_t), pd.Series(p_nb), pd.Series(p_svm)]).unique())

                    with col_eval1:
                        st.markdown("##### MultinomialNB")
                        metrics_nb = {
                            "Model": "MultinomialNB",
                            "Accuracy": accuracy_score(y_t, p_nb),
                            "Precision": precision_score(y_t, p_nb, average='weighted', zero_division=0),
                            "Recall": recall_score(y_t, p_nb, average='weighted', zero_division=0),
                            "F1-score": f1_score(y_t, p_nb, average='weighted', zero_division=0),
                            "Train time (s)": round(data['t_nb'], 4),
                        }
                        st.dataframe(pd.DataFrame([metrics_nb]).set_index("Model").style.format("{:.4f}"), use_container_width=True)
                        fig_nb, ax_nb = plt.subplots(figsize=(4.5, 3.5))
                        fig_nb.patch.set_alpha(0.0)
                        sns.heatmap(
                            confusion_matrix(y_t, p_nb, labels=labels_cm), annot=True, fmt='d',
                            cmap=sns.light_palette(PALETTE["info"], as_cmap=True),
                            xticklabels=labels_cm, yticklabels=labels_cm, ax=ax_nb,
                            cbar=False, linewidths=1, linecolor="white",
                        )
                        ax_nb.set_title(f"Confusion matrix · NB ({split_name})", fontsize=10, fontweight='bold', color=INK)
                        ax_nb.set_xlabel("Predicted", color=PALETTE["muted"])
                        ax_nb.set_ylabel("Actual", color=PALETTE["muted"])
                        fig_nb.tight_layout()
                        st.pyplot(fig_nb, use_container_width=True)
                        plt.close(fig_nb)

                    with col_eval2:
                        st.markdown("##### LinearSVC")
                        metrics_svm = {
                            "Model": "LinearSVC",
                            "Accuracy": accuracy_score(y_t, p_svm),
                            "Precision": precision_score(y_t, p_svm, average='weighted', zero_division=0),
                            "Recall": recall_score(y_t, p_svm, average='weighted', zero_division=0),
                            "F1-score": f1_score(y_t, p_svm, average='weighted', zero_division=0),
                            "Train time (s)": round(data['t_svm'], 4),
                        }
                        st.dataframe(pd.DataFrame([metrics_svm]).set_index("Model").style.format("{:.4f}"), use_container_width=True)
                        fig_svm, ax_svm = plt.subplots(figsize=(4.5, 3.5))
                        fig_svm.patch.set_alpha(0.0)
                        sns.heatmap(
                            confusion_matrix(y_t, p_svm, labels=labels_cm), annot=True, fmt='d',
                            cmap=sns.light_palette(PALETTE["positive"], as_cmap=True),
                            xticklabels=labels_cm, yticklabels=labels_cm, ax=ax_svm,
                            cbar=False, linewidths=1, linecolor="white",
                        )
                        ax_svm.set_title(f"Confusion matrix · LinearSVC ({split_name})", fontsize=10, fontweight='bold', color=INK)
                        ax_svm.set_xlabel("Predicted", color=PALETTE["muted"])
                        ax_svm.set_ylabel("Actual", color=PALETTE["muted"])
                        fig_svm.tight_layout()
                        st.pyplot(fig_svm, use_container_width=True)
                        plt.close(fig_svm)

            st.button("Continue to aspect evaluation →", type="primary", on_click=set_page, args=(PAGES[4],))
    else:
        st.warning("Run labeling (module 03) before training.", icon="⚠️")

# ============================================================ 05 EVALUASI
elif menu == PAGES[4]:
    section_header(
        "05 — Aspect-level evaluation",
        "Benchmark NB vs LinearSVC per aspect",
        "The baseline split is exploded on `aspect_list` so each aspect is scored independently. "
        "Percentages are static text — never color-only.",
    )

    if 'hasil_skenario' in st.session_state:
        skenario_options = list(st.session_state['hasil_skenario'].keys())
        selected_scenario = st.selectbox(
            "Split scenario",
            options=skenario_options,
            index=1 if len(skenario_options) > 1 else 0,
        )

        data_eval = st.session_state['hasil_skenario'][selected_scenario]
        df_eval = data_eval['test_data_eval']
        df_exp_eval = df_eval.explode('aspect_list')

        aspect_metrics = []
        unique_aspects = [a for a in df_exp_eval['aspect_list'].unique() if pd.notna(a)]
        for asp in unique_aspects:
            sub = df_exp_eval[df_exp_eval['aspect_list'] == asp]
            if len(sub) > 0:
                aspect_metrics.append({
                    'Aspect': asp,
                    'Test rows': len(sub),
                    'Accuracy NB': accuracy_score(sub['y_true'], sub['pred_nb']),
                    'F1 NB': f1_score(sub['y_true'], sub['pred_nb'], average='weighted', zero_division=0),
                    'Accuracy LinearSVC': accuracy_score(sub['y_true'], sub['pred_svm']),
                    'F1 LinearSVC': f1_score(sub['y_true'], sub['pred_svm'], average='weighted', zero_division=0),
                })

        df_asp_met = pd.DataFrame(aspect_metrics)
        if not df_asp_met.empty:
            df_asp_met = df_asp_met.sort_values('Test rows', ascending=False)
            fmt_cols = {c: '{:.2%}' for c in df_asp_met.columns if 'Accuracy' in c or 'F1' in c}
            st.dataframe(df_asp_met.style.format(fmt_cols), use_container_width=True)

            fig_asp, ax_asp = plt.subplots(figsize=(8, 4))
            fig_asp.patch.set_alpha(0.0)
            df_plot = df_asp_met.melt(id_vars=['Aspect'], value_vars=['Accuracy NB', 'Accuracy LinearSVC'],
                                      var_name='Model', value_name='Accuracy')
            sns.barplot(data=df_plot, x='Aspect', y='Accuracy', hue='Model',
                        palette=[PALETTE["info"], PALETTE["positive"]], ax=ax_asp,
                        edgecolor="white", linewidth=1, width=0.55)
            ax_asp.set_ylim(0, 1.12)
            for container in ax_asp.containers:
                ax_asp.bar_label(container, fmt='%.0%%', padding=4, fontsize=8, color=PALETTE["muted"])
            ax_asp.set_title(f"Accuracy: NB vs LinearSVC per aspect ({selected_scenario})",
                             fontweight='bold', color=INK)
            ax_asp.set_xlabel('')
            ax_asp.yaxis.grid(True, linestyle='--', alpha=0.9)
            ax_asp.set_axisbelow(True)
            for spine in ['top', 'right']:
                ax_asp.spines[spine].set_visible(False)
            fig_asp.tight_layout()
            st.pyplot(fig_asp, use_container_width=True)
            plt.close(fig_asp)

        st.button("Go to realtime testing →", type="primary", on_click=set_page, args=(PAGES[5],))
    else:
        st.warning("Train a model in module 04 first.", icon="⚠️")

# ============================================================ 06 REALTIME
elif menu == PAGES[5]:
    section_header(
        "06 — Realtime inference",
        "Spot-check the trained baseline",
        "Uses the promoted 80:20 bundle (or the freshly trained model in this session). "
        "For batch evaluation with metrics, use the standalone demo console.",
    )

    if 'model_nb' not in st.session_state or 'model_svm' not in st.session_state:
        st.warning("Train a model in module 04 first.", icon="⚠️")
    else:
        raw_text = st.text_area("Sentences (one per line)", height=150,
                                placeholder="menu MBG lezat dan bergizi\ndistribusi terlambat dua jam")
        if st.button("Run realtime inference", type="primary"):
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            if lines:
                with st.spinner(f"Analyzing {len(lines)} sentence(s)…"):
                    df_res = analyze_texts(
                        lines, st.session_state['model_nb'], st.session_state['model_svm'],
                        st.session_state['vectorizer'], norm_dict, final_stopwords, stemmer,
                    )
                pos = int((df_res['Prediksi SVM'] == 'Positif').sum())
                render_kpi_grid([
                    kpi_card(f"{len(df_res)}", "Segments", f"from {len(lines)} input(s)", "blue", PALETTE["info"]),
                    kpi_card(f"{pos}", "Positive · LinearSVC", f"{pos / max(len(df_res), 1):.0%}", "green", PALETTE["positive"]),
                    kpi_card(f"{len(df_res) - pos}", "Negative · LinearSVC", f"{(len(df_res) - pos) / max(len(df_res), 1):.0%}", "red", PALETTE["negative"]),
                ])
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("Input is empty — paste at least one sentence.", icon="⚠️")

st.caption("ABSA MBG · Research pipeline · RoBERTa annotation · TF-IDF + MNB / LinearSVC · UNNES")
