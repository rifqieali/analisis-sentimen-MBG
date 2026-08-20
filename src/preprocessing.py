"""
Modul Preprocessing & Segmentasi Kalimat NLP
"""

import re
import string
from src.constants import ASPEK_DICT, KONJUNGSI, KONJUNGSI_SET


def clean_text(text: str) -> str:
    """
    Membersihkan teks dari mention, hashtag, URL, angka, dan tanda baca.
    """
    text = str(text).lower()
    text = re.sub(r'@\w+', ' ', text)
    text = re.sub(r'#\w+', ' ', text)
    text = re.sub(r'http\S+|www\S+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    return re.sub(r'\s+', ' ', text).strip()


def normalize_text(text: str, norm_dict: dict) -> str:
    """
    Mengganti kata tidak baku / slang menggunakan dictionary normalisasi.
    """
    return ' '.join(norm_dict.get(w, w) for w in text.split())


def segmentasi_kalimat(text: str) -> list:
    """
    Memecah kalimat majemuk menjadi beberapa segmen opini berdasarkan kata hubung (konjungsi).
    """
    parts = re.split(KONJUNGSI, text)
    return [s.strip() for s in parts if s.strip() and s.strip() not in KONJUNGSI_SET] or [text]


def stopword_and_stem(text: str, final_stopwords: set, stemmer) -> str:
    """
    Menghapus stopword dan menerapkan stemming Sastrawi.
    """
    words = [w for w in text.split() if w not in final_stopwords]
    if not words:
        return ""
    return stemmer.stem(' '.join(words))


def preprocess_text(text: str, norm_dict: dict, final_stopwords: set, stemmer) -> list:
    """
    Pipeline lengkap preprocessing per kalimat: Cleaning -> Normalisasi -> Segmentasi -> Stopword & Stemming.
    Returns: list of cleaned segments.
    """
    cleaned = clean_text(text)
    normed = normalize_text(cleaned, norm_dict)
    segments = segmentasi_kalimat(normed)
    result = []
    for seg in segments:
        processed = stopword_and_stem(seg, final_stopwords, stemmer)
        if processed.strip():
            result.append(processed)
    return result


def get_aspects(text: str) -> list:
    """
    Mengekstraksi aspek (Kualitas, Layanan, Anggaran, atau Lainnya) berdasarkan keyword matching.
    """
    tokens = set(str(text).split())
    found = [asp for asp, keys in ASPEK_DICT.items() if not tokens.isdisjoint(keys)]
    return found if found else ['Lainnya']


def determine_sentiment_roberta(text: str, classifier) -> str:
    """
    Menentukan label sentimen (Positif, Negatif, Netral) menggunakan model Transformer RoBERTa.
    """
    if not isinstance(text, str) or not text.strip() or classifier is None:
        return 'Netral'
    try:
        result = classifier(text[:512])[0]
        label = result['label'].lower()
        if 'pos' in label:
            return 'Positif'
        elif 'neg' in label:
            return 'Negatif'
        return 'Netral'
    except Exception:
        return 'Netral'
