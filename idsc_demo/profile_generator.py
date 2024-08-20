import autogen
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
from tools.internal_search import internal_search
from tools.search_and_crawl import search_and_crawl
from tools.internal_search import internal_search

from tools.post_message import post_message
from tools.post_message import post_internal_message

speaker = "Hu Heng Hua"


with open('atx_plenary.txt', 'r') as file:
    memo = file.read()


task = "Generate a speaker profile for " + speaker

config_list = [
        {
            "model": "mistral-nemo:latest", 
            "api_key": "ollama", 
            "base_url": "http://localhost:11434/v1", 
            "temperature":0.0
        }
    ]

user_proxy = UserProxyAgent(
    name="User Proxy",
    system_message="A human admin. Give the task, and send instructions to writer to refine the profile.",
    code_execution_config=False,
)

orchestrator = AssistantAgent(
    name="Orchestrator",
    system_message=f"""Orchestrator. Please determine what information is needed to {task}. """,
    llm_config={"config_list": config_list, "cache_seed": None},
)

supervisor = AssistantAgent(
    name = "Supervisor",
    system_message=f"""Supervisor. Ignore the group manager. Your only job is to remind the next member of the team to search for {speaker}.""",
    llm_config={"config_list": config_list, "cache_seed": None},
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

internal_searcher = AssistantAgent(
    name="Internal Searcher",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message=f"""Your only job is to search the internal database for relevant information
    based on what is required by the supervisor. You are only allowed to call the internal_search tool.
    Your searches must be in plaintext without any special characters. 
    Perform multiple searches if necessary.
""",
)
internal_searcher.register_for_llm(name="internal_search", description="Searches the internal database for information")(internal_search)
user_proxy.register_for_execution(name="internal_search")(internal_search)

writer = AssistantAgent(
    name="Writer",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message="""Writer. Write the speaker profile in text based on the information provided by tool calls. 
    If the information is prefaced by INTERNAL SEARCH, preface your profile with the headline "INTERNAL SEARCH"
    If the information is prefaced by EXTERNAL SEARCH, preface your profile with the headline "EXTERNAL SEARCH"
    If there is insufficient information, add a disclaimer for "Extra Context Needed", and list the pieces of information which are missing. 
    """,
)

summariser = AssistantAgent(
    name="Summariser",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message=f"""Summariser. Your job is to summarise the profiles generated by the writer into a single report.
    You must preface your output with "PROFILE SUMMARY: {speaker}". 
    """,
)

post_internal_message("LOG STARTING...",mode='direct')
post_message("STARTING WORKFLOW...",mode='direct')
post_message("PROMPT: "+task, mode='direct')
ordering = [orchestrator,
            supervisor,
            external_searcher,
            user_proxy,
            writer,
            supervisor,
            internal_searcher,
            user_proxy,
            writer,        
            summariser,]

def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
    """Define a customized speaker selection function.
    A recommended way is to define a transition for each speaker in the groupchat.

    Returns:
        Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
    """
    messages = groupchat.messages
    if messages != []:
        post_internal_message(messages[-1])
        if last_speaker is writer or last_speaker is summariser:
            post_message(messages[-1])
        elif last_speaker is summariser:
            post_message(messages[-1])
        
    if len(messages) <= len(ordering):
        return ordering[len(messages)-1]


    elif last_speaker is orchestrator:
        # if the last message is from planner, let the crawler search
        return external_searcher
    
    elif last_speaker is user_proxy:
        if messages[-1]["content"].strip() != "" and messages[-1]["content"].strip()[0] == "#" :
            # If the last message is the result of a tool call from user and is not empty, let the writer continue
            return writer
        else: 
            return orchestrator     

    elif last_speaker is external_searcher:
        return user_proxy

    elif last_speaker is writer:
        # Always let the user to speak after the writer
        return internal_searcher

    else:
        # default to auto speaker selection method
        return "auto"


groupchat = GroupChat(
    agents=[user_proxy, writer, external_searcher, orchestrator, supervisor, internal_searcher, summariser],
    messages=[],
    max_round=len(ordering)+1,
    speaker_selection_method=custom_speaker_selection_func,
)
manager = GroupChatManager(groupchat=groupchat, 
                           llm_config={"config_list": config_list, "cache_seed": None},
                           is_termination_msg=lambda msg: "TERMINATE" in msg["content"])

with Cache.disk(cache_seed=42) as cache:
    groupchat_history_custom = user_proxy.initiate_chat(
        manager,
        message=task,
        cache=cache,
    )

post_message("END OF WORKFLOW",mode='literal')
post_internal_message("END OF WORKFLOW",mode="literal")
# user_proxy.initiate_chat(
#         manager,
#         message=task)