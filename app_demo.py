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
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from src.resources import load_nlp_resources, load_normalization_dict
from src.model_utils import load_saved_model, analyze_texts
from src.ui import inject_custom_css, render_hero_banner, render_sidebar_haki, apply_matplotlib_style

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Analisis Sentimen MBG - Realtime Demo",
    page_icon="🍽️",
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
    title="🍽️ Analisis Sentimen Program Makan Bergizi Gratis (MBG)",
    subtitle="Pengujian Real-Time Aspect-Based Sentiment Analysis (ABSA) Menggunakan Machine Learning (Multinomial Naïve Bayes vs LinearSVC)",
    is_demo=True
)

# Sidebar Info HAKI & UNNES
render_sidebar_haki()

if model_data is None:
    st.error("Model Machine Learning belum dapat dimuat. Pastikan file `saved_model_data.joblib` tersedia atau rilis GitHub Release telah dibuat.")
    st.stop()

nb_model = model_data['model_nb']
svm_model = model_data['model_svm']
vec = model_data['vectorizer']

vocab_size = len(vec.vocabulary_)
classes = nb_model.classes_

# Model Metadata Card
st.markdown(f"""
<div style="background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.2); border-radius: 12px; padding: 14px 20px; margin-bottom: 24px; display: flex; flex-wrap: wrap; gap: 24px; align-items: center;">
    <div><span style="opacity: 0.7; font-size: 0.8rem; text-transform: uppercase; font-weight: 700;">Model Aktif</span><br><b style="font-size: 0.95rem;">MultinomialNB & LinearSVC</b></div>
    <div style="border-left: 1px solid rgba(128,128,128,0.2); padding-left: 20px;"><span style="opacity: 0.7; font-size: 0.8rem; text-transform: uppercase; font-weight: 700;">TF-IDF Vocabulary</span><br><b style="font-size: 0.95rem; color: #6366F1;">{vocab_size:,} Fitur</b></div>
    <div style="border-left: 1px solid rgba(128,128,128,0.2); padding-left: 20px;"><span style="opacity: 0.7; font-size: 0.8rem; text-transform: uppercase; font-weight: 700;">Kelas Prediksi</span><br><b style="font-size: 0.95rem; color: #10B981;">{' · '.join(classes)}</b></div>
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
        "Pilih Mode Input Pengujian:",
        ("✏️ Input Manual (Paste Teks)", "📄 Upload CSV File"),
        horizontal=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if "Manual" in mode:
        st.info("💡 **Panduan Input:** Masukkan satu kalimat per baris. Untuk menguji akurasi otomatis, tambahkan label di akhir kalimat dengan separator `|` (contoh: `menu MBG sangat lezat dan bergizi | Positif`).")

        raw = st.text_area(
            "Masukkan Kalimat Uji (Satu per Baris):",
            height=220,
            placeholder="makanan bergizi enak dan porsinya cukup untuk anak sekolah | Positif\ndistribusi makanan sering telat siswa menunggu berjam-jam | Negatif\ndana MBG dikorupsi dan dimarkup oknum tidak bertanggung jawab | Negatif\nmenu MBG lezat dan higienis sangat membantu gizi siswa | Positif",
            label_visibility="collapsed"
        )

        col_btn1, _ = st.columns([1, 3])
        with col_btn1:
            run = st.button("🚀 Analisis Teks Real-Time", use_container_width=True)

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
                st.warning("⚠️ Teks pengujian tidak boleh kosong.")

    else:
        st.info("📄 **Format File CSV:** Kolom wajib bernama `full_text`. Kolom opsional `label` (berisi 'Positif' atau 'Negatif') jika ingin menghitung evaluasi akurasi.")

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
                file_name="template_pengujian_mbg.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_up:
            uploaded_test = st.file_uploader("Upload CSV Pengujian:", type="csv", label_visibility="collapsed")

        if st.button("🚀 Analisis Seluruh Dataset CSV", use_container_width=True):
            if uploaded_test:
                df_csv = pd.read_csv(uploaded_test)
                if 'full_text' not in df_csv.columns:
                    st.error("❌ Kolom wajib 'full_text' tidak ditemukan dalam file CSV.")
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
                st.warning("⚠️ Silakan unggah file CSV terlebih dahulu.")

else:
    col_ulang, _ = st.columns([1.5, 4.5])
    with col_ulang:
        if st.button("🔄 Reset / Ulangi Pengujian", use_container_width=True):
            st.session_state.update({
                'rt_analyzed': False, 'rt_texts': [],
                'rt_labels': [], 'rt_has_labels': False, 'df_results': None
            })
            st.rerun()

    texts = st.session_state['rt_texts']
    labels = st.session_state['rt_labels']
    has_labels = st.session_state['rt_has_labels']

    if st.session_state['df_results'] is None:
        progress_bar = st.progress(0, text=f"Menganalisis {len(texts)} kalimat uji...")
        df_res = analyze_texts(texts, nb_model, svm_model, vec, norm_dict, final_stopwords, stemmer, progress_bar)
        progress_bar.empty()
        st.session_state['df_results'] = df_res
    else:
        df_res = st.session_state['df_results']

    if df_res.empty:
        st.warning("⚠️ Tidak ada segmen opini valid yang terdeteksi.")
        st.stop()

    total_seg = len(df_res)
    pos_svm = (df_res['Prediksi SVM'] == 'Positif').sum()
    neg_svm = (df_res['Prediksi SVM'] == 'Negatif').sum()
    pos_nb = (df_res['Prediksi NB'] == 'Positif').sum()
    neg_nb = (df_res['Prediksi NB'] == 'Negatif').sum()
    unique_texts = df_res['Teks Asli'].nunique()

    # Metric Dashboard Grid
    st.markdown(f"""
    <div class="metric-grid-4">
        <div class="metric-card-pro">
            <div class="metric-num txt-indigo">{unique_texts}</div>
            <div class="metric-txt">Kalimat Diuji</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-amber">{total_seg}</div>
            <div class="metric-txt">Total Segmen Opini</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-emerald">{pos_svm}</div>
            <div class="metric-txt">Positif (LinearSVC)</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-rose">{neg_svm}</div>
            <div class="metric-txt">Negatif (LinearSVC)</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-emerald">{pos_nb}</div>
            <div class="metric-txt">Positif (Naive Bayes)</div>
        </div>
        <div class="metric-card-pro">
            <div class="metric-num txt-rose">{neg_nb}</div>
            <div class="metric-txt">Negatif (Naive Bayes)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs Hasil Analisis
    tab_table, tab_charts, tab_eval = st.tabs(["📋 Tabel Hasil Analisis", "📊 Visualisasi", "🎯 Evaluasi Akurasi"])

    with tab_table:
        st.subheader("📋 Detail Segmentasi Kalimat & Prediksi Sentimen-Aspek")
        st.dataframe(df_res, use_container_width=True, height=360)

    with tab_charts:
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.markdown("##### 🥧 Perbandingan Distribusi Sentimen")
            fig_pie, axes = plt.subplots(1, 2, figsize=(8, 3.8))
            fig_pie.patch.set_alpha(0.0)
            
            for ax, col_pred, name in [(axes[0], 'Prediksi SVM', 'LinearSVC'), (axes[1], 'Prediksi NB', 'MultinomialNB')]:
                counts = df_res[col_pred].value_counts()
                colors = ['#10B981' if l == 'Positif' else '#EF4444' for l in counts.index]
                ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%', colors=colors, startangle=90, wedgeprops=dict(width=0.4, edgecolor='white'))
                ax.set_title(name, fontsize=11, fontweight='bold')
            st.pyplot(fig_pie)
            plt.close(fig_pie)

        with c_chart2:
            st.markdown("##### 📊 Distribusi Sentimen Per Aspek (LinearSVC)")
            df_asp = df_res[~df_res['Aspek'].str.contains('Lainnya', na=False)].copy()
            if not df_asp.empty:
                pivot = df_asp.groupby(['Aspek', 'Prediksi SVM']).size().unstack(fill_value=0)
                fig_bar, ax_bar = plt.subplots(figsize=(6, 3.8))
                fig_bar.patch.set_alpha(0.0)
                colors_bar = {'Positif': '#10B981', 'Negatif': '#EF4444'}
                pivot.plot(kind='bar', ax=ax_bar, color=[colors_bar.get(c, '#6366F1') for c in pivot.columns], width=0.55)
                ax_bar.set_title("Sentimen per Aspek", fontweight='bold', fontsize=11)
                ax_bar.set_xlabel('')
                ax_bar.set_ylabel('Jumlah Segmen')
                plt.xticks(rotation=0)
                st.pyplot(fig_bar)
                plt.close(fig_bar)
            else:
                st.info("Belum ada segmen aspek spesifik terdeteksi.")

    with tab_eval:
        if has_labels and any(l is not None for l in labels):
            st.subheader("🎯 Evaluasi Akurasi Pengujian Real-Time")

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
                    'Status LinearSVC': '✅ Benar' if ps == labels[i] else '❌ Salah',
                    'Status NaiveBayes': '✅ Benar' if pn == labels[i] else '❌ Salah',
                })

            if eval_data:
                df_eval = pd.DataFrame(eval_data)
                acc_svm = accuracy_score(df_eval['Label Sebenarnya'], df_eval['Prediksi LinearSVC'])
                acc_nb = accuracy_score(df_eval['Label Sebenarnya'], df_eval['Prediksi NaiveBayes'])
                f1_svm = f1_score(df_eval['Label Sebenarnya'], df_eval['Prediksi LinearSVC'], average='weighted', zero_division=0)
                f1_nb = f1_score(df_eval['Label Sebenarnya'], df_eval['Prediksi NaiveBayes'], average='weighted', zero_division=0)

                m1, m2, m3, m4 = st.columns(4)
                with m1: st.metric("Akurasi LinearSVC", f"{acc_svm:.1%}")
                with m2: st.metric("Akurasi Multinomial NB", f"{acc_nb:.1%}")
                with m3: st.metric("F1-Score LinearSVC", f"{f1_svm:.1%}")
                with m4: st.metric("F1-Score Multinomial NB", f"{f1_nb:.1%}")

                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df_eval, use_container_width=True)
        else:
            st.info("💡 **Tips:** Untuk melihat evaluasi akurasi otomatis, berikan label pada kalimat uji dengan format `kalimat | Positif` atau upload file CSV dengan kolom `label`.")

    st.divider()
    st.download_button(
        "📥 Download Hasil Analisis Lengkap (CSV)",
        data=df_res.to_csv(index=False).encode('utf-8'),
        file_name="hasil_analisis_realtime_mbg.csv",
        mime="text/csv"
    )
