
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_ollama import ChatOllama

class AgentBase:
    def __init__(self, ctx_size, temp, model = "mistral-16K:latest"):
        self.CTX_SIZE = ctx_size
        self.TEMP = temp
        self.model = ChatOllama(model = model, temperature = self.TEMP, num_ctx = self.CTX_SIZE)

    def spawn_runnable(self, system_prompt, tools = []):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{messages}"),
            ])
        if tools:
            return (prompt | self.model.bind_tools(tools))
        else:
            return (prompt | self.model)
