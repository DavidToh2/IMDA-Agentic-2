
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
from typing import List

class EmbedModel():
    def __init__(self):
        # Embeddings
        EMBEDDING_MODEL = embedding_functions.DefaultEmbeddingFunction()
        self.model = EMBEDDING_MODEL

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.model.encode(t).tolist() for t in texts]
    
    def embed_query(self, query: str) -> List[float]:
        return self.model.encode(query).tolist()