import chromadb
from chromadb.utils import embedding_functions

from typing_extensions import Annotated


client = chromadb.HttpClient(host='localhost', port=8000)
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_collection(name="internal_info", embedding_function=default_ef)

def internal_search(
    query: Annotated[str, 'query to search for in internal database'],
    n=3,
):
    res = collection.query(query_texts=[query], n_results=n)
    return "\n".join(res['documents'][0])

