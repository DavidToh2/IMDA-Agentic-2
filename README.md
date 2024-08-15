## Extensions installed manually:
```python
sentence_transformers
chromadb
pyautogen
langchain langchain-core langchain-community langchain_chroma
selenium
unstructured(required by chroma)
```

You may need to install `libmagic` via Homebrew if your system doesn't have it yet

## Running

Before running codefiles, ensure that `ollama` is installed.

Execute `ollama pull mistral-nemo:latest` to download a local copy of the `mistral-nemo` LLM, then `ollama run` it.

Execute `chroma run --path ./chroma_db` to initialise the chromaDB.