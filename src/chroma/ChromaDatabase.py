from chroma.ChromaClient import ChromaClient
from chroma.FileReader import FileReader
import chromadb
import os

from typing_extensions import Annotated
from langchain_core.tools import tool

class ChromaDatabase(ChromaClient):
    def __init__(self):
        super().__init__()

        # Persistent vectorstore
        DB_DIR = f"{os.getcwd()}/chroma_db"
        self.vectorstore = chromadb.PersistentClient(path=DB_DIR)
        try:
            self.collection = self.vectorstore.create_collection(name="internal_info", embedding_function=self.embedding_function)
            docs = FileReader().get_chunks()
            doc_chunks = self.split_docs(docs)
            self.collection.add(documents=doc_chunks, ids=[str(i) for i in range(len(doc_chunks))])
        except chromadb.db.base.UniqueConstraintError:
            self.collection = self.vectorstore.get_collection(name="internal_info")

    def internal_search(self, qn, k):
        # print("---- Starting similarity search on Chroma database ----\n")
        res = self.collection.query(query_texts=[qn], n_results=k)['documents'][0]
        # print(res)
        print("---- Similarity search finished on Chroma database ----\n")
        return res
    
    def insert(self, document):
        pass

@tool
def internal_search(internal_search_query: Annotated[str, "Query to search for"], k=3):
    """Search the local internal database for information pertaining to the query.
    """
    chroma_db = ChromaDatabase()
    return chroma_db.internal_search(internal_search_query, k)