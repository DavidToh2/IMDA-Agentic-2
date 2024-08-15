from chroma.ChromaClient import ChromaClient
from chroma.FileReader import FileReader
from langchain_chroma import Chroma
import os

class ChromaDatabase(ChromaClient):
    def __init__(self):
        super().__init__()

        # Persistent vectorstore
        DB_DIR = f"{os.getcwd()}/chroma_db"
        if (os.path.exists(DB_DIR)):
            self.vectorstore : Chroma = Chroma(embedding_function=self.model, persist_directory=DB_DIR)
        else:
            docs = FileReader().get_chunks()
            doc_chunks = self.split_docs(docs)
            self.vectorstore : Chroma = Chroma.from_documents(documents=doc_chunks, embedding=self.model, persist_directory=DB_DIR)

    def similarity_search(self, qn, k):
        print("---- Starting similarity search on Chroma database ----\n")
        res = self.vectorstore.similarity_search(query=qn, k=k)
        print("---- Similarity search finished on Chroma database ----\n")
        return res
    
    def insert(self, document):
        pass
        
