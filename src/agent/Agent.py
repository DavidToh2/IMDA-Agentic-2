from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

class Agent:
    def __init__(self, system_prompt="", local_llm='elvee/hermes-2-pro-llama-3:8b-Q5_K_M',temperature=0.0):  
        self.llm = ChatOllama(model=local_llm, temperature=temperature)
        self.system_prompt = system_prompt
        self.log = {"inputs":[],"outputs":[]}

    def sendSync(self, input="", printout=False) -> str:
        prompt = ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("user", "{input}")]
        )

        output_chain = prompt | self.llm
        output = output_chain.invoke({"input": input})
        
        self.log["inputs"].append(input)
        self.log["outputs"].append(output.content)

        if printout:
            print(output.content)

        return output.content
    
    async def send(self, input="", printout=False) -> str:
        # https://python.langchain.com/v0.2/docs/how_to/streaming/#using-stream-events
        prompt = ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("user", "{input}")]
        )
        output_chain = prompt | self.llm

        if printout:
            try:
                async for event in output_chain.astream_events(input={"input": input}, version="v2", include_types=["chat_model"]):
                    if event["event"] == "on_chat_model_stream":
                        print(event['data']['chunk'].content, end="", flush=True)
                    if event["event"] == "on_chat_model_end":
                        output = event['data']['output'].content
                        self.log["inputs"].append(input)
                        self.log["outputs"].append(output)
                        print("\n")
                        return output
            except Exception as e:
                print(f"The following exception occured while attempting to parse output asynchronously (with printout):\n{e}")
        else:
            try:
                async for event in output_chain.astream_events(input, version="v2", include_types=["chat_model"]):
                    if event["event"] == "on_chat_model_end":
                        output = event['data']['output'].content
                        self.log["inputs"].append(input)
                        self.log["outputs"].append(output)
                        return output
            except Exception as e:
                print(f"The following exception occured while attempting to parse output asynchronously:\n{e}")
    