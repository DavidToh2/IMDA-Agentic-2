import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
path = "./idsc_demo/internal_info"

files_content = []

for filename in filter(lambda p: p.endswith("txt"), os.listdir(path)):
    filepath = os.path.join(path, filename)
    with open(filepath, mode='r') as f:
        files_content += [f.read()]

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=500,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)
texts = [doc.page_content for doc in text_splitter.create_documents(files_content)]

from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./idsc_demo/chroma_db")

default_ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.create_collection(name="internal_info", embedding_function=default_ef)
collection.add(
    documents=texts,
    ids=[str(i) for i in range(len(texts))]
)

