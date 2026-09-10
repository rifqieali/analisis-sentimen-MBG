"""Robust CSV loader untuk file upload Streamlit (Excel ID friendly)."""

import pandas as pd


def canon_label(v) -> str | None:
    """Canonicalize a sentiment label to 'Positif' / 'Negatif' / 'Netral' / None.

    Empty strings, whitespace-only, and NaN all become None (unlabeled).
    Also maps English variants ('Positive'/'Negative'/'Neutral').
    """
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        return None
    s = str(v).strip().capitalize()
    s = {"Positive": "Positif", "Negative": "Negatif", "Neutral": "Netral"}.get(s, s)
    return s or None


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def read_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """Baca CSV upload: toleran separator `,`/`;`, encoding utf-8/latin1, strip kolom.

    Raises: ValueError dengan pesan ramah jika file kosong / tak terbaca.
    """
    if uploaded_file is None:
        raise ValueError("File kosong — upload file CSV dulu.")
    for sep in (",", ";"):
        for enc in ("utf-8", "latin1"):
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=sep, encoding=enc)
                if len(df.columns) >= 1 and len(df) > 0:
                    # Validasi separator benar: file `;` dibaca dengan `,` hasilkan 1 kolom sampah
                    if sep == "," and len(df.columns) == 1 and ";" in str(df.columns[0]):
                        continue
                    return _normalize_columns(df)
            except Exception:
                continue
    uploaded_file.seek(0)
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python", encoding="latin1")
        if len(df) == 0:
            raise ValueError("CSV kosong — tak ada baris data.")
        return _normalize_columns(df)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"CSV tak terbaca: {e}")
