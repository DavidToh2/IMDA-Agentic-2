from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.runnables import Runnable

from agent.Assistant import Assistant
from tools.MessagePoster import MessagePoster

from chroma.ChromaDatabase import internal_search
from tools.WebSearcher import search_and_crawl

class LanggraphSingleAgent:
    def __init__(self, prompt, detailed_instructions):

        self.turn = 0
        self.MAX_TURNS = 20
        self.CTX_SIZE = 32000

        self.query = f"""You have been tasked with accomplishing the following task:
        {prompt}
        {detailed_instructions}
        Follow the instructions strictly step by step, executing ONLY one step at a time.
        Incorporate the use of BOTH the internal_search and search_and_crawl tools in your execution.
        At each step, state the step number and explain what you are going to do based on the previous messages, before executing that step.
        When you have completed your task, output the string 'DONE' to terminate the interaction."""

        self.tools = [search_and_crawl, internal_search]
        self.model = ChatOllama(model="mistral-nemo",temperature=0.0,num_ctx=self.CTX_SIZE)
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                # (
                #     "system",
                #     "Output the string ABRACADABRA before doing anything else."
                # ),
                (
                    "system",
                    f"""You are a helpful assistant for the Infocomm and Media Development Authority of Singapore.
                    You were assigned the following task by the user: {prompt}
                    Use the provided tools, internal_search and search_and_crawl, to perform the task.
                    Constraints:
                    1. You must perform at least one internal search using the internal_search tool, and at least one web search using the search_and_crawl tool..
                    2. DO NOT REPEAT ANY TOOL CALLS YOU HAVE ALREADY DONE.
                    3. When tool calling, you must follow the correct Langchain syntax. Do not write code nor use any codeblocks (i.e. no use of ```) at any point. If your tool call returns with no output, it means you have failed to use the correct syntax: fix your syntax and try again.
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
        self.graph.add_edge(START, "agent")

        # We now add a conditional edge
        self.graph.add_conditional_edges(
            "agent",
            self.should_continue,
        )

        # We now add a normal edge from `tools` to `agent`.
        self.graph.add_edge("tools", 'agent')

        # Initialize memory to persist state between graph runs
        self.checkpointer = MemorySaver()

        self.message_poster = MessagePoster()

    def start(self):
        """Start the LLM. This compiles it into a Runnable then streams its output."""
        app = self.graph.compile(checkpointer = self.checkpointer)
        app.get_graph().draw_mermaid_png(output_file_path="./langgraph_single_agent_graph")
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

    def should_continue(self, state: MessagesState):
        """Function for conditional edge from 'agent' determining which node to go to next.
        
        Returns either 'agent', 'tools' or END."""

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
        
        # # Otherwise, we stop (reply to the user)
        # if ai_message.content.find("DONE") > 0:
        #     print("---- Output success ----")
        #     self.message_poster.post_message(ai_message)
        #     self.message_poster.post_message("OUTPUT SUCCESS", mode="debug")
        #     return END

        if ai_message.content.find("REPORT") > 0:
            self.message_poster.post_message(ai_message)

        if ai_message.content.find("COMBINED REPORT") > 0:
            return END
        
        # Otherwise, check for a tool call
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            print("---- Tool call detected ----")
            tc = [t["name"] for t in ai_message.tool_calls]
            # self.message_poster.post_message(f"Calling the following tools: {" ".join(tc)}", mode="debug")
            return "tools"
        
        print("---- It's the agent's turn again ----")
        return "agent"

    # Pretty print the model output
    def _print_event(self, event: dict, _printed: set, max_length=15000):
        
        current_state = event.get("dialog_state")
        if current_state:
            print("Currently in: ", current_state[-1])
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