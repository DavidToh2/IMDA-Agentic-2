# Introduction

Agentic AI Proof-of-Concept project for IMDA internship 2024 using Autogen and LangChain / Langgraph frameworks.

Our problem statement was to create a mutli-agent, retrieval-augmented AI system that could assist in the generation of speaker profiles (and potentially other types of profiles) using both internal and external data. Every run invokes the following steps to generate the speaker profile:
1. Generate a profile template
3. For each speaker, perform an online search using the search_and_crawl tool, and use it to generate a public profile
4. For each speaker, perform an internal search using the internal_search tool, and use it to generate an internal profile
5. Synthesize both profiles into a combined version

A stretch goal was to identify and generate all profiles of all speakers at any event.

## Project Structure

- `idsc_demo` contains experimental versions and trials that were prototyped during the exploratory phase of the project. The most complete version is `profile_generator.py`. Note that everything in this folder is self-contained.
- `src` contains a skeleton app, scaffolded in a somewhat OOP manner, where more complete versions of the app can be plugged in for testing.
- `internal_info` contains some text files that serve as the source files of a placeholder internal database.
- `chroma_db` contains the actual `.sqlite3` database itself.

Other folders:

- `.cache` contains cached runs from Autogen runs.
- `examples` was intended to contain a list of files detailing some results from past good runs, along with the parameters necessary to configure these runs.

# Setup

1. Install `ollama` (instructions can be found online).

Execute `ollama pull mistral-nemo:latest` to download a local copy of the `mistral-nemo` LLM image, then `ollama run` it.

Execute `chroma run --path ./chroma_db` to initialise the chromaDB.

Note: If you require a larger context-sized version of the model for Autogen, you may need to duplicate the `mistral-nemo` image with a larger `ctx` parameter. Search online for how to do so.

2. Install `python` and dependencies.

We use Python 3.12.4. Set up a virtual environment (instructions can be found online).

The following environment variables are required for the code (specifically, `src/tools/MessagePoster.py`) to work properly: `URL_OUTPUT`, `URL_LOG`. Inject them into `venv/bin/activate` (instructions can be found online).

Execute `pip install -r requirements.txt` to install all requirements. You may need to install `libmagic` via Homebrew if your system doesn't have it yet.

## Recreating requirements.txt

Install the following dependencies manually:

```python
sentence_transformers
chromadb
pyautogen
langchain langchain-core langchain-community langchain_chroma langgraph
selenium
unstructured (required by chroma)
```
Then `pip freeze > requirements.txt`.

# Further Development

We have built four different agentic models which can be found in `src`:

- `AutogenGroupChatAgentic.py`: uses Autogen to implement a system of agents (`orchestrator, supervisor, external_searcher, internal_searcher, writer, summariser`). 
    - The agents carry out the task in a predetermined sequence: future work can be done on this by removing `self.ordering` and further building up `custom_speaker_select_func()`.
    - As mentioned before, this model is cache-able: by modifying the seed value in the code, runs can be cached or replayed from the cache.
    - This model is not deterministic for some reason even though the temperature is 0.0, hence caching is necessary.
- `AutogenSeqChatAgentic.py`: uses the Sequential Chat architecture on Autogen to segregate external and internal search workflows.
    - External and internal search workflows are implemented on separate groupchats
    - Flow is as follows:
      ```
      ORCHESTRATOR --> (PLANNER --> EXTERNAL SEARCHER --> USER PROXY --> WRITER) --> (INTERNAL SEARCHER --> USER PROXY --> WRITER)
      ```
- `LanggraphSingleAgent.py`: uses Langgraph to implement a single-agent workflow, structured as a simple cyclic graph: 
```
START --> AGENT <-> TOOL_CALL
```
    - Note that LangChain (and hence Langgraph) is strictly deterministic as the temperature is set to 0.0.
- `LanggraphAgentic.py`: uses Langgraph to implement a multi-agent workflow.
    - This class hardcodes the `supervisor` and `tool_call_filter` agents, while allowing for other agents to be configured in `LanggraphAgentConfig.py`. The workflow is represented by the graph: 
```
START --> SUPERVISOR --> ENTER_CUSTOM_AGENT --> CUSTOM_AGENT --> CUSTOM_AGENT_TOOL --> TOOL_CALL_FILTER --> EXIT_AGENT --> SUPERVISOR
```

Every class accepts `prompt` and `detailed_instructions` arguments. To invoke, simply instantiate the class in `main.py` and then call the `start()` method. In this manner you may switch between the three models depending on their performance.
