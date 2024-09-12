# Introduction

Agentic AI Proof-of-Concept project for IMDA internship 2024 using Autogen and LangChain / Langgraph frameworks.

Our problem statement was to create a mutli-agent, retrieval-augmented AI system that could assist in the generation of speaker profiles (and potentially other types of profiles) using both internal and external data. Every run invokes the following steps to generate the speaker profile:
1. Generate a profile template
3. For each speaker, perform an online search using the search_and_crawl tool, and use it to generate a public profile
4. For each speaker, perform an internal search using the internal_search tool, and use it to generate an internal profile
5. Synthesize both profiles into a combined version

A stretch goal was to identify and generate all profiles of all speakers at any event.

Refer to https://pine-friction-47e.notion.site/52d829b041e74cdba9351397a9690cb4?v=0b8a5eebf9db41088419d8ca53694637 for documentation. 

Refer to https://github.com/BurningSheep02/IMDA-Agentic for prior exploration of agentic framworks. 

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

# Agentic Models

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

To invoke, simply instantiate the class in `main.py` and then call the `start()` method. In this manner you may switch between the four models depending on their performance.

# Cached runs
Examples of successful runs have been cached for reference.
Note that caching is only supported for autogen-based implementations.  
- 10: AutogenSeqChatAgentic profile for 'Mira Murati'
- 103: AutogenGroupChatAgentic profile for 'Mira Murati'
To prevent accidental overwrites of these cached runs, DO NOT use any of the numbers above as cache seeds.

# Instructions

1. Clone this repo from GitHub into a virtual environment. 

https://github.com/DavidToh2/IMDA-Agentic-2

1. Install dependencies as required. 
2. Set up Ollama following: 
    
    [Local LLM Setup: Ollama](https://www.notion.so/Local-LLM-Setup-Ollama-09b0eac9a41e4908b77333b5c4f5c9d5?pvs=21)
    
    For profile generator to work, download mistral-nemo and set the context size to 32000 (near the limit for Macbook Pro with 16GB RAM). 
    
3. Set the following environmental variables if Slack integration is desired (Input dummy values otherwise)
    1. URL_OUTPUT
    2. URL_LOG
4. To run the profile generator, go to the main.py file in the src folder. 
    1. To run the Sequential Chat, replace the contents of the files with the following: 
        
        ```python
        from AutogenSeqChatAgentic import AutogenSeqChatAgent
        
        def main():
            autogen = AutogenSeqChatAgent("Mira Murati") # Input speaker name
            autogen.start()
          
        main()
        ```
        
    2. To run the GroupChat: 
        
        ```python
        from AutogenGroupChatAgentic import AutogenGroupChatAgent
        
        def main():
            autogen = AutogenGroupChatAgent("Mira Murati") # Input speaker name
            autogen.start()
          
        main()
        ```
        
    3. To run LangGraph with single agent: 
        
        ```python
        
        from LanggraphSingleAgent import LanggraphSingleAgent 
        
        def main():
            langgraph = LanggraphSingleAgent(prompt, detailed_instructions)
            prompt = """Write a profile of Mira Murati.""" # Input speaker name
            detailed_instructions = """
                Step 1. Conduct an online search of externally available data using the search_and_query tool, passing in search arguments in the external_search_query parameter.
                Step 2. Disregard all information irrelevant to the main task. Summarise the relevant websearch results into a preliminary report. Preface this report with the words 'EXTERNAL REPORT'.
                Step 3. Conduct an internal search of data in our internal database using the internal_search tool, passing in search arguments in the internal_search_query parameter.
                Step 4. Disregard all internal results irrelevant to the main task. Summarise the relevant internal information into a second report. Preface this report with the words 'INTERNAL REPORT'. If there is no relevant information in the internal database, skip the internal report and proceed directly to step 5.
                Step 5. Using your summary skills, write a combined report that includes only the information relevant to the main task. Preface this report with the words 'COMBINED REPORT'. Output the words 'DONE' to end off your report.
        
                Ensure you use the correct tool calling syntax. If your tool call returns with no output, it means you have failed to use the correct syntax: fix your syntax and try again.
                All your reports should be in paragraph form, and not in point form.
            """
            langgraph.start()
        
            
        main()
        ```
        
    4. To run LangGraph with multiple agents: 
        
        ```python
        
        from LanggraphAgentic import LanggraphAgent
        
        def main():
            langgraph = LanggraphAgent(prompt, detailed_instructions)
            prompt = """Write a profile of Mira Murati.""" # Input speaker name
            detailed_instructions = """
                Step 1. Conduct an online search of externally available data using the search_and_query tool, passing in search arguments in the external_search_query parameter.
                Step 2. Disregard all information irrelevant to the main task. Summarise the relevant websearch results into a preliminary report. Preface this report with the words 'EXTERNAL REPORT'.
                Step 3. Conduct an internal search of data in our internal database using the internal_search tool, passing in search arguments in the internal_search_query parameter.
                Step 4. Disregard all internal results irrelevant to the main task. Summarise the relevant internal information into a second report. Preface this report with the words 'INTERNAL REPORT'. If there is no relevant information in the internal database, skip the internal report and proceed directly to step 5.
                Step 5. Using your summary skills, write a combined report that includes only the information relevant to the main task. Preface this report with the words 'COMBINED REPORT'. Output the words 'DONE' to end off your report.
        
                Ensure you use the correct tool calling syntax. If your tool call returns with no output, it means you have failed to use the correct syntax: fix your syntax and try again.
                All your reports should be in paragraph form, and not in point form.
            """
            langgraph.start()
        
            
        main()
        ```
        
5. Run the main.py file from IMDA-Agentic-2 via the command line.  

```python
python3 src/main.py
```

# Caching

LLM-generated output is nondeterministic. For consistency and for demo purposes, we can opt to cache (i.e. save) the result of a successful run. 

Caching saves the result of a run in the .cache folder. The results can then be replayed in the future with the original cache seed and identical prompts. 

Caching is only supported by autogen. 

### Making a cache

Enter the src folder. Search for `Cache.disk` within the file defining the autogen agents. For instance, if a groupchat run is to be cached, go to src/AutogenGroupChatAgentic.py.

```python
with Cache.disk(cache_seed=103) as cache: # Modify the cache seed
                groupchat_history_custom = self.user_proxy.initiate_chat(
                    self.manager,
                    message = self.task,
                    cache = cache,
                )
            
                return groupchat_history_custom
```

To create a new cache, change the value of the `cache_seed` to a number that DOES NOT ALREADY APPEAR within the .cache folder. 

To OVERWRITE a previously cached run,  set the `cache_seed` to the cache seed of the run that is to be overwritten. This may be necessary if we wish to overwrite the result of a failed run. Make sure to 

# Troubleshooting

### RuntimeError: Code execution is set to be run in docker (default behaviour) but docker is not running

Either: Activate Docker 

Or: Set AUTOGEN_USE_DOCKER to "0/False/no" in your environment variables by running `export AUTOGEN_USE_DOCKER=0`  on the command line from the IMDA-Agentic-2 folder. 

### Agents taking too long

Either: Wait out and let them cook. 

Or: Reduce the context size. See for more details: 

### Tool calls not working

1. Make sure the agent is actually making a tool call. This is what a successful tool call looks like in autogen: 
    
    ```python
    ***** Suggested tool call (call_9oop6ond): search_and_crawl *****
    Arguments: 
    {"external_search_query":"Mira Murati"}
    *****************************************************************
    ```
    
    If the agent is not making any tool calls where it should, change the cache seed or the prompts and rerun the file. 
    
2. If external search is called but doesn’t work: 
    1. Make sure Firefox is installed and working. A Firefox browser should open when this tool is called. 
    2. It is possible that the websites visited do not have extractable texts. (e.g. LinkedIn sign-in page)
3. If internal search is called but doesn’t work: 
    1. Check that the chroma_db folder exists in IMDA-Agentic-2. This should be the case if the code is cloned from the repo. If not, create the database and name it ‘internal_info’. Refer to: 
        
        [RAG Database Setup: Chroma-DB](https://www.notion.so/RAG-Database-Setup-Chroma-DB-77cf6c2c3fa14cdf9f08facce0a2dbeb?pvs=21)
        

### post_message/post_internal_message not working

Check that these two environmental variables: `URL_LOG` and `URL_OUTPUT` have been defined. Provide the Slack webhook urls for these variables if Slack integration is required. Otherwise, provide dummy urls to prevent errors from being thrown. 

Alternatively, informed users may edit the source code to remove message-posting capabilities.
