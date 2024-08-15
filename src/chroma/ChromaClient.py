
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chroma.EmbedModel import EmbedModel
from typing import List

class ChromaClient():

    def __init__(self, chunk_size=500, chunk_overlap=0):

        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Embedding Model
        self.model = EmbedModel()

    def insert(self, doc):
        pass

    def delete(self, doc):
        pass

    def split_docs(self, docs):
        return self.text_splitter.split_documents(docs)