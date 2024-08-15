from sentence_transformers import SentenceTransformer
from typing import List
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

dir_path = os.getcwd()



loader = DirectoryLoader(f"{dir_path}/internal_info", glob="**/*.txt",show_progress=True)
data = loader.load()
print(data)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)
all_splits = [split.page_content for split in all_splits]

import chromadb
client = chromadb.PersistentClient(path="./chroma_db")

default_ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.create_collection(name="internal_info", embedding_function=default_ef)
collection.add(
    documents=all_splits,
    ids=[str(i) for i in range(len(all_splits))]
)

