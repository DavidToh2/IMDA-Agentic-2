from chroma.ChromaClient import ChromaClient
from langchain_chroma import Chroma
from langchain.schema.document import Document
import os

class ChromaTemp(ChromaClient):
    def __init__(self, docs):
        super().__init__(1000, 100)

        # Temporary vectorstore
        doc_chunks = self.split_docs([Document(page_content=doc, metadata={"source": "local"}) for doc in docs])
        self.vectorstore : Chroma = Chroma.from_documents(documents=doc_chunks, embedding=self.model)

    def similarity_search(self, query, k=5):
        print("---- Starting similarity search on temporary database ----\n")
        res = self.vectorstore.similarity_search(query=query, k=k)
        print("---- Similarity search finished on temporary vectorstore ----\n")
        return res