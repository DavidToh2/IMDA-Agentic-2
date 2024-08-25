
from agent.AgentFlowControl import ToExternalSearchAgent, ToInternalSearchAgent, ToWriterAgent, CompleteTask
from chroma.ChromaDatabase import internal_search
from tools.WebSearcher import search_and_crawl
from agent.State import State

from typing import Callable

class LanggraphAgentConfig:

    def __init__(self, prompt, detailed_instructions):

        INTERNAL_SEARCHER_PROMPT = f"""You are an agent in charge of searching the internal database using the internal_search tool.
        When called, you must refer to the previous message, issued by the supervisor agent, for instructions on what to search for.
        Your search should be relevant to the overall task given by the user.
        The task is as follows: {prompt} 
        Once you have understood the supervisor's instructions, perform a tool call using the internal_search tool.
        Your search will not have been performed until the tool is actually called."""

        EXTERNAL_SEARCHER_PROMPT = f"""You are an agent in charge of searching the web using the search_and_crawl tool.
        When called, you must refer to the previous message, issued by the supervisor agent, for instructions on what to search for.
        Your search should be relevant to the overall task given by the user.
        The task is as follows: {prompt} 
        Once you have understood the supervisor's instructions, perform a tool call using the search_and_crawl tool.
        Your search will not have been performed until the tool is actually called."""

        WRITER_PROMPT = f"""You are a writer agent.
        When called, you must refer to the previous message, issued by the supervisor agent, for instructions on exactly what to do.
        This will usually require you to use the contents of the messages from filter_agent."""

        self.supervisor_tools = [ToWriterAgent, ToInternalSearchAgent, ToExternalSearchAgent]
        self.agent_tools = [internal_search, search_and_crawl]
        self.agents = [
            {
                "name": "internal_searcher",
                "prompt": INTERNAL_SEARCHER_PROMPT,
                "tools": [internal_search]
            },
            {
                "name": "external_searcher",
                "prompt": EXTERNAL_SEARCHER_PROMPT,
                "tools": [search_and_crawl]
            },
            {
                "name": "writer",
                "prompt": WRITER_PROMPT
            }
        ]
    
    def route_agent(self, state: State, callback: Callable):
        msg = state["messages"][-1]
        tc = msg.tool_calls
        if tc:
            match(tc[0]["name"]):
                case ToWriterAgent.__name__:
                    return "enter_writer"
                case ToExternalSearchAgent.__name__:
                    return "enter_external_searcher"
                case ToInternalSearchAgent.__name__:
                    return "enter_internal_searcher"
                case CompleteTask.__name__:
                    callback(msg)
                    return "__end__"
        return "supervisor"