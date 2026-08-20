"""
Modul Utilitas Manajemen & Pengujian Model ML
"""

import os
import joblib
import requests
import pandas as pd
import streamlit as st
from src.constants import JOBLIB_FILE_PATH, JOBLIB_RELEASE_URL
from src.preprocessing import preprocess_text, get_aspects


def download_model_if_needed(file_path: str = JOBLIB_FILE_PATH, url: str = JOBLIB_RELEASE_URL) -> bool:
    """
    Mengunduh file joblib dari GitHub Releases jika belum tersedia secara lokal.
    Sangat berguna untuk deployment di Streamlit Cloud / Hugging Face Spaces.
    """
    if os.path.exists(file_path):
        return True

    st.info(f"Mengunduh trained model ({file_path}) dari GitHub Releases...")
    try:
        resp = requests.get(url, stream=True, timeout=30)
        if resp.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            st.success("Berhasil mengunduh model!")
            return True
        else:
            st.warning(f"File model lokal '{file_path}' belum ada dan gagal mengunduh dari GitHub Releases (Status Code: {resp.status_code}).")
            return False
    except Exception as e:
        st.warning(f"Gagal mengunduh file model secara otomatis: {e}")
        return False


@st.cache_resource
def load_saved_model(file_path: str = JOBLIB_FILE_PATH):
    """
    Memuat dictionary model yang tersimpan di file joblib.
    """
    if not os.path.exists(file_path):
        downloaded = download_model_if_needed(file_path)
        if not downloaded or not os.path.exists(file_path):
            return None
    try:
        return joblib.load(file_path)
    except Exception as e:
        st.error(f"Gagal memuat file joblib '{file_path}': {e}")
        return None


def analyze_texts(texts: list, nb_model, svm_model, vec, norm_dict: dict, stopwords: set, stemmer, progress_bar=None) -> pd.DataFrame:
    """
    Menganalisis daftar kalimat uji dalam mode real-time.
    """
    rows = []
    total_texts = len(texts)
    for i, text in enumerate(texts):
        segments = preprocess_text(text, norm_dict, stopwords, stemmer)
        if segments:
            for seg in segments:
                X = vec.transform([seg])
                pred_nb = nb_model.predict(X)[0]
                pred_svm = svm_model.predict(X)[0]
                probs_nb = nb_model.predict_proba(X)[0]
                classes = nb_model.classes_
                prob_str = " | ".join([f"{c}: {probs_nb[j]:.1%}" for j, c in enumerate(classes)])
                rows.append({
                    "Teks Asli": text,
                    "Segmen Bersih": seg,
                    "Aspek": ", ".join(get_aspects(seg)),
                    "Prediksi SVM": pred_svm,
                    "Prediksi NB": pred_nb,
                    "Probabilitas NB": prob_str,
                })

        if progress_bar is not None:
            if total_texts < 100 or i % max(1, total_texts // 100) == 0 or i == total_texts - 1:
                progress = min((i + 1) / total_texts, 1.0)
                progress_bar.progress(progress, text=f"Menganalisis kalimat {i + 1} dari {total_texts}...")

    return pd.DataFrame(rows)
