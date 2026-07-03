from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import numpy as np


@dataclass
class EmbeddingBundle:
    vectors: np.ndarray
    model_name: str


class LocalTfidfEmbeddings:
    """
    Yo uso TF-IDF como fallback reproducible cuando no hay embeddings externos disponibles.
    Para Colab o producción se puede cambiar por SentenceTransformers.
    """
    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=4096)
        self.model_name = "local_tfidf_fallback"
        self._fit = False

    def fit_transform(self, texts: Iterable[str]) -> EmbeddingBundle:
        matrix = self.vectorizer.fit_transform(list(texts))
        self._fit = True
        return EmbeddingBundle(matrix.toarray().astype("float32"), self.model_name)

    def transform(self, texts: Iterable[str]) -> EmbeddingBundle:
        if not self._fit:
            raise RuntimeError("Yo necesito ajustar el vectorizador antes de transformar preguntas.")
        matrix = self.vectorizer.transform(list(texts))
        return EmbeddingBundle(matrix.toarray().astype("float32"), self.model_name)


class SentenceTransformerEmbeddings:
    """
    Yo uso embeddings semánticos reales si sentence-transformers está instalado.
    """
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def fit_transform(self, texts: Iterable[str]) -> EmbeddingBundle:
        vectors = self.model.encode(list(texts), normalize_embeddings=True)
        return EmbeddingBundle(np.asarray(vectors, dtype="float32"), self.model_name)

    def transform(self, texts: Iterable[str]) -> EmbeddingBundle:
        vectors = self.model.encode(list(texts), normalize_embeddings=True)
        return EmbeddingBundle(np.asarray(vectors, dtype="float32"), self.model_name)


def create_embedding_model(prefer_semantic: bool = False):
    """
    Yo elijo embeddings semánticos si están disponibles; si no, uso fallback local para que el notebook ejecute completo.
    """
    if prefer_semantic:
        try:
            return SentenceTransformerEmbeddings()
        except Exception:
            return LocalTfidfEmbeddings()
    return LocalTfidfEmbeddings()
