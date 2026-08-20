# 📊 Aspect-Based Sentiment Analysis (ABSA) - Program Makan Bergizi Gratis (MBG)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine_Learning-F7931E.svg)](https://scikit-learn.org/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Transformers-yellow.svg)](https://huggingface.co/w11wo/indonesian-roberta-base-sentiment-classifier)
[![HKI / HAKI Registered](https://img.shields.io/badge/HAKI-Surat_Pencatatan_Ciptaan-green.svg)](#-hak-kekayaan-intelektual-hki--haki)

Repositori ini berisi *source code* aplikasi penelitian yang berfokus pada **Analisis Sentimen Berbasis Aspek (ABSA)** terhadap opini publik terkait **Program Makan Bergizi Gratis (MBG)**. 

Penelitian ini membandingkan kinerja dua algoritma *Machine Learning*, yaitu **Multinomial Naïve Bayes** dan **Linear Support Vector Classifier (LinearSVC)**, dengan menerapkan teknik unik berupa **segmentasi kalimat berbasis konjungsi** untuk memisahkan opini majemuk sebelum klasifikasi.

---

## 📜 Hak Kekayaan Intelektual (HKI / HAKI)

Program komputer ini telah terdaftar dan dilindungi secara hukum berdasarkan **Surat Pencatatan Ciptaan** dari **Kementerian Hukum Republik Indonesia (Direktorat Jenderal Kekayaan Intelektual)**:

> **Nomor Pencatatan:** `001265752` | **Nomor Permohonan:** `EC002026079870` (5 Juni 2026)

| Parameter | Keterangan |
|---|---|
| **Judul Ciptaan** | Analisis Sentimen Berbasis Aspek terhadap Program Makan Bergizi Gratis |
| **Jenis Ciptaan** | Program Komputer |
| **Nomor Pencatatan** | `001265752` |
| **Tanggal Pertama Kali Diumumkan** | 13 Mei 2026 (Kota Semarang) |
| **Pemegang Hak Cipta** | Universitas Negeri Semarang |
| **Pencipta** | 1. **Rifqie Alimul Haq**<br>2. **Dr. Nur Iksan, S.T., M.Kom.**<br>3. **Dr. Djuniadi, M.T.** |
| **Masa Pelindungan** | Berlaku selama 50 (lima puluh) tahun sejak ciptaan pertama kali diumumkan. |

---

## 🌟 Fitur Utama

1. **Modular Architecture (`src/`):** Kode NLP, preprocessing, resources, dan utilitas model terpisah secara bersih dan efisien.
2. **Auto-Downloading Model & HF Transformers Integration:** 
   - Auto-labeling menggunakan **Indonesian RoBERTa** (`w11wo/indonesian-roberta-base-sentiment-classifier`) via Hugging Face Hub tanpa perlu menyimpan biner 479MB di dalam repositori Git.
   - Pengujian real-time otomatis mengunduh biner `saved_model_data.joblib` dari GitHub Releases jika belum tersedia di lokal.
3. **Dua Mode Aplikasi:**
   - **`app_pipeline.py` (Lokal - Full 6 Tahapan Pipeline):** Upload data $\rightarrow$ Preprocessing & Segmentasi $\rightarrow$ RoBERTa Auto-Labeling $\rightarrow$ Training 3 Skenario (70:30, 80:20, 90:10) $\rightarrow$ Evaluasi Per Aspek $\rightarrow$ Pengujian Real-Time.
   - **`app_demo.py` (Deployment Ready - Real-Time Testing):** Antarmuka pengujian cepat untuk deployment di **Streamlit Cloud** / **Hugging Face Spaces**.

---

## 📁 Struktur Direktori Repositori

```text
analisis-sentimen-MBG/
├── .gitignore                    # Melindungi Git dari venv & binary besar
├── .streamlit/
│   └── config.toml               # Konfigurasi tema Streamlit Cloud
├── data/
│   └── data_mbg.csv              # Dataset mentah Twitter/X tentang MBG
├── src/                          # Modul Python Terstruktur
│   ├── __init__.py
│   ├── constants.py              # Dictionary aspek, konjungsi, dan konstanta
│   ├── preprocessing.py          # Cleaning, normalisasi, segmentasi, stemming
│   ├── resources.py              # Cache loader Sastrawi, stopwords, & RoBERTa
│   ├── model_utils.py            # Loader & auto-downloader model ML
│   └── ui.py                     # Desain UI premium & styling komponen
├── app_pipeline.py               # Aplikasi Pipeline Lengkap (6 Tab - Utama)
├── app_demo.py                   # Aplikasi Pengujian Real-Time (Siap Deploy)
├── requirements-full.txt         # Dependency lengkap (untuk pipeline lokal)
├── requirements.txt              # Dependency ringan (untuk Streamlit Cloud)
└── README.md                     # Dokumentasi proyek
```

---

## 🚀 Cara Instalasi & Menjalankan Lokal

### 1. Clone Repositori
```cmd
git clone https://github.com/rifqieali/analisis-sentimen-MBG.git
cd analisis-sentimen-MBG
```

### 2. Buat Virtual Environment
```cmd
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Instal Dependensi

* **Untuk Pipeline Lengkap (`app_pipeline.py` termasuk RoBERTa):**
  ```cmd
  pip install -r requirements-full.txt
  ```

* **Untuk Pengujian Demo Real-Time (`app_demo.py`):**
  ```cmd
  pip install -r requirements.txt
  ```

### 4. Jalankan Aplikasi

* **Menjalankan Pipeline Lengkap (Utama):**
  ```cmd
  streamlit run app_pipeline.py
  ```

* **Menjalankan Demo Real-Time:**
  ```cmd
  streamlit run app_demo.py
  ```

---

## ☁️ Petunjuk Deployment di Streamlit Cloud

1. Push repositori ini ke GitHub (`https://github.com/rifqieali/analisis-sentimen-MBG`).
2. Buat **Release** baru di GitHub Repo (misal tag `v1.0.0`) dan lampirkan file `saved_model_data.joblib` (6.7MB) sebagai release asset.
3. Buka [share.streamlit.io](https://share.streamlit.io/) dan hubungkan dengan akun GitHub Anda.
4. Pilih repositori `analisis-sentimen-MBG`, atur Main file path ke **`app_demo.py`**.
5. Klik **Deploy**! Aplikasi akan otomatis berjalan dan mengunduh model dari Release saat pertama kali diakses.

---

## 📄 Lisensi & Kredit

Penelitian & Pengembangan oleh **Rifqie Alimul Haq**, **Dr. Nur Iksan, S.T., M.Kom.**, dan **Dr. Djuniadi, M.T.** (Universitas Negeri Semarang).  
Model Transformer: [w11wo/indonesian-roberta-base-sentiment-classifier](https://huggingface.co/w11wo/indonesian-roberta-base-sentiment-classifier)  
Library NLP Bahasa Indonesia: [Sastrawi Stemmer](https://github.com/sastrawi/sastrawi) & [InSet Lexicon](https://github.com/fajri91/InSet)
