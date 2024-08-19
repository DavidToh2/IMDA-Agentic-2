import os
from datetime import datetime
from ssl import ALERT_DESCRIPTION_BAD_CERTIFICATE_HASH_VALUE

from autogen import (
    Agent,
    AssistantAgent,
    ConversableAgent,
    GroupChat,
    GroupChatManager,
    UserProxyAgent,
    config_list_from_json,
    register_function,
)

from autogen.cache import Cache
from chroma.ChromaDatabase import internal_search
from tools.WebSearcher import search_and_crawl

# speakers = ["Dario Amodei",
#             "Gaspard Twagirayezu",
#             "Hu Heng Hua"]

# event = "ATx Summit Plenary"
# task = "Generate speaker profiles for "

class ProfileGeneratorAgent:
    def __init__(
            self,
            task
            ):
        
        self.config_list = [
            {
                "model": "mistral-nemo:latest", 
                "api_key": "ollama", 
                "base_url": "http://localhost:11434/v1", 
                #"temperature":0.0
                "price" : [0.0, 0.0]
            }
        ]

        self.task = task

        self.user_proxy = UserProxyAgent(
            name = "Admin",
            system_message="A human admin. Give the task, and send instructions to writer to refine the profile.",
            code_execution_config=False,
        )

        self.planner = AssistantAgent(
            name = "Planner",
            system_message=f"""You are a planner. You will be given an overarching task involving the generation of profiles.
            Give a step-by-step breakdown of how you would accomplish this task, listing out all information required for each step.
            Your plan should consist of no more than five steps.
             
            The task description follows:
            {task} """,
            llm_config={"config_list": self.config_list, "cache_seed": None},
        )

        self.supervisor = AssistantAgent(
            name = "Supervisor",
            system_message = f"""You are a supervisor in charge of a team of AI agents in a group chat. 
            Your task is to supervise your team of AI agents to accomplish the goal in the given prompt, by instructing each agent on what to do.
            Your instructions should be based on the following plan:
            Step 1. Find a list of all speakers by performing an online search using the search_and_crawl tool
            Step 2. For each speaker, perform an online search using the search_and_crawl tool
            Step 3. For each speaker, perform an internal search using the internal_search tool
            Step 4. Synthesize the profiles of all speakers
            Ensure that your instructions adhere to the order of steps given in the plan.
            Keep your instructions as short as possible and relevant to the overall task.
            Note that, if the previous agent did not return anything, you do not need to repeat their task. Just move on to the next agent and instruct them.

            The task description follows:
            {task} """,
            llm_config={"config_list": self.config_list, "cache_seed": None},
        )

        self.extractor = AssistantAgent(
            name = "Extractor",
            system_message=f"""You will be provided with the text dump of a webpage in the previous message.
            Your job is to extract the text relevant to the task.
            Ignore all privacy policy, copyright, search or cookie-related terms. Ignore all functional terms like "previous", "next" and "book now". Ignore all common, repeated and filler words if they do not directly contribute to the task.

            The task description follows:
            {task}
            """,
            llm_config={"config_list": self.config_list, "cache_seed": None},
        )

        self.external_searcher = AssistantAgent(
            name="External Searcher",
            llm_config={"config_list": self.config_list, "cache_seed": None},
            system_message=f"""Your job is to search the web for information according to instructions provided by the supervisor in the previous message.
            This information will be used to help accomplish a larger task. 

            The task description follows:
            {task}""",
        )
        self.external_searcher.register_for_llm(name="search_and_crawl", description="A web searcher")(search_and_crawl)
        self.user_proxy.register_for_execution(name="search_and_crawl")(search_and_crawl)

        self.internal_searcher = AssistantAgent(
            name="Internal Searcher",
            llm_config={"config_list": self.config_list, "cache_seed": None},
            system_message=f"""Your job is to search the internal database for information according to instructions provided by the supervisor in the previous message.
            This information will be used to help accomplish a larger task.

            The task description follows:
            {task}""",
        )
        self.internal_searcher.register_for_llm(name="internal_search", description="Searches the internal database")(internal_search)
        self.user_proxy.register_for_execution(name="internal_search")(internal_search)

        self.writer = AssistantAgent(
            name="Writer",
            llm_config={"config_list": self.config_list, "cache_seed": None},
            system_message=f"""Writer. Please write the profile in markdown format (with relevant titles) and put the content in pseudo ```md``` code block, based on the planner's instructions.
            Extract relevant information from the result of the External Searcher and Internal Searcher agents.
            
            The task description follows:
            {task}""",
        )

        def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
            """Define a customized speaker selection function.
            A recommended way is to define a transition for each speaker in the groupchat.

            Returns:
                Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
            """
            messages = groupchat.messages

            ordering = [self.supervisor,
                        self.external_searcher,
                        self.user_proxy,
                        self.extractor,
                        self.supervisor,
                        self.external_searcher,
                        self.user_proxy,
                        self.extractor,
                        self.supervisor,
                        self.internal_searcher,
                        self.user_proxy,
                        self.supervisor,
                        self.writer,
                        self.supervisor,
                        self.external_searcher,
                        self.user_proxy,
                        self.extractor,
                        self.supervisor,
                        self.writer
                        ]
            if len(messages) <= len(ordering):
                return ordering[len(messages)-1]


            elif last_speaker is self.planner:
                # if the last message is from planner, let the crawler search
                return self.external_searcher
            
            elif last_speaker is self.user_proxy:
                if messages[-1]["content"].strip() != "" and messages[-1]["content"].strip()[0] == "#" :
                    # If the last message is the result of a tool call from user and is not empty, let the writer continue
                    return self.writer
                else: 
                    return self.planner     

            elif last_speaker is self.external_searcher:
                return self.user_proxy

            elif last_speaker is self.writer:
                # Always let the user to speak after the writer
                return self.internal_searcher

            else:
                # default to auto speaker selection method
                return "auto"


        self.groupchat = GroupChat(
            agents = [self.user_proxy, self.writer, self.external_searcher, self.planner, self.extractor, self.internal_searcher, 
                        self.supervisor, self.extractor],
            messages = [],
            max_round = 15,
            speaker_selection_method = custom_speaker_selection_func,
        )
        self.manager = GroupChatManager(groupchat = self.groupchat, llm_config = {"config_list": self.config_list, "cache_seed": None})

    def start(self):
        with Cache.disk(cache_seed=43) as cache:
            groupchat_history_custom = self.user_proxy.initiate_chat(
                self.manager,
                message = self.task,
                cache = cache,
            )
        
            return groupchat_history_custom