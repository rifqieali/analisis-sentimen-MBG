"""
Modul Pemuatan Sumber Daya NLP & Model (Cached)
"""

import os
from io import BytesIO
import requests
import pandas as pd
import streamlit as st
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from src.constants import MODEL_HF_NAME


@st.cache_resource
def load_nlp_resources():
    """
    Memuat Stemmer Sastrawi dan Stopwords terintegrasi.
    """
    factory_stem = StemmerFactory()
    stemmer = factory_stem.create_stemmer()

    factory_stop = StopWordRemoverFactory()
    sw_sastrawi = set(factory_stop.get_stop_words())
    sw_custom = {
        "yg", "dg", "rt", "dgn", "ny", "d", "klo", "kalo", "amp",
        "biar", "bikin", "udah", "udh", "aja", "sih", "deh", "nih",
        "lah", "dong", "kan", "tuh", "mah", "wkwk", "haha", "hehe",
        "aku", "saya", "kamu", "dia", "kita", "kami", "mereka", "sama"
    }
    negation_words = {
        'tidak', 'tak', 'tiada', 'bukan', 'jangan',
        'belum', 'kurang', 'gak', 'ga', 'nggak', 'enggak'
    }
    final_stopwords = (sw_sastrawi | sw_custom) - negation_words
    return stemmer, final_stopwords, negation_words


@st.cache_data
def load_normalization_dict():
    """
    Memuat kamus kata baku dari GitHub repo kamus_kata_baku dengan fallback lokal dictionary.
    """
    url = "https://github.com/analysisdatasentiment/kamus_kata_baku/raw/main/kamuskatabaku.xlsx"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        xls = pd.read_excel(BytesIO(resp.content), engine="openpyxl")
        cols = xls.columns.tolist()
        return dict(zip(
            xls[cols[0]].astype(str).str.lower(),
            xls[cols[1]].astype(str).str.lower()
        ))
    except Exception:
        return {"yg": "yang", "gk": "tidak", "ga": "tidak", "gak": "tidak", "bgt": "banget"}


@st.cache_data
def load_inset_lexicon():
    """
    Memuat InSet Lexicon (Positive & Negative) untuk pelabelan kata berbasis leksikon.
    """
    pos_url = 'https://raw.githubusercontent.com/fajri91/InSet/master/positive.tsv'
    neg_url = 'https://raw.githubusercontent.com/fajri91/InSet/master/negative.tsv'
    try:
        df_pos = pd.read_csv(pos_url, sep='\t', names=['word', 'weight'], header=None)
        df_neg = pd.read_csv(neg_url, sep='\t', names=['word', 'weight'], header=None)
        df_lex = pd.concat([df_pos, df_neg], ignore_index=True)
        df_lex['weight'] = pd.to_numeric(df_lex['weight'], errors='coerce')
        df_lex = df_lex.dropna(subset=['weight'])
        df_lex['word'] = df_lex['word'].astype(str).str.strip()
        df_lex['weight'] = df_lex['weight'].astype(int)
        lexicon = dict(zip(df_lex['word'], df_lex['weight']))
        
        # Hapus kata topik netral agar tidak bias skor sentimen
        for w in {'mbg', 'makan', 'bergizi', 'gratis', 'gizi', 'program',
                  'prabowo', 'jokowi', 'presiden', 'menteri', 'indonesia'}:
            lexicon.pop(w, None)
        return lexicon
    except Exception:
        return {}


@st.cache_resource
def load_roberta_pipeline():
    """
    Memuat pipeline RoBERTa langsung dari Hugging Face Hub (ringan, tanpa perlu menyimpan model lokal 479MB).
    """
    try:
        from transformers import pipeline
        return pipeline(
            "text-classification",
            model=MODEL_HF_NAME,
            tokenizer=MODEL_HF_NAME,
            device=-1,
            truncation=True,
            max_length=128
        )
    except Exception as e:
        st.error(f"Gagal memuat model RoBERTa dari Hugging Face: {e}")
        return None
