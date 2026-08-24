"""
Aplikasi Pengujian Real-Time ABSA MBG (Demo Version) - Swiss Technical Print (Light Edition)
Memuat model terlatih dari joblib (auto-download jika di-deploy di Streamlit Cloud).
Jalankan: streamlit run app_demo.py
"""

import warnings
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from src.resources import load_nlp_resources, load_normalization_dict
from src.model_utils import load_saved_model, analyze_texts
from src.ui import inject_custom_css, render_hero_banner, render_sidebar_haki, apply_matplotlib_style

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="ABSA MBG // Realtime Inference Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom UI styles & setup matplotlib
inject_custom_css()
apply_matplotlib_style()

stemmer, final_stopwords, negation_words = load_nlp_resources()
norm_dict = load_normalization_dict()
model_data = load_saved_model()

# Header Hero Banner
render_hero_banner(
    title="Aspect-Based Sentiment Analysis (ABSA) // Program MBG",
    subtitle="High-Precision Real-Time Opinion Mining & Machine Learning Benchmark (Multinomial Naïve Bayes vs LinearSVC)",
    is_demo=True
)

# Sidebar Info HAKI & UNNES
render_sidebar_haki()

if model_data is None:
    st.error("[ERROR // MODEL_UNAVAILABLE] Model Machine Learning belum dapat dimuat. Pastikan file saved_model_data.joblib tersedia.")
    st.stop()

nb_model = model_data['model_nb']
svm_model = model_data['model_svm']
vec = model_data['vectorizer']

vocab_size = len(vec.vocabulary_)
classes = nb_model.classes_

# Telemetry Metadata Card (Light)
st.markdown(f"""
<div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 2px; padding: 14px 20px; margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 24px; align-items: center;">
    <div><span style="font-family: 'JetBrains Mono', monospace; color: #64748B; font-size: 0.7rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">[ ACTIVE_ARCHITECTURES ]</span><br><b style="font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; color: #0F172A;">MultinomialNB & LinearSVC</b></div>
    <div style="border-left: 1px solid #CBD5E1; padding-left: 20px;"><span style="font-family: 'JetBrains Mono', monospace; color: #64748B; font-size: 0.7rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">[ TFIDF_VOCABULARY_SIZE ]</span><br><b style="font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; color: #0284C7;">{vocab_size:,} FEATURES</b></div>
    <div style="border-left: 1px solid #CBD5E1; padding-left: 20px;"><span style="font-family: 'JetBrains Mono', monospace; color: #64748B; font-size: 0.7rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">[ TARGET_CLASSES ]</span><br><b style="font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; color: #16A34A;">{' // '.join(classes).upper()}</b></div>
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

if not st.session_state['rt_analyzed']:
    mode = st.radio(
        "[ INGESTION_MODE ] Pilih Metode Input Data:",
        ("Manual Text Batch (Line-by-Line)", "Structured CSV Upload"),
        horizontal=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if "Manual" in mode:
        st.info("**Panduan Input:** Masukkan 1 kalimat per baris. Untuk benchmark akurasi otomatis, sertakan label di akhir kalimat dengan pemisah `|` (contoh: `menu MBG sangat lezat dan bergizi | Positif`).")

        raw = st.text_area(
            "INPUT_STREAM:",
            height=190,
            placeholder="makanan bergizi enak dan porsinya cukup untuk anak sekolah | Positif\ndistribusi makanan sering telat siswa menunggu berjam-jam | Negatif\ndana MBG dikorupsi dan dimarkup oknum tidak bertanggung jawab | Negatif\nmenu MBG lezat dan higienis sangat membantu gizi siswa | Positif",
            label_visibility="collapsed"
        )

        col_btn1, _ = st.columns([1.2, 2.8])
        with col_btn1:
            run = st.button("EXECUTE REAL-TIME INFERENCE", use_container_width=True)

        if run:
            if raw.strip():
                texts, labels, has_labels = [], [], False
                for line in raw.split('\n'):
                    line = line.strip()
                    if not line: continue
                    if '|' in line:
                        parts = line.split('|', 1)
                        texts.append(parts[0].strip())
                        labels.append(parts[1].strip().capitalize())
                        has_labels = True
                    else:
                        texts.append(line)
                        labels.append(None)
                st.session_state.update({
                    'rt_texts': texts, 'rt_labels': labels,
                    'rt_has_labels': has_labels, 'rt_analyzed': True
                })
                st.rerun()
            else:
                st.warning("[WARNING] Input stream kosong. Masukkan teks pengujian.")

    else:
        st.info("**Format Skema CSV:** Kolom wajib `full_text`. Kolom opsional `label` ('Positif' / 'Negatif') untuk evaluasi metrik.")

        template_df = pd.DataFrame({
            "full_text": [
                "makanan bergizi enak dan porsinya cukup untuk anak sekolah",
                "distribusi makanan sering telat siswa menunggu berjam-jam",
                "dana MBG dikorupsi dan dimarkup oknum tidak bertanggung jawab",
                "kualitas makanan bagus dan anak kenyang setelah makan",
            ],
            "label": ["Positif", "Negatif", "Negatif", "Positif"]
        })

        col_dl, col_up = st.columns([1, 2])
        with col_dl:
            st.download_button(
                "DOWNLOAD TEMPLATE CSV",
                data=template_df.to_csv(index=False).encode('utf-8'),
                file_name="template_pengujian_mbg.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_up:
            uploaded_test = st.file_uploader("UPLOAD_CSV_FILE:", type="csv", label_visibility="collapsed")

        if st.button("EXECUTE BATCH DATASET INFERENCE", use_container_width=True):
            if uploaded_test:
                df_csv = pd.read_csv(uploaded_test)
                if 'full_text' not in df_csv.columns:
                    st.error("[SCHEMA_ERROR] Kolom wajib 'full_text' tidak ditemukan dalam file CSV.")
                else:
                    texts = df_csv['full_text'].dropna().astype(str).tolist()
                    labels = df_csv['label'].tolist() if 'label' in df_csv.columns else [None]*len(texts)
                    has_labels = 'label' in df_csv.columns
                    st.session_state.update({
                        'rt_texts': texts, 'rt_labels': labels,
                        'rt_has_labels': has_labels, 'rt_analyzed': True
                    })
                    st.rerun()
            else:
                st.warning("[WARNING] Unggah file CSV terlebih dahulu.")

else:
    col_ulang, _ = st.columns([1.5, 4.5])
    with col_ulang:
        if st.button("RESET EXPERIMENT SESSION", use_container_width=True):
            st.session_state.update({
                'rt_analyzed': False, 'rt_texts': [],
                'rt_labels': [], 'rt_has_labels': False, 'df_results': None
            })
            st.rerun()

    texts = st.session_state['rt_texts']
    labels = st.session_state['rt_labels']
    has_labels = st.session_state['rt_has_labels']

    if st.session_state['df_results'] is None:
        progress_bar = st.progress(0, text=f"[INFERENCE_RUNNING] Analyzing {len(texts)} samples...")
        df_res = analyze_texts(texts, nb_model, svm_model, vec, norm_dict, final_stopwords, stemmer, progress_bar)
        progress_bar.empty()
        st.session_state['df_results'] = df_res
    else:
        df_res = st.session_state['df_results']

    if df_res.empty:
        st.warning("[WARNING] Tidak ada segmen opini valid yang terdeteksi.")
        st.stop()

    total_seg = len(df_res)
    pos_svm = (df_res['Prediksi SVM'] == 'Positif').sum()
    neg_svm = (df_res['Prediksi SVM'] == 'Negatif').sum()
    pos_nb = (df_res['Prediksi NB'] == 'Positif').sum()
    neg_nb = (df_res['Prediksi NB'] == 'Negatif').sum()
    unique_texts = df_res['Teks Asli'].nunique()

    # Telemetry Bento Grid (Light)
    st.markdown(f"""
    <div class="metric-grid-4">
        <div class="metric-card-pro">
            <div class="metric-num txt-indigo">{unique_texts}</div>
            <div class="metric-txt">[ SAMPLES_EVALUATED ]</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-amber">{total_seg}</div>
            <div class="metric-txt">[ OPINION_SEGMENTS ]</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-emerald">{pos_svm}</div>
            <div class="metric-txt">[ POSITIVE_LSVC ]</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-rose">{neg_svm}</div>
            <div class="metric-txt">[ NEGATIVE_LSVC ]</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-emerald">{pos_nb}</div>
            <div class="metric-txt">[ POSITIVE_MNB ]</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-rose">{neg_nb}</div>
            <div class="metric-txt">[ NEGATIVE_MNB ]</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Technical Tabs
    tab_table, tab_charts, tab_eval = st.tabs(["[ 01 // DATA_MATRIX ]", "[ 02 // VISUAL_TELEMETRY ]", "[ 03 // BENCHMARK_EVALUATION ]"])

    with tab_table:
        st.subheader("Detail Segmentasi Konjungsi & Prediksi Sentimen-Aspek")
        st.dataframe(df_res, use_container_width=True, height=360)

    with tab_charts:
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.markdown("##### [ TELEMETRY // SENTIMENT_DISTRIBUTION ]")
            fig_pie, axes = plt.subplots(1, 2, figsize=(8, 3.8))
            fig_pie.patch.set_alpha(0.0)
            
            for ax, col_pred, name in [(axes[0], 'Prediksi SVM', 'LinearSVC'), (axes[1], 'Prediksi NB', 'MultinomialNB')]:
                counts = df_res[col_pred].value_counts()
                colors = ['#16A34A' if l == 'Positif' else '#DC2626' for l in counts.index]
                ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%', colors=colors, startangle=90, 
                       textprops=dict(color='#0F172A', fontfamily='JetBrains Mono', fontsize=9, fontweight='bold'),
                       wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=1.5))
                ax.set_title(name, fontsize=11, fontweight='bold', color='#0F172A', fontfamily='JetBrains Mono')
            st.pyplot(fig_pie)
            plt.close(fig_pie)

        with c_chart2:
            st.markdown("##### [ TELEMETRY // ASPECT_POLARITY_LSVC ]")
            df_asp = df_res[~df_res['Aspek'].str.contains('Lainnya', na=False)].copy()
            if not df_asp.empty:
                pivot = df_asp.groupby(['Aspek', 'Prediksi SVM']).size().unstack(fill_value=0)
                fig_bar, ax_bar = plt.subplots(figsize=(6, 3.8))
                fig_bar.patch.set_alpha(0.0)
                colors_bar = {'Positif': '#16A34A', 'Negatif': '#DC2626'}
                pivot.plot(kind='bar', ax=ax_bar, color=[colors_bar.get(c, '#0284C7') for c in pivot.columns], width=0.55, edgecolor='none')
                ax_bar.set_title("Sentimen per Aspek", fontweight='bold', fontsize=11, color='#0F172A', fontfamily='JetBrains Mono')
                ax_bar.set_xlabel('')
                ax_bar.set_ylabel('Jumlah Segmen', color='#475569', fontfamily='JetBrains Mono')
                ax_bar.spines['top'].set_visible(False)
                ax_bar.spines['right'].set_visible(False)
                ax_bar.spines['left'].set_color('#CBD5E1')
                ax_bar.spines['bottom'].set_color('#CBD5E1')
                plt.xticks(rotation=0, color='#0F172A', fontfamily='JetBrains Mono')
                plt.yticks(color='#475569', fontfamily='JetBrains Mono')
                st.pyplot(fig_bar)
                plt.close(fig_bar)
            else:
                st.info("[INFO] Belum ada segmen aspek spesifik terdeteksi.")

    with tab_eval:
        if has_labels and any(l is not None for l in labels):
            st.subheader("Benchmark Akurasi & Error Analysis")

            eval_data = []
            for i, text in enumerate(texts):
                if labels[i] is None: continue
                rows_t = df_res[df_res['Teks Asli'] == text]
                if rows_t.empty: continue
                ps = rows_t.iloc[0]['Prediksi SVM']
                pn = rows_t.iloc[0]['Prediksi NB']
                eval_data.append({
                    'Teks': text[:65] + '...' if len(text) > 65 else text,
                    'Label Sebenarnya': labels[i],
                    'Prediksi LinearSVC': ps,
                    'Prediksi NaiveBayes': pn,
                    'Status LinearSVC': 'MATCH' if ps == labels[i] else 'MISMATCH',
                    'Status NaiveBayes': 'MATCH' if pn == labels[i] else 'MISMATCH',
                })

            if eval_data:
                df_eval = pd.DataFrame(eval_data)
                acc_svm = accuracy_score(df_eval['Label Sebenarnya'], df_eval['Prediksi LinearSVC'])
                acc_nb = accuracy_score(df_eval['Label Sebenarnya'], df_eval['Prediksi NaiveBayes'])
                f1_svm = f1_score(df_eval['Label Sebenarnya'], df_eval['Prediksi LinearSVC'], average='weighted', zero_division=0)
                f1_nb = f1_score(df_eval['Label Sebenarnya'], df_eval['Prediksi NaiveBayes'], average='weighted', zero_division=0)

                m1, m2, m3, m4 = st.columns(4)
                with m1: st.metric("ACCURACY (LSVC)", f"{acc_svm:.1%}")
                with m2: st.metric("ACCURACY (MNB)", f"{acc_nb:.1%}")
                with m3: st.metric("F1-SCORE (LSVC)", f"{f1_svm:.1%}")
                with m4: st.metric("F1-SCORE (MNB)", f"{f1_nb:.1%}")

                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df_eval, use_container_width=True)
        else:
            st.info("[INFO] Untuk melihat evaluasi akurasi otomatis, sertakan label pada kalimat uji dengan format `kalimat | Positif` atau upload file CSV dengan kolom `label`.")

    st.divider()
    st.download_button(
        "DOWNLOAD FULL CSV TELEMETRY",
        data=df_res.to_csv(index=False).encode('utf-8'),
        file_name="hasil_analisis_realtime_mbg.csv",
        mime="text/csv"
    )
