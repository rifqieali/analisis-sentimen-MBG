"""
Aplikasi Pipeline Lengkap Analisis Sentimen Berbasis Aspek (ABSA) MBG
Menjalankan seluruh tahapan skripsi: Upload -> Preprocessing -> Labeling -> Training -> Evaluasi -> Real-Time
Jalankan: streamlit run app_pipeline.py
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
from wordcloud import WordCloud

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, classification_report, precision_score, recall_score,
    f1_score, confusion_matrix
)

# Import modul terstruktur dari src/
from src.constants import PAGES, TFIDF_PARAMS
from src.resources import (
    load_nlp_resources, load_normalization_dict,
    load_inset_lexicon, load_roberta_pipeline
)
from src.preprocessing import (
    clean_text, normalize_text, segmentasi_kalimat,
    stopword_and_stem, get_aspects, determine_sentiment_roberta
)
from src.model_utils import analyze_texts, load_saved_model

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Analisis Sentimen MBG - Pipeline Lengkap", layout="wide", page_icon="📑")

# Load NLP resources
stemmer, final_stopwords, negation_words = load_nlp_resources()
norm_dict = load_normalization_dict()
lexicon = load_inset_lexicon()

# ============================================================
# SESSION STATE & NAVIGASI
# ============================================================
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

st.title("Analisis Sentimen Program Makan Bergizi Gratis (MBG)")
st.markdown("Berbasis **Segmentasi Konjungsi**, **Sastrawi**, **RoBERTa Auto-Labeling**, dan **Machine Learning** (MultinomialNB vs LinearSVC)")

menu = st.sidebar.selectbox("Pilih Tahapan Pipeline", PAGES, key='current_page')

# ============================================================
# TAB 1: UPLOAD DATA
# ============================================================
if menu == PAGES[0]:
    st.header("Upload Dataset CSV")

    data_type = st.radio(
        "Jenis data yang diupload:",
        (
            "Data Mentah (Belum Preprocessing)", 
            "Data Hasil Preprocessing (Lewati ke Labeling)",
            "Data Sudah Dilabeli (Lihat Visualisasi & Modeling)"
        )
    )

    uploaded_file = st.file_uploader("Pilih file CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        if data_type == "Data Mentah (Belum Preprocessing)":
            st.session_state['df_raw'] = df
            st.session_state['df_exploded'] = None
            st.session_state['preprocessing_done'] = False
            st.session_state['labeling_done'] = False
            st.session_state['df_neutral_handled'] = None
            st.session_state['neutral_action'] = None
            st.success(f"Data mentah dimuat: **{len(df)}** baris.")
            st.dataframe(df.head())
            st.button("Lanjut ke Preprocessing →", on_click=set_page, args=(PAGES[1],))
        elif data_type == "Data Hasil Preprocessing (Lewati ke Labeling)":
            if 'segment' not in df.columns:
                st.error("Kolom 'segment' tidak ditemukan. Pastikan file hasil preprocessing memiliki kolom 'segment'.")
            else:
                st.session_state['df_exploded'] = df
                st.session_state['df_raw'] = None
                st.session_state['preprocessing_done'] = True
                st.session_state['labeling_done'] = False
                st.session_state['df_neutral_handled'] = None
                st.session_state['neutral_action'] = None
                st.success(f"Data preprocessing dimuat: **{len(df)}** segmen.")
                st.dataframe(df.head())
                st.button("Lanjut ke Labeling →", on_click=set_page, args=(PAGES[2],))
        else:
            required_cols = ['segment', 'sentiment_label', 'aspect_list']
            missing_cols = [c for c in required_cols if c not in df.columns]
            
            if missing_cols:
                st.error(f"Kolom tidak ditemukan: {', '.join(missing_cols)}. Pastikan file berlabel memiliki kolom tersebut.")
            else:
                def parse_aspect(x):
                    if isinstance(x, str):
                        try:
                            res = ast.literal_eval(x)
                            if isinstance(res, list): return res
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
                
                st.success(f"Data berlabel dimuat: **{len(df)}** segmen. Siap divisualisasikan dan dimodelkan!")
                st.dataframe(df.head())
                st.button("Lihat Visualisasi (Tab Labeling) →", on_click=set_page, args=(PAGES[2],))

# ============================================================
# TAB 2: PREPROCESSING & SEGMENTASI
# ============================================================
elif menu == PAGES[1]:
    st.header("Preprocessing & Segmentasi")
    st.warning("1 baris tweet dapat dipecah menjadi beberapa segmen berdasarkan konjungsi.")

    if st.session_state['df_raw'] is not None:
        df = st.session_state['df_raw'].copy()
        col_name = st.selectbox("Pilih kolom teks:", df.columns)

        if st.button("Mulai Preprocessing (Semua Data)"):
            with st.spinner("Menjalankan pipeline preprocessing bertahap..."):
                count_raw = len(df)
                
                # Filter duplikat
                df = df.drop_duplicates(subset=[col_name], keep='first').copy()
                df['doc_id'] = range(len(df))
                count_awal = len(df)

                # Cleaning
                df['text_clean'] = df[col_name].apply(clean_text)
                count_clean = len(df)

                # Normalisasi
                df['text_norm'] = df['text_clean'].apply(lambda x: normalize_text(x, norm_dict))
                count_norm = len(df)

                # Segmentasi
                df['segmen_list'] = df['text_norm'].apply(segmentasi_kalimat)
                df_exploded = df.explode('segmen_list').dropna(subset=['segmen_list'])
                df_exploded['segment'] = df_exploded['segmen_list'].astype(str).str.strip()
                df_exploded = df_exploded[df_exploded['segment'] != '']
                count_segmentasi = len(df_exploded)

                # Stopword removal & Stemming
                my_bar = st.progress(0)
                total_rows = count_segmentasi
                
                processed_segments = []
                for i, seg in enumerate(df_exploded['segment']):
                    stemmed = stopword_and_stem(seg, final_stopwords, stemmer)
                    processed_segments.append(stemmed)
                    
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
                    "norm": count_norm, "segmentasi": count_segmentasi, "final": count_final
                }

        if st.session_state.get('preprocessing_done', False):
            stats = st.session_state.get('prep_stats', {})
            if stats:
                st.success("Pipeline Preprocessing selesai!")
                st.markdown(f"""
                **Statistik Perubahan Jumlah Data:**
                * **Data Mentah Awal:** `{stats['raw']}` baris
                * **Setelah Filter Duplikat:** `{stats['awal']}` baris *(Dibuang {stats['raw'] - stats['awal']} baris)*
                * **Setelah Cleaning & Normalisasi:** `{stats['norm']}` baris
                * **Setelah Segmentasi (Pecah Konjungsi):** `{stats['segmentasi']}` segmen *(Bertambah {stats['segmentasi'] - stats['norm']} pecahan)*
                * **Final (Setelah Stopword & Stemming):** `{stats['final']}` segmen bersih *(Dibuang {stats['segmentasi'] - stats['final']} segmen kosong/tak bermakna)*
                """)

            st.divider()
            st.markdown("### Preview Hasil Data Akhir")
            st.dataframe(st.session_state['df_exploded'][['doc_id', col_name, 'segment']].head(10), use_container_width=True)

            csv_data = st.session_state['df_exploded'].to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Hasil Preprocessing (CSV)",
                data=csv_data,
                file_name="hasil_preprocessing.csv",
                mime="text/csv"
            )
            st.button("Lanjut ke Labeling →", on_click=set_page, args=(PAGES[2],))
    else:
        st.warning("Upload data mentah terlebih dahulu di Tab 1.")

# ============================================================
# TAB 3: LABELING & ASPEK
# ============================================================
elif menu == PAGES[2]:
    st.header("Pelabelan Sentimen (RoBERTa) & Identifikasi Aspek")

    if st.session_state['df_exploded'] is not None:
        df = st.session_state['df_exploded']

        st.markdown("### Pengaturan Labeling Biner")
        handle_neutral = st.radio(
            "Pilih penanganan untuk opini yang terdeteksi 'Netral' oleh RoBERTa:",
            ("Hapus Data Netral (Hanya simpan Positif & Negatif)", "Ubah data Netral menjadi Positif")
        )
        
        if not st.session_state['labeling_done']:
            if st.button("Jalankan Pelabelan & Aspek"):
                with st.spinner("Memuat RoBERTa Classifier dari Hugging Face Hub..."):
                    classifier = load_roberta_pipeline()
                    
                if classifier is None:
                    st.error("Gagal menjalankan labeling karena model RoBERTa tidak dapat dimuat.")
                else:
                    with st.spinner("Menentukan sentimen dan aspek per segmen..."):
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

                        if handle_neutral == "Hapus Data Netral (Hanya simpan Positif & Negatif)":
                            df = df[df['sentiment_label'] != 'Netral'].reset_index(drop=True)
                        else:
                            df['sentiment_label'] = df['sentiment_label'].replace('Netral', 'Positif')

                        st.session_state['df_exploded'] = df
                        st.session_state['labeling_done'] = True
                        st.rerun()
        else:
            df = st.session_state['df_exploded']
            st.success("Pelabelan selesai!")

            if st.button("Ulangi Pelabelan"):
                st.session_state['labeling_done'] = False
                st.session_state['df_neutral_handled'] = None
                st.session_state['neutral_action'] = None
                if 'sentiment_label' in st.session_state['df_exploded'].columns:
                    st.session_state['df_exploded'].drop(columns=['sentiment_label', 'aspect_list'], inplace=True, errors='ignore')
                st.rerun()

            c1, c2, c3 = st.columns(3)
            with c1:
                st.subheader("Distribusi Sentimen")
                fig, ax = plt.subplots()
                vals = df['sentiment_label'].value_counts()
                ax.pie(vals.values, labels=vals.index, autopct='%1.1f%%')
                st.pyplot(fig)
                plt.close(fig)
            with c2:
                st.subheader("Distribusi Aspek")
                df_asp = df.explode('aspect_list')
                st.bar_chart(df_asp['aspect_list'].value_counts())
            with c3:
                st.subheader("Jumlah Segmen per Sentimen")
                st.bar_chart(df['sentiment_label'].value_counts())

            with st.expander("Contoh Data dengan Sentimen & Aspek"):
                st.dataframe(df[['segment', 'sentiment_label', 'aspect_list']].head(10))

            if st.session_state.get('df_neutral_handled') is not None and not st.session_state['df_neutral_handled'].empty:
                st.subheader("Data Sentimen Netral yang Ditangani")
                action_text = "dihapus dari dataset" if "Hapus" in st.session_state['neutral_action'] else "diubah menjadi Positif"
                st.info(f"Terdapat **{len(st.session_state['df_neutral_handled'])}** segmen yang awalnya terdeteksi **Netral** oleh model RoBERTa dan telah **{action_text}**.")

            st.divider()
            csv_data_labeled = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Data Berlabel (CSV)",
                data=csv_data_labeled,
                file_name="hasil_pelabelan_dan_aspek.csv",
                mime="text/csv"
            )

        if 'sentiment_label' in st.session_state['df_exploded'].columns:
            st.button("Lanjut ke Modeling →", on_click=set_page, args=(PAGES[3],))
    else:
        st.warning("Lakukan Preprocessing terlebih dahulu.")

# ============================================================
# TAB 4: MODELING (TRAINING)
# ============================================================
elif menu == PAGES[3]:
    st.header("Training Model (MultinomialNB vs LinearSVC)")

    df_exp = st.session_state.get('df_exploded')
    if df_exp is not None and 'sentiment_label' in df_exp.columns:

        if 'model_nb' not in st.session_state and os.path.exists('saved_model_data.joblib'):
            try:
                saved = joblib.load('saved_model_data.joblib')
                for k in ['model_nb', 'model_svm', 'vectorizer', 'y_test',
                          'y_pred_nb', 'y_pred_svm', 'test_data_eval', 't_nb', 't_svm', 'hasil_skenario']:
                    if k in saved:
                        st.session_state[k] = saved[k]
                        if k in ['model_nb', 'model_svm', 'vectorizer']:
                            st.session_state[f"{k}_final"] = saved[k]
            except Exception:
                pass

        df_model = df_exp.copy()

        if st.button("Mulai Training Model"):
            with st.spinner("Mengeksekusi 3 Skenario Pengujian (70:30, 80:20, 90:10)..."):
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
                        't_nb': t_nb, 't_svm': t_svm, 'test_data_eval': test_df
                    }
                    
                    if name == "80:20":
                        st.session_state['model_nb'] = nb
                        st.session_state['model_svm'] = svm
                        st.session_state['vectorizer'] = tfidf
                        st.session_state['model_nb_final'] = nb
                        st.session_state['model_svm_final'] = svm
                        st.session_state['vectorizer_final'] = tfidf
                        st.session_state['test_data_eval'] = test_df
                        
                pb.progress(100)
                st.session_state['hasil_skenario'] = hasil_skenario
                
                try:
                    saved_data = {
                        'model_nb': st.session_state['model_nb'],
                        'model_svm': st.session_state['model_svm'],
                        'vectorizer': st.session_state['vectorizer'],
                        'test_data_eval': st.session_state['test_data_eval'],
                        'hasil_skenario': hasil_skenario
                    }
                    if "80:20" in hasil_skenario:
                        data_8020 = hasil_skenario["80:20"]
                        saved_data.update({
                            'y_test': data_8020['y_test'],
                            'y_pred_nb': data_8020['y_pred_nb'],
                            'y_pred_svm': data_8020['y_pred_svm'],
                            't_nb': data_8020['t_nb'],
                            't_svm': data_8020['t_svm'],
                        })
                    joblib.dump(saved_data, 'saved_model_data.joblib')
                    st.success("Training selesai dan model berhasil disimpan ke 'saved_model_data.joblib'!")
                except Exception as e:
                    st.success("Training selesai!")
                    st.warning(f"Namun gagal menyimpan model ke disk: {e}")

        if 'hasil_skenario' in st.session_state:
            st.divider()
            st.subheader("Matriks Evaluasi Global Berdasarkan Skenario Split")
            
            tab70, tab80, tab90 = st.tabs(["**70:30**", "**80:20**", "**90:10**"])
            tabs_dict = {"70:30": tab70, "80:20": tab80, "90:10": tab90}
            
            for split_name, tab in tabs_dict.items():
                with tab:
                    data = st.session_state['hasil_skenario'][split_name]
                    y_t = data['y_test']
                    p_nb = data['y_pred_nb']
                    p_svm = data['y_pred_svm']
                    
                    col_eval1, col_eval2 = st.columns(2)
                    labels_cm = sorted(pd.concat([pd.Series(y_t), pd.Series(p_nb), pd.Series(p_svm)]).unique())

                    with col_eval1:
                        metrics_nb = {
                            "model": "Multinomial NB",
                            "accuracy": accuracy_score(y_t, p_nb),
                            "precision": precision_score(y_t, p_nb, average='weighted', zero_division=0),
                            "recall": recall_score(y_t, p_nb, average='weighted', zero_division=0),
                            "f1": f1_score(y_t, p_nb, average='weighted', zero_division=0),
                            "train_time (s)": round(data['t_nb'], 4)
                        }
                        st.dataframe(pd.DataFrame([metrics_nb]).set_index("model").style.format("{:.4f}"), use_container_width=True)
                        
                        fig_nb, ax_nb = plt.subplots(figsize=(5, 4))
                        sns.heatmap(confusion_matrix(y_t, p_nb, labels=labels_cm), annot=True, fmt='d', cmap='Blues', xticklabels=labels_cm, yticklabels=labels_cm, ax=ax_nb)
                        ax_nb.set_title(f"Confusion Matrix NB ({split_name})")
                        st.pyplot(fig_nb)
                        plt.close(fig_nb)

                    with col_eval2:
                        metrics_svm = {
                            "model": "LinearSVC",
                            "accuracy": accuracy_score(y_t, p_svm),
                            "precision": precision_score(y_t, p_svm, average='weighted', zero_division=0),
                            "recall": recall_score(y_t, p_svm, average='weighted', zero_division=0),
                            "f1": f1_score(y_t, p_svm, average='weighted', zero_division=0),
                            "train_time (s)": round(data['t_svm'], 4)
                        }
                        st.dataframe(pd.DataFrame([metrics_svm]).set_index("model").style.format("{:.4f}"), use_container_width=True)
                        
                        fig_svm, ax_svm = plt.subplots(figsize=(5, 4))
                        sns.heatmap(confusion_matrix(y_t, p_svm, labels=labels_cm), annot=True, fmt='d', cmap='Blues', xticklabels=labels_cm, yticklabels=labels_cm, ax=ax_svm)
                        ax_svm.set_title(f"Confusion Matrix LinearSVC ({split_name})")
                        st.pyplot(fig_svm)
                        plt.close(fig_svm)

            st.button("Lanjut ke Evaluasi Per Aspek →", on_click=set_page, args=(PAGES[4],))

    else:
        st.warning("Lakukan Pelabelan di Tab 3 terlebih dahulu.")

# ============================================================
# TAB 5: EVALUASI DETAIL PER ASPEK
# ============================================================
elif menu == PAGES[4]:
    st.header("Evaluasi Detail Per Aspek")

    if 'hasil_skenario' in st.session_state:
        skenario_options = list(st.session_state['hasil_skenario'].keys())
        selected_scenario = st.selectbox(
            "Pilih Skenario Split Data:",
            options=skenario_options,
            index=1
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
                    'Aspek': asp,
                    'Jumlah Data Uji': len(sub),
                    'Akurasi NB': accuracy_score(sub['y_true'], sub['pred_nb']),
                    'F1 NB': f1_score(sub['y_true'], sub['pred_nb'], average='weighted', zero_division=0),
                    'Akurasi SVM': accuracy_score(sub['y_true'], sub['pred_svm']),
                    'F1 SVM': f1_score(sub['y_true'], sub['pred_svm'], average='weighted', zero_division=0),
                })

        df_asp_met = pd.DataFrame(aspect_metrics)
        
        if not df_asp_met.empty:
            df_asp_met = df_asp_met.sort_values('Jumlah Data Uji', ascending=False)
            fmt_cols = {c: '{:.2%}' for c in df_asp_met.columns if 'Akurasi' in c or 'F1' in c}
            st.dataframe(df_asp_met.style.format(fmt_cols), use_container_width=True)

            fig_asp, ax_asp = plt.subplots(figsize=(10, 5))
            df_plot = df_asp_met.melt(id_vars=['Aspek'], value_vars=['Akurasi NB', 'Akurasi SVM'],
                                     var_name='Model', value_name='Akurasi')
            sns.barplot(data=df_plot, x='Aspek', y='Akurasi', hue='Model', palette='coolwarm', ax=ax_asp)
            ax_asp.set_ylim(0, 1.1)
            ax_asp.set_title(f"Akurasi NB vs SVM per Aspek ({selected_scenario})")
            st.pyplot(fig_asp)
            plt.close(fig_asp)

        st.button("Pengujian Real-Time →", on_click=set_page, args=(PAGES[5],))

    else:
        st.warning("Latih model di Tab 4 terlebih dahulu.")

# ============================================================
# TAB 6: PENGUJIAN REAL-TIME
# ============================================================
elif menu == PAGES[5]:
    st.header("Pengujian Model Real-Time")

    if 'model_nb' not in st.session_state or 'model_svm' not in st.session_state:
        st.warning("Latih model di Tab 4 terlebih dahulu.")
    else:
        raw_text = st.text_area("Masukkan Kalimat Uji (Satu kalimat per baris):", height=150)
        if st.button("Analisis Teks"):
            lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
            if lines:
                df_res = analyze_texts(
                    lines, st.session_state['model_nb'], st.session_state['model_svm'],
                    st.session_state['vectorizer'], norm_dict, final_stopwords, stemmer
                )
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("Teks tidak boleh kosong.")
