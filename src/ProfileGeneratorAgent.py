from typing import Annotated, Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

from agent.AgentBase import AgentBase
from agent.Assistant import Assistant
from agent.AgentControlFlow import ToExternalSearchAgent, ToInternalSearchAgent, ToWriterAgent, CompleteTask
from agent.State import State
from tools.MessagePoster import MessagePoster

from chroma.ChromaDatabase import internal_search
from tools.WebSearcher import search_and_crawl

class LanggraphAgent:
    def __init__(self, prompt, detailed_instructions):

        self.turn = 0
        self.MAX_TURNS = 20

        self.query = f"""You have been tasked with accomplishing the following task:
        {prompt}

        Detailed instructions follow:
        {detailed_instructions}"""

        # Define a new graph
        self.graph = StateGraph(State)
        self.model = AgentBase(16000, 0.0)
        
        SUPERVISOR_PROMPT = f"""You are a supervisor in charge of a team of agents.
        You were assigned the following task by the user: {prompt}
        Follow the detailed instructions step by step.

        At each step, you must rely on the previous messages to identify which step you are at.
        You must then delegate the corresponding sub-task to the relevant sub-agent. 
        Instruct the sub-agent on what to do, specifying any tool calls they must make (if any).

        When a sub-agent completes their sub-task, evaluate their output to determine if it adheres satisfactorily to the instruction given. If the output is satisfactory, proceed to issue instructions to the next sub-agent and pass control to them.
        If the output is not satisfactory, prompt the previous sub-agent to repeat the task, giving concise instructions on how its output may be improved.

        When you have completed the overall task, output the string 'DONE' to terminate the interaction.
        """

        supervisor_runnable = self.model.spawn_runnable(
            SUPERVISOR_PROMPT, [ToWriterAgent, ToInternalSearchAgent, ToExternalSearchAgent, CompleteTask]
        )

        TOOL_CALL_FILTER_PROMPT = f"""You are a filter agent, in charge of summarising the results of the previous tool call.
        Your job is to summarise those parts of the previous ToolMessage that are relevant to the overall task given by the user.
        The task is as follows: {prompt}

        In your summary, make sure you filter out ALL parts of the previous ToolMessage irrelevant to the task, and ONLY include those parts that are relevant.
        For example, if the previous ToolMessage is a webpage dump provided by search_and_crawl, you should ignore all privacy policy, copyright, search or cookie-related terms, as well as all webpage-specific terms like "previous", "next" and "book now".
        As another example, if the previous ToolMessage came from the results of an internal_search, you should filter out all results that talk about things other than the task, and only return those texts that directly relate to the task.

        If you believe that no part of the ToolMessage is relevant, output the string "NO RELEVANT CONTENT FOUND, PLEASE REPEAT TOOL CALL".
        """

        tool_call_filter_runnable = self.model.spawn_runnable(
            TOOL_CALL_FILTER_PROMPT
        )

        INTERNAL_SEARCHER_PROMPT = f"""You are an agent in charge of searching the internal database using the internal_search tool.
        When called, you must refer to the previous message, issued by the supervisor agent, for instructions on what to search for.
        Your search should be relevant to the overall task given by the user.
        The task is as follows: {prompt}
        Once you have understood the supervisor's instructions, perform a tool call using the internal_search tool, passing the appropriate search terms into the internal_search_query argument.
        Do not, at any point, repeat previous searches using the exact same search terms.
        """

        internal_searcher_runnable = self.model.spawn_runnable(
            INTERNAL_SEARCHER_PROMPT, [internal_search]
        )

        EXTERNAL_SEARCHER_PROMPT = f"""You are an agent in charge of searching the web using the search_and_crawl tool.
        When called, you must refer to the previous message, issued by the supervisor agent, for instructions on what to search for.
        Your search should be relevant to the overall task given by the user.
        The task is as follows: {prompt}
        Once you have understood the supervisor's instructions, perform a tool call using the search_and_crawl tool, passing the appropriate search terms into the external_search_query argument, and the number of webpages to fetch into the num_pages argument.
        Do not, at any point, repeat previous searches using the exact same search terms.
        """

        external_searcher_runnable = self.model.spawn_runnable(
            EXTERNAL_SEARCHER_PROMPT, [search_and_crawl]
        )

        WRITER_PROMPT = f"""You are a writer agent.
        When called, you must refer to the previous message, issued by the supervisor agent, for instructions on exactly what to do.
        This will usually require you to use the contents of the messages from filter_agent.
        """

        writer_runnable = self.model.spawn_runnable(
            WRITER_PROMPT
        )

        self.graph.add_node("supervisor", Assistant(supervisor_runnable))
        self.graph.add_node("tool_call_filter", Assistant(tool_call_filter_runnable))
        self.graph.add_node("internal_searcher", Assistant(internal_searcher_runnable))
        self.graph.add_node("external_searcher", Assistant(external_searcher_runnable))
        self.graph.add_node("writer", Assistant(writer_runnable))
        self.graph.add_node("tools", self.create_tool_node_with_fallback(self.tools))

        self.graph.add_edge(START, "supervisor")

        self.graph.add_conditional_edges("supervisor", self.route_agent)

        self.graph.add_edge("tools", "tool_call_filter")
        self.graph.add_edge("tool_call_filter", "supervisor")

        self.checkpointer = MemorySaver()

        self.message_poster = MessagePoster()

    def start(self):
        # Finally, we compile it!
        # This compiles it into a LangChain Runnable,
        # meaning you can use it as you would any other runnable.
        # Note that we're (optionally) passing the memory when compiling the graph
        app = self.graph.compile(checkpointer = self.checkpointer)

        # Use the Runnable
        _events = app.stream(
            {"messages": [ HumanMessage(content = self.query)] },
            config= {"configurable": {"thread_id": 42}},
            stream_mode = "values"
        )
        _printed = set()
        for _event in _events:
            self._print_event(_event, _printed)

        return _events
    
    def route_agent(self, state: State):
        self.turn += 1
        msg = state["messages"][-1]
        tc = msg.tool_calls
        if tc:
            match(tc[0]["name"]):
                case ToWriterAgent.__name__:
                    return "writer"
                case ToExternalSearchAgent.__name__:
                    return "external_searcher"
                case ToInternalSearchAgent.__name__:
                    return "internal_searcher"
                case CompleteTask.__name__:
                    self.message_poster.post_message(msg)
                    return END
        return "supervisor"

    def route_tools(self, state: State):
        self.turn += 1
        dialog_state = state["dialog_state"]

        msg = state["messages"][-1]
        tc = msg.tool_calls
        if tc:
            return "tools"
        return dialog_state

    # Define the function that determines whether to continue or not
    def should_continue(self, state: MessagesState):

        # Terminate if 10 messages have already passed
        self.turn += 1
        
        # Grab the last message...
        messages = state['messages']
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")

        # If 10 turns, terminate
        if self.turn >= self.MAX_TURNS:
            print("---- Max turns reached ----")
            self.message_poster.post_message(ai_message)
            self.message_poster.post_message(f"MAX NO. OF TURNS REACHED", mode="debug")
            return END
        
        # Otherwise, we stop (reply to the user)
        if ai_message.content.find("DONE") > 0:
            print("---- Output success ----")
            self.message_poster.post_message(ai_message)
            self.message_poster.post_message("OUTPUT SUCCESS", mode="debug")
            return END
        
        # Otherwise, check for a tool call
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            print("---- Tool call detected ----")
            tc = [t["name"] for t in ai_message.tool_calls]
            self.message_poster.post_message(f"Calling the following tools: {" ".join(tc)}", mode="debug")
            return "tools"
        
        print("---- It's the agent's turn again ----")
        if ai_message.content.find("PROFILE") > 0:
            self.message_poster.post_message(ai_message)
        return "agent"

    # Pretty print the model output
    def _print_event(self, event: dict, _printed: set, max_length=15000):
        
        message = event.get("messages")
        if message:
            if isinstance(message, list):
                if isinstance(message[-1], ToolMessage):
                    message_2 = ToolMessage(content = " ".join([t.content for t in message if t.id not in _printed]), id = f"{message[-1].id}", tool_call_id = f"{message[-1].tool_call_id}")
                    message = message_2
                else:
                    message = message[-1]
            if message.id not in _printed:
                msg_repr = message.pretty_repr(html=True)
                if len(msg_repr) > max_length:
                    msg_repr = msg_repr[:max_length] + " ... (truncated)"
                print(msg_repr)
                _printed.add(message.id)

    # Pretty print tool error
    def handle_tool_error(self, state) -> dict:
        error = state.get("error")
        tool_calls = state["messages"][-1].tool_calls
        return {
            "messages": [
                ToolMessage(
                    content=f"Error: {repr(error)}\nPlease fix your mistakes.",
                    tool_call_id=tc["id"],
                )
                for tc in tool_calls
            ]
        }

    def create_tool_node_with_fallback(self, tools: list) -> dict:
        return ToolNode(tools).with_fallbacks(
            [RunnableLambda(self.handle_tool_error)], exception_key="error"
        )