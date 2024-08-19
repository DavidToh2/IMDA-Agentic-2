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

## Agent Workflow

For an event, the steps to generate the speaker profiles are:
1. Generate a profile template
2. Find a list of all speakers by performing an online search using the search_and_crawl tool
3. For each speaker, perform an online search using the search_and_crawl tool
4. For each speaker, perform an internal search using the internal_search tool
5. Synthesize the profiles of all speakers