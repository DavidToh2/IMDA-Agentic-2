
from sentence_transformers import SentenceTransformer
from typing import List

class EmbedModel():
    def __init__(self):
        # Embeddings
        EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
        self.model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.model.encode(t).tolist() for t in texts]
    
    def embed_query(self, query: str) -> List[float]:
        return self.model.encode(query).tolist()