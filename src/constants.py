"""
Konstanta dan Konfigurasi Analisis Sentimen MBG
"""

ASPEK_DICT = {
    'Kualitas': [
        'kualitas', 'bagus', 'jelek', 'enak', 'basi', 'gizi', 'susu',
        'menu', 'rasa', 'porsi', 'higienis', 'keracunan', 'sehat',
        'mentah', 'keras', 'hambar', 'ulat', 'lauk', 'sayur',
        'karbohidrat', 'protein', 'lemak', 'gula', 'ayam', 'telur',
        'kenyang', 'alergi', 'higienitas'
    ],
    'Layanan': [
        'layan', 'antri', 'ramah', 'lambat', 'cepat', 'bantu', 'saji',
        'distribusi', 'vendor', 'katering', 'sekolah', 'siswa', 'guru',
        'telat', 'molor', 'bocor', 'tepat waktu', 'pelosok', 'merata',
        'zonasi', 'umkm', 'kemasan', 'kotak', 'plastik'
    ],
    'Anggaran': [
        'harga', 'mahal', 'murah', 'biaya', 'bayar', 'anggar', 'boros',
        'korupsi', 'dana', 'apbn', 'pajak', 'potong', 'sunat', 'markup',
        'tender', 'proyek', 'apbd', 'defisit', 'utang', 'ekonomi',
        'alokasi', 'transparan', 'budget'
    ],
}

KONJUNGSI = r'\b(tetapi|namun|meskipun|tapi|sedangkan|cuman|cuma|sayangnya|padahal|walau|walaupun|pasalnya)\b'
KONJUNGSI_SET = {
    'tetapi', 'namun', 'meskipun', 'tapi', 'sedangkan', 'cuman',
    'cuma', 'sayangnya', 'padahal', 'walau', 'walaupun', 'pasalnya'
}

TFIDF_PARAMS = {
    'max_features': 3000,
    'ngram_range': (1, 2),
    'sublinear_tf': True,
    'min_df': 2,
    'max_df': 0.85
}

MODEL_HF_NAME = "w11wo/indonesian-roberta-base-sentiment-classifier"

# URL Release GitHub untuk mengunduh joblib jika tidak ada di lokal (misal saat dipublish di Streamlit Cloud)
JOBLIB_RELEASE_URL = "https://github.com/rifqieali/analisis-sentimen-MBG/releases/download/v1.0.0/saved_model_data.joblib"
JOBLIB_FILE_PATH = "saved_model_data.joblib"

PAGES = [
    "Upload Data",
    "Preprocessing & Segmentasi",
    "Labeling & Aspek",
    "Modeling (Training)",
    "Evaluasi Detail (Per Aspek)",
    "Pengujian Real-Time"
]
