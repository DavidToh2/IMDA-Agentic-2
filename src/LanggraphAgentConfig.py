
from agent.AgentFlowControl import ToExternalSearchAgent, ToInternalSearchAgent, ToWriterAgent, CompleteTask
from chroma.ChromaDatabase import internal_search
from tools.WebSearcher import search_and_crawl
from agent.State import State

from typing import Callable

class LanggraphAgentConfig:

    def __init__(self, prompt, detailed_instructions):

        INTERNAL_SEARCHER_PROMPT = f"""You are an agent whose only job is to invoke the internal_search tool to search the internal database.
        Pass in the relevant search parameters into the internal_search_query parameter, based on the instructions in the previous message.
        You are not to output the actual results of the search - this is the job of another agent.
        Perform your tool call using correct LangChain syntax. You must preface each tool call with the string '[TOOL_CALLS]'.
        DO NOT OUTPUT CODE. DO NOT USE ANY CODEBLOCKS (i.e. no use of ``` allowed)."""

        EXTERNAL_SEARCHER_PROMPT = f"""You are an agent whose only job is to invoke the search_and_crawl tool to search the web.
        Pass in the relevant search parameters into the external_search_query parameter, based on the instructions in the previous message.
        You are not to output the actual results of the search - this is the job of another agent.
        Perform your tool call using correct LangChain syntax. You must preface each tool call with the string '[TOOL_CALLS]'.
        DO NOT OUTPUT CODE. DO NOT USE ANY CODEBLOCKS (i.e. no use of ``` allowed)."""

        WRITER_PROMPT = f"""You are a writer agent.
        When called, you must refer to the previous message, issued by the supervisor agent, for instructions on exactly what to do.
        This will usually require you to use the contents of the messages from filter_agent."""

        self.supervisor_tools = [ToWriterAgent, ToInternalSearchAgent, ToExternalSearchAgent]
        self.agent_tools = [internal_search, search_and_crawl]
        self.agents = {
            "internal_searcher": {
                "prompt": INTERNAL_SEARCHER_PROMPT,
                "tools": [internal_search]
            },
            "external_searcher": {
                "prompt": EXTERNAL_SEARCHER_PROMPT,
                "tools": [search_and_crawl]
            },
            "writer": {
                "prompt": WRITER_PROMPT
            }
        }
    
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