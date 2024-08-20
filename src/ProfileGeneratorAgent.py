from typing import Annotated, Literal, TypedDict

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage

from agent.Agent import Assistant

from chroma.ChromaDatabase import internal_search
from tools.WebSearcher import search_and_crawl

class ProfileGeneratorAgent:
    def __init__(self, query):

        self.turn = 0
        self.query = f"""You have been tasked with accomplishing the following task:
        {query}
        Start by providing a step-by-step plan of how you would accomplish the task.
        Incorporate the use of both the search_and_crawl tool (for online searching) and the internal_search tool (for searching the internal database) in your plan.
        Following that, execute your plan step by step.
        At each step, you may rely on the previous messages to identify which step you are at, before proceeding with the next step.
        When you believe you are done with your task, output the string 'DONE'."""

        self.tools = [search_and_crawl, internal_search]
        self.model = ChatOllama(model="mistral-nemo",temperature=1.0,num_ctx=64000)
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                # (
                #     "system",
                #     "Output the string ABRACADABRA before doing anything else."
                # ),
                (
                    "system",
                    """You are a helpful assistant for the Infocomm and Media Development Authority of Singapore.
                    You will be given a task by the user. Use the provided tools, internal_search and search_and_crawl to perform the task.
                    Constraints:
                    1. You must perform at least one internal search using the internal_search tool, and at least one web search using the search_and_crawl tool..
                    2. You should not perform repeated web searches, using the search_and_crawl tool, that have exactly the same search terms.
                    """
                ),
                ("placeholder", "{messages}"),
            ])

        assistant_runnable = self.prompt | self.model.bind_tools(self.tools)

        # Define a new graph
        self.graph = StateGraph(MessagesState)

        # Define the two nodes we will cycle between
        self.graph.add_node("agent", Assistant(assistant_runnable))
        self.graph.add_node("tools", self.create_tool_node_with_fallback(self.tools))

        # Set the entrypoint as `agent`
        # This means that this node is the first one called
        self.graph.add_edge(START, "agent")

        # We now add a conditional edge
        self.graph.add_conditional_edges(
            # First, we define the start node. We use `agent`.
            # This means these are the edges taken after the `agent` node is called.
            "agent",
            # Next, we pass in the function that will determine which node is called next.
            self.should_continue,
        )

        # We now add a normal edge from `tools` to `agent`.
        # This means that after `tools` is called, `agent` node is called next.
        self.graph.add_edge("tools", 'agent')

        # Initialize memory to persist state between graph runs
        self.checkpointer = MemorySaver()

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

    # Define the function that determines whether to continue or not
    def should_continue(self, state: MessagesState):

        # Terminate if 10 messages have already passed
        self.turn += 1
        if self.turn >= 10:
            return END
        
        # Else, grab the last message...
        messages = state['messages']
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        
        # and check for a tool call
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        # Otherwise, we stop (reply to the user)
        elif ai_message.content.find("DONE") > 0:
            return END
        else:
            return "agent"

    # Pretty print the model output
    def _print_event(self, event: dict, _printed: set, max_length=15000):
        current_state = event.get("dialog_state")
        if current_state:
            print("Currently in: ", current_state[-1])
        message = event.get("messages")
        if message:
            if isinstance(message, list):
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
                    content=f"Error: {repr(error)}\n please fix your mistakes.",
                    tool_call_id=tc["id"],
                )
                for tc in tool_calls
            ]
        }

    def create_tool_node_with_fallback(self, tools: list) -> dict:
        return ToolNode(tools).with_fallbacks(
            [RunnableLambda(self.handle_tool_error)], exception_key="error"
        )