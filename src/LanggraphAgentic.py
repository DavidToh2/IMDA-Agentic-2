from typing import Callable

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

from LanggraphAgentConfig import LanggraphAgentConfig
from agent.AgentBase import AgentBase
from agent.AgentFlowControl import CompleteTask
from agent.Assistant import Assistant
from agent.State import State
from tools.MessagePoster import MessagePoster

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

        self.config = LanggraphAgentConfig(prompt, detailed_instructions)

                        # SUPERVISOR AGENT

        SUPERVISOR_PROMPT = f"""You are a supervisor in charge of a team of agents.
        You were assigned the following task by the user: {prompt}
        Follow the detailed instructions step by step.

        At each step, you must rely on the previous messages to identify which step you are at.
        You must then delegate the corresponding sub-task to the relevant sub-agent. 
        Instruct the sub-agent on what to do, specifying any tool calls they must make (if any).
        You should only issue one set of instructions to one sub-agent at once.

        When a sub-agent completes their sub-task, evaluate their output to determine if it adheres satisfactorily to the instruction given. If the output is satisfactory, proceed to issue instructions to the next sub-agent and pass control to them.
        If the output is not satisfactory, prompt the previous sub-agent to repeat the task, giving concise instructions on how its output may be improved.
        When you have completed the overall task, call the CompleteTask tool to finish the job."""

        supervisor_runnable = self.model.spawn_runnable(
            SUPERVISOR_PROMPT, self.config.supervisor_tools + [CompleteTask]
        )
        self.graph.add_node("supervisor", Assistant(supervisor_runnable))

                        # TOOL CALL FILTER AGENT

        TOOL_CALL_FILTER_PROMPT = f"""You are a filter agent, in charge of summarising the results of the previous tool call.
        Your job is to summarise those parts of the previous ToolMessage that are relevant to the overall task given by the user.
        The task is as follows: {prompt} 
        In your summary, make sure you filter out ALL parts of the previous ToolMessage irrelevant to the task, and ONLY include those parts that are relevant.
        For example, if the previous ToolMessage is a webpage dump provided by search_and_crawl, you should ignore all privacy policy, copyright, search or cookie-related terms, as well as all webpage-specific terms like 'previous', 'next' and 'book now'.
        As another example, if the previous ToolMessage came from the results of an internal_search, you should filter out all results that talk about things other than the task, and only return those texts that directly relate to the task.
        If you believe that no part of the ToolMessage is relevant, output the string 'NO RELEVANT CONTENT FOUND, PLEASE REPEAT TOOL CALL."""

        tool_call_filter_runnable = self.model.spawn_runnable(
            TOOL_CALL_FILTER_PROMPT
        )
        self.graph.add_node("tool_call_filter", Assistant(tool_call_filter_runnable))

                        # AGENT, ENTRY_AGENT AND TOOL_AGENT NODEs

        self.agent_runnables = {}
        for agent, c in self.config.agents.items():
            if "tools" in c:
                self.graph.add_node(f"enter_{agent}", self.create_entry_node(agent, agent))
                self.agent_runnables[agent] = self.model.spawn_runnable(c["prompt"], c["tools"])
                self.graph.add_node(agent, Assistant(self.agent_runnables[agent]))
                self.graph.add_node(f"tools_{agent}", self.create_tool_node_with_fallback(c["tools"]))

                self.graph.add_edge(f"enter_{agent}", agent)
                self.graph.add_conditional_edges(agent, self.tool_router)
                self.graph.add_edge(f"tools_{agent}", "tool_call_filter")
            else:
                self.graph.add_node(f"enter_{agent}", self.create_entry_node(agent, agent))
                self.agent_runnables[agent] = self.model.spawn_runnable(c["prompt"])
                self.graph.add_node(agent, Assistant(self.agent_runnables[agent]))

                self.graph.add_edge(f"enter_{agent}", agent)
                self.graph.add_edge(agent, "exit_agent")

                        # EXIT NODE

        self.graph.add_node("exit_agent", self.pop_dialog_state)

                        # Graph edges:

        self.graph.add_edge(START, "supervisor")
        self.graph.add_conditional_edges("supervisor", self.agent_router)

        self.graph.add_edge("tool_call_filter", "exit_agent")
        self.graph.add_edge("exit_agent", "supervisor")

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
    
    def agent_router(self, state: State):
        self.turn += 1
        if self.turn >= 10:
            return "__end__"
        return self.config.route_agent(state, self.message_poster.post_message)

    def tool_router(self, state: State):
        self.turn += 1
        dialog_state = state["dialog_state"][-1]

        msg = state["messages"][-1]
        tc = msg.tool_calls
        if tc:
            ret = f"tools_{dialog_state}"
        else:
            ret = dialog_state
        
        print(f"Tool router for node {dialog_state} routed to {ret}")
        return ret

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
    
    def create_entry_node(self, assistant_name: str, new_dialog_state: str) -> Callable:
        def entry_node(state: State) -> dict:
            tool_call_id = state["messages"][-1].tool_calls[0]["id"]
            ret = {
                "messages": [
                    ToolMessage(
                        content=f"""The assistant is now the {assistant_name}.\n{self.config.agents[new_dialog_state]["prompt"]}""",
                        tool_call_id = tool_call_id,
                    )
                ],
                "dialog_state": new_dialog_state,
            }
            return ret

        return entry_node
    
    def pop_dialog_state(self, state: State) -> dict:
        """Pop the dialog stack and return to the main assistant.
        This lets the full graph explicitly track the dialog flow and delegate control to specific sub-graphs.
        """
        messages = []
        if state["messages"][-1].tool_calls:
            # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
            messages.append(
                ToolMessage(
                    content = """Resuming dialog with the supervisor. Please reflect on the past conversation and continue with the next step of the user's instructions.""",
                    tool_call_id = state["messages"][-1].tool_calls[0]["id"],
                )
            )
        return {
            "dialog_state": "pop",
            "messages": messages,
        }

    def create_tool_node_with_fallback(self, tools: list) -> dict:
        return ToolNode(tools).with_fallbacks(
            [RunnableLambda(self.handle_tool_error)], exception_key="error"
        )