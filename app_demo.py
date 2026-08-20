"""
Aplikasi Pengujian Real-Time ABSA MBG (Demo Version)
Memuat model terlatih dari joblib (auto-download jika di-deploy di Streamlit Cloud).
Jalankan: streamlit run app_demo.py
"""

import warnings
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from src.resources import load_nlp_resources, load_normalization_dict
from src.model_utils import load_saved_model, analyze_texts

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Analisis Sentimen MBG - Realtime Demo",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.main-header {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #388BFD, #3FB950, #D29922);
}
.main-header h1 {
    font-size: 1.8rem;
    font-weight: 800;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.main-header p {
    font-size: 0.9rem;
    margin: 0;
    opacity: 0.8;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}
.metric-card {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.2;
}
.color-green { color: #28a745; }
.color-red { color: #dc3545; }
.metric-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 4px;
    opacity: 0.7;
}
</style>
""", unsafe_allow_html=True)

stemmer, final_stopwords, negation_words = load_nlp_resources()
norm_dict = load_normalization_dict()
model_data = load_saved_model()

# Header Utama
st.markdown("""
<div class="main-header">
    <h1>🍽️ Analisis Sentimen Program Makan Bergizi Gratis (MBG)</h1>
    <p>Pengujian real-time menggunakan model Multinomial Naïve Bayes & LinearSVC yang telah dilatih</p>
</div>
""", unsafe_allow_html=True)

if model_data is None:
    st.error("Model Machine Learning belum dapat dimuat. Pastikan file `saved_model_data.joblib` tersedia atau rilis GitHub Release telah dibuat.")
    st.stop()

nb_model = model_data['model_nb']
svm_model = model_data['model_svm']
vec = model_data['vectorizer']

vocab_size = len(vec.vocabulary_)
classes = nb_model.classes_
st.markdown(f"""
**Info Model:** MultinomialNB & LinearSVC &nbsp;|&nbsp; 
**TF-IDF Vocab:** {vocab_size:,} fitur &nbsp;|&nbsp; 
**Kelas Prediksi:** {' · '.join(classes)}
""")

st.divider()

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
        "Mode Input:",
        ("✏️ Input Manual (Paste Teks)", "📄 Upload CSV"),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if "Manual" in mode:
        st.info("**Panduan Input:** Satu kalimat per baris. Untuk evaluasi akurasi, tambahkan label dengan format `kalimat | Positif` atau `kalimat | Negatif`.")

        raw = st.text_area(
            "Masukkan kalimat uji:",
            height=240,
            placeholder="makanan bergizi enak dan porsinya cukup untuk anak sekolah | Positif\ndistribusi makanan sering telat siswa menunggu berjam-jam | Negatif\ndana MBG dikorupsi dan dimarkup oknum tidak bertanggung jawab | Negatif\nmenu MBG lezat dan higienis sangat membantu gizi siswa",
            label_visibility="collapsed"
        )

        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            run = st.button("🔍 Analisis Teks", use_container_width=True)

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
                st.warning("Teks tidak boleh kosong.")

    else:
        st.info("**Format CSV:** Kolom wajib: `full_text` (kalimat uji). Opsional kolom `label` (Positif/Negatif).")

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
                "📥 Download Template CSV",
                data=template_df.to_csv(index=False).encode('utf-8'),
                file_name="template_pengujian.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_up:
            uploaded_test = st.file_uploader("Upload CSV:", type="csv", label_visibility="collapsed")

        if st.button("🔍 Analisis CSV", use_container_width=True):
            if uploaded_test:
                df_csv = pd.read_csv(uploaded_test)
                if 'full_text' not in df_csv.columns:
                    st.error("Kolom 'full_text' tidak ditemukan.")
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
                st.warning("Upload CSV terlebih dahulu.")

else:
    col_ulang, _ = st.columns([1, 5])
    with col_ulang:
        if st.button("↩ Ulangi Analisis", use_container_width=True):
            st.session_state.update({
                'rt_analyzed': False, 'rt_texts': [],
                'rt_labels': [], 'rt_has_labels': False, 'df_results': None
            })
            st.rerun()

    texts = st.session_state['rt_texts']
    labels = st.session_state['rt_labels']
    has_labels = st.session_state['rt_has_labels']

    if st.session_state['df_results'] is None:
        progress_bar = st.progress(0, text=f"Memproses {len(texts)} kalimat...")
        df_res = analyze_texts(texts, nb_model, svm_model, vec, norm_dict, final_stopwords, stemmer, progress_bar)
        progress_bar.empty()
        st.session_state['df_results'] = df_res
    else:
        df_res = st.session_state['df_results']

    if df_res.empty:
        st.warning("Tidak ada segmen valid yang terdeteksi.")
        st.stop()

    total_seg = len(df_res)
    pos_svm = (df_res['Prediksi SVM'] == 'Positif').sum()
    neg_svm = (df_res['Prediksi SVM'] == 'Negatif').sum()
    pos_nb = (df_res['Prediksi NB'] == 'Positif').sum()
    neg_nb = (df_res['Prediksi NB'] == 'Negatif').sum()
    unique_texts = df_res['Teks Asli'].nunique()

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card"><div class="metric-value">{unique_texts}</div><div class="metric-label">Kalimat Uji</div></div>
        <div class="metric-card"><div class="metric-value">{total_seg}</div><div class="metric-label">Total Segmen</div></div>
        <div class="metric-card"><div class="metric-value color-green">{pos_svm}</div><div class="metric-label">Positif (SVM)</div></div>
        <div class="metric-card"><div class="metric-value color-red">{neg_svm}</div><div class="metric-label">Negatif (SVM)</div></div>
        <div class="metric-card"><div class="metric-value color-green">{pos_nb}</div><div class="metric-label">Positif (NB)</div></div>
        <div class="metric-card"><div class="metric-value color-red">{neg_nb}</div><div class="metric-label">Negatif (NB)</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Hasil Analisis Per Segmen")
    st.dataframe(df_res, use_container_width=True)

    if has_labels and any(l is not None for l in labels):
        st.divider()
        st.markdown("### 🎯 Evaluasi Akurasi Pengujian Real-Time")

        eval_data = []
        for i, text in enumerate(texts):
            if labels[i] is None: continue
            rows_t = df_res[df_res['Teks Asli'] == text]
            if rows_t.empty: continue
            ps = rows_t.iloc[0]['Prediksi SVM']
            pn = rows_t.iloc[0]['Prediksi NB']
            eval_data.append({
                'Teks': text[:70] + '...' if len(text) > 70 else text,
                'Label Sebenarnya': labels[i],
                'Prediksi SVM': ps,
                'Prediksi NB': pn,
                'SVM': '✅' if ps == labels[i] else '❌',
                'NB': '✅' if pn == labels[i] else '❌',
            })

        if eval_data:
            df_eval = pd.DataFrame(eval_data)
            acc_svm = accuracy_score(df_eval['Label Sebenarnya'], df_eval['Prediksi SVM'])
            acc_nb = accuracy_score(df_eval['Label Sebenarnya'], df_eval['Prediksi NB'])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Akurasi LinearSVC", f"{acc_svm:.1%}")
            with col2:
                st.metric("Akurasi Multinomial NB", f"{acc_nb:.1%}")

            st.dataframe(df_eval, use_container_width=True)

    st.divider()
    st.download_button(
        "📥 Download Semua Hasil Analisis (CSV)",
        data=df_res.to_csv(index=False).encode('utf-8'),
        file_name="hasil_analisis_realtime.csv",
        mime="text/csv"
    )
