from autogen import GroupChatManager, ConversableAgent, GroupChat, AssistantAgent, UserProxyAgent
from tools.search_and_crawl import search_and_crawl
from tools.internal_search import internal_search

speaker = "Dario Amodei"

config_list = [
        {
            "model": "mistral-16K:latest", 
            "api_key": "ollama", 
            "base_url": "http://localhost:11434/v1", 
        }
    ]
config = {"config_list":config_list}

orchestrator = ConversableAgent(
    name='Orchestrator',                         
    llm_config=False,
    human_input_mode="ALWAYS",

    )


planner = AssistantAgent(
            name="Planner",
            system_message=f"""Planner. Please determine what information is needed to generate a user profile for {speaker}. """,
            llm_config={"config_list": config_list, "cache_seed": None})
user_proxy = UserProxyAgent(
    name="User Proxy",
    system_message="A human admin. Executes the search tool calls.",
)
ConversableAgent()
external_writer = AssistantAgent(
    name="External Writer",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message="""Writer. Your only job is to write the speaker profile in text based on the information provided by tool calls. 
    If there is insufficient information, return "EXTRA CONTEXT NEEDED", and list the pieces of information which are missing. 
    """,
)
external_searcher = AssistantAgent(
            name="External Searcher",
            llm_config={"config_list": config_list, "cache_seed": None},
            system_message=f"""Your job is to search the web for relevant information as instructed by the supervisor. 
            Keep your searches relevant to the speaker profiles provided by the supervisor. 
            Make multiple searches if necessary. 
        """,
        )     
external_searcher.register_for_llm(name="search_and_crawl", description="A web searcher")(search_and_crawl)
user_proxy.register_for_execution(name="search_and_crawl")(search_and_crawl)
external_search_groupchat = GroupChat(agents=[planner,external_searcher,user_proxy,external_writer],
                                      messages=[],
                                      speaker_selection_method='round_robin',
                                      max_round=5
                                      )
external_groupchat_manager = GroupChatManager(
    groupchat=external_search_groupchat,
    llm_config=config,
)

internal_writer = AssistantAgent(
    name="Internal Writer",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message=f"""Writer. Your only job is to synthesise the information provided by the internal_search tool call. 
    Write a report based only on the internal information found about {speaker}. Do not assume anything else about {speaker} other than the information you are provided by the internal search. 
    """,
)
internal_searcher = AssistantAgent(
    name="Internal Searcher",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message=f"""Internal Searcher. Do not generate a profile. 
        Your only job is to perform a internal search for relevant information about {speaker}. 
        You are equipped with the internal search tool which searches the internal database for information. 
        You must use the internal search tool to search for {speaker}. 
""",
)
internal_searcher.register_for_llm(name="internal_search", description="Searches the internal database for information")(internal_search)
user_proxy.register_for_execution(name="internal_search")(internal_search)
internal_search_groupchat = GroupChat(agents=[internal_searcher,user_proxy,internal_writer],
                                      messages=[],
                                      speaker_selection_method='round_robin',
                                      max_round=4
                                      )
internal_groupchat_manager = GroupChatManager(
    groupchat=internal_search_groupchat,
    llm_config=config,
)

reply = orchestrator.initiate_chats(
    [
        {"recipient": external_groupchat_manager,"message": f"Generate a speaker profile for {speaker}", "summary_method": "last_msg"},
        {"recipient": internal_groupchat_manager,"message": "", "summary_method": "last_msg"}
    ]
)