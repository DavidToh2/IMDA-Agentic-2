import tempfile
from autogen import GroupChatManager, ConversableAgent, GroupChat, AssistantAgent, UserProxyAgent
from tools.search_and_crawl import search_and_crawl

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
            system_message=f"""Planner. Please determine what information is needed to generate a user profile for Dario Amodei. """,
            llm_config={"config_list": config_list, "cache_seed": None})

user_proxy = UserProxyAgent(
    name="User Proxy",
    system_message="A human admin. Give the task, and send instructions to writer to refine the profile.",
)

writer = AssistantAgent(
    name="Writer",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message="""Writer. Your only job is to write the speaker profile in text based on the information provided by tool calls. 
    If the information is prefaced by EXTERNAL SEARCH, preface your profile with the headline "EXTERNAL SEARCH". 
    If the information is prefaced by INTERNAL SEARCH, preface your profile with the headline "INTERNAL SEARCH". 
    You must generate a complete profile. 
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

external_search_groupchat = GroupChat(agents=[planner,external_searcher,user_proxy,writer],
                                      messages=[],
                                      speaker_selection_method='round_robin'
                                      max_round=4
                                      )

external_groupchat_manager = GroupChatManager(
    groupchat=external_search_groupchat,
    llm_config=config,
)


reply = orchestrator.initiate_chats(
    [
        {"recipient": external_groupchat_manager, "message": "Generate a speaker profile for Dario Amodei", "summary_method": "last_msg"},
    ]
)