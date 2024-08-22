from agent.Agent import Agent

class Assistant(Agent):
    def __init__(self):
        super().__init__()

        self.MAX_TURNS = 20

        self.query = f"""You have been tasked with accomplishing the following task:
        {prompt}
        {detailed_instructions}
        
        Execute your plan step by step. Incorporate the use of BOTH the internal_search and search_and_crawl tools in your execution.
        At each step, you must rely on the previous messages to identify which step you are at, before proceeding with the next step.
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