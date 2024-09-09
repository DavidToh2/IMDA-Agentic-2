from autogen import GroupChatManager, ConversableAgent, GroupChat, AssistantAgent, UserProxyAgent
from tools.WebSearcher import search_and_crawl_autogen
from chroma.ChromaDatabase import internal_search_autogen

class AutogenSeqChatAgent: 
    def __init__(self,speaker):
        config_list = [
        {
            "model": "mistral-32K:latest", 
            "api_key": "ollama", 
            "base_url": "http://localhost:11434/v1", 
        }
    ]
        self.speaker = speaker
        self.config = {"config_list":config_list}

        self.orchestrator = ConversableAgent(
            name='Orchestrator',                         
            llm_config=False,
            human_input_mode="ALWAYS",

            )
        self.planner = AssistantAgent(
                    name="Planner",
                    system_message=f"""Planner. Please determine what information is needed to generate a user profile for {speaker}. """,
                    llm_config={"config_list": config_list, "cache_seed": None}
        )
        self.user_proxy = UserProxyAgent(
            name="User Proxy",
            system_message="A human admin. Executes the search tool calls.",
        )
        self.external_writer = AssistantAgent(
            name="External Writer",
            llm_config={"config_list": config_list, "cache_seed": None},
            system_message="""Writer. Your only job is to write the speaker profile in text based on the information provided by tool calls. 
            If there is insufficient information, return "EXTRA CONTEXT NEEDED", and list the pieces of information which are missing. 
            """,
        )
        self.external_searcher = AssistantAgent(
                    name="External Searcher",
                    llm_config={"config_list": config_list, "cache_seed": None},
                    system_message=f"""Your job is to search the web for relevant information using search_and_crawl.
                    Keep your searches relevant to generating a speaker profile for {self.speaker}. 
                    Use search_and_crawl multiple times if necessary. 
                """,
                )     
        self.external_searcher.register_for_llm(name="search_and_crawl", description="A web searcher")(search_and_crawl_autogen)
        self.user_proxy.register_for_execution(name="search_and_crawl")(search_and_crawl_autogen)
        external_search_groupchat = GroupChat(agents=[self.planner,self.external_searcher,self.user_proxy,self.external_writer],
                                            messages=[],
                                            speaker_selection_method='round_robin',
                                            max_round=5
                                            )
        self.external_groupchat_manager = GroupChatManager(
            groupchat=external_search_groupchat,
            llm_config=self.config,
        )

        self.internal_writer = AssistantAgent(
            name="Internal Writer",
            llm_config={"config_list": config_list, "cache_seed": None},
            system_message=f"""Writer. Your only job is to synthesise the information provided by the internal_search tool call. 
            Write a report based only on the internal information found about {speaker}. Do not assume anything else about {speaker} other than the information you are provided by the internal search. 
            """,
        )
        self.internal_searcher = AssistantAgent(
            name="Internal Searcher",
            llm_config={"config_list": config_list, "cache_seed": None},
            system_message=f"""Internal Searcher. Do not generate a profile. 
                Your only job is to perform a internal search for relevant information about {speaker}. 
                You are equipped with the internal search tool which searches the internal database for information. 
                You must use the internal search tool to search for {speaker}. 
        """,
        )
        self.internal_searcher.register_for_llm(name="internal_search", description="Searches the internal database for information")(internal_search_autogen)
        self.user_proxy.register_for_execution(name="internal_search")(internal_search_autogen)
        internal_search_groupchat = GroupChat(agents=[self.internal_searcher,self.user_proxy,self.internal_writer],
                                            messages=[],
                                            speaker_selection_method='round_robin',
                                            max_round=4
                                            )
        self.internal_groupchat_manager = GroupChatManager(
            groupchat=internal_search_groupchat,
            llm_config=self.config,
        )
    
    def start(self):
        reply = self.orchestrator.initiate_chats(
            [
                {"recipient": self.external_groupchat_manager,"message": f"Generate a speaker profile for {self.speaker}", "summary_method": "last_msg"},
                {"recipient": self.internal_groupchat_manager,"message": "", "summary_method": "last_msg"}
            ]
        )

        return reply