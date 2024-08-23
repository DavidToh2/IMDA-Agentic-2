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
from chroma.ChromaDatabase import internal_search_autogen
from tools.WebSearcher import search_and_crawl_autogen
from tools.MessagePoster import MessagePoster

class ProfileGeneratorAgent:
    def __init__(
            self,
            speaker
            ):
        
        self.config_list = [
            {
                "model": "mistral-16K:latest", 
                "api_key": "ollama", 
                "base_url": "http://localhost:11434/v1", 
                #"temperature":0.0
                "price" : [0.0, 0.0]
            }
        ]

        self.task = "Generate a speaker profile for " + speaker

        self.user_proxy = UserProxyAgent(
            name="User Proxy",
            system_message="A human admin. Give the task, and send instructions to writer to refine the profile.",
            code_execution_config=False,
        )

        self.orchestrator = AssistantAgent(
            name="Orchestrator",
            system_message=f"""Orchestrator. Please determine what information is needed to {self.task}. """,
            llm_config={"config_list": self.config_list, "cache_seed": None},
        )

        self.supervisor = AssistantAgent(
            name = "Supervisor",
            system_message=f"""Supervisor. Ignore the group manager. Your only job is to remind the next member of the team to search for {speaker}.""",
            llm_config={"config_list": self.config_list, "cache_seed": None},
        )

        self.external_searcher = AssistantAgent(
            name="External Searcher",
            llm_config={"config_list": self.config_list, "cache_seed": None},
            system_message=f"""Your job is to search the web for relevant information as instructed by the supervisor. 
            Keep your searches relevant to the speaker profiles provided by the supervisor. 
            Make multiple searches if necessary. 
        """,
        )
        
        self.external_searcher.register_for_llm(name="search_and_crawl", description="A web searcher")(search_and_crawl_autogen)
        self.user_proxy.register_for_execution(name="search_and_crawl")(search_and_crawl_autogen)

        self.supervisor = AssistantAgent(
            name="Supervisor",
            llm_config={"config_list": self.config_list, "cache_seed": None},
            system_message=f"""Do not generate a profile. Your only job is to remind the next agent to search for {speaker}. 
            Respond with 'Please search for {speaker}'""",
        )

        self.internal_searcher = AssistantAgent(
            name="Internal Searcher",
            llm_config={"config_list": self.config_list, "cache_seed": None},
            system_message=f"""Internal Searcher. Do not generate a profile. 
                Your only job is to perform a internal search for relevant information about {speaker}. 
                You are equipped with the internal search tool which searches the internal database for information. 
                You are to respond with a tool call using the internal search tool to search for {speaker}. 
        """,
        )
        
        self.internal_searcher.register_for_llm(name="internal_search", description="Searches the internal database for information")(internal_search_autogen)
        self.user_proxy.register_for_execution(name="internal_search")(internal_search_autogen)

        self.writer = AssistantAgent(
            name="Writer",
            llm_config={"config_list": self.config_list, "cache_seed": None},
            system_message="""Writer. Your only job is to write the speaker profile in text based on the information provided by tool calls. 
            If the information is prefaced by EXTERNAL SEARCH, preface your profile with the headline "EXTERNAL SEARCH"
            If the information is prefaced by INTERNAL SEARCH, preface your profile with the headline "INTERNAL SEARCH"
            If there is insufficient information, add a disclaimer for "Extra Context Needed", and list the pieces of information which are missing. 
            """,
        )

        self.summariser = AssistantAgent(
            name="Summariser",
            llm_config={"config_list": self.config_list, "cache_seed": None},
            system_message=f"""Summariser. Your job is to summarise the profiles generated by the writer into a single report.
            You must preface your output with "PROFILE SUMMARY: {speaker}". 
            """,
        )
      
        self.ordering = [self.orchestrator,
                    self.external_searcher,
                    self.user_proxy,
                    self.writer,             # Summarise online information
                    self.supervisor,         # Remind the next member of the team to search for {speaker}
                    self.internal_searcher,  # Offline search
                    self.user_proxy,
                    self.writer,             # Summarise offline information
                    self.summariser,]        # Summarise both
        
        def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
            """Define a customized speaker selection function.
            A recommended way is to define a transition for each speaker in the groupchat.

            Returns:
                Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
            """
            
            messages = groupchat.messages
            poster = MessagePoster()
            
            if messages != []:
                poster.post_internal_message(messages[-1],mode='autogen')
                if last_speaker is self.writer:
                    poster.post_message(messages[-1]['content'].replace("**","*"),mode='s')
            
            if len(messages) == 4:
                poster.post_message("PROFILE GENERATED BY EXTERNAL SEARCH:",mode='s')
            if len(messages) == 8:
                poster.post_message("PROFILE GENERATED BY INTERNAL SEARCH:",mode='s')

            if len(messages) <= len(self.ordering):
                return self.ordering[len(messages)-1]
            else:
                return self.user_proxy

        self.groupchat = GroupChat(
            agents = [self.user_proxy, self.orchestrator, self.writer, self.external_searcher, self.internal_searcher, self.supervisor, self.summariser],
            messages = [],
            max_round = len(self.ordering)+1,
            speaker_selection_method = custom_speaker_selection_func,
        )
        self.manager = GroupChatManager(groupchat = self.groupchat, llm_config = {"config_list": self.config_list, "cache_seed": None})

    def start(self):
        try:
            with Cache.disk(cache_seed=54) as cache:
                groupchat_history_custom = self.user_proxy.initiate_chat(
                    self.manager,
                    message = self.task,
                    cache = cache,
                )
            
                return groupchat_history_custom
        except EOFError as e:
            print("EOFError")
            return
        
agent = ProfileGeneratorAgent("Dario Amodei")
agent.start()