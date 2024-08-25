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

speaker = "Dario Amodei"

task = "Generate a speaker profile for " + speaker

config_list = [
        {
            "model": "mistral-16K:latest", 
            "api_key": "ollama", 
            "base_url": "http://localhost:11434/v1", 
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

supervisor = AssistantAgent(
    name="Supervisor",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message=f"""Do not generate a profile. Your only job is to remind the next agent to search for {speaker}. """,
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

writer = AssistantAgent(
    name="Writer",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message="""Writer. Your only job is to write the speaker profile in text based on the information provided by tool calls. 
    If the information is prefaced by EXTERNAL SEARCH, preface your profile with the headline "EXTERNAL SEARCH". 
    If the information is prefaced by INTERNAL SEARCH, preface your profile with the headline "INTERNAL SEARCH". 
    You must generate a complete profile. 
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

post_internal_message("LOG STARTING FOR profile_generator.py...",mode='direct')
post_message("STARTING WORKFLOW...",mode='direct')
post_message("PROMPT: "+task, mode='direct')
ordering = [orchestrator,
            external_searcher,
            user_proxy,
            writer,             # Summarise online information
            supervisor,         # Remind the next member of the team to search for {speaker}
            internal_searcher,  # Offline search
            user_proxy,
            writer,             # Summarise offline information
            summariser,]        # Summarise both

def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
    """Define a customized speaker selection function.
    A recommended way is to define a transition for each speaker in the groupchat.

    Returns:
        Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
    """
    messages = groupchat.messages
    if messages != []:
        post_internal_message(messages[-1])
        if last_speaker is writer:
            post_message(messages[-1]['content'].replace("**","*"),mode='s')
        elif last_speaker is summariser:
            post_message(messages[-1]['content'].replace("**","*"),mode='s')
    
    if len(messages) == 4:
        post_message("PROFILE GENERATED BY EXTERNAL SEARCH:",mode='s')
    if len(messages) == 8:
        post_message("PROFILE GENERATED BY INTERNAL SEARCH:",mode='s')

    if len(messages) <= len(ordering):
        return ordering[len(messages)-1]
    else:
        return user_proxy

groupchat = GroupChat(
    agents=[user_proxy, writer, external_searcher, orchestrator, supervisor, internal_searcher, summariser],
    messages=[],
    max_round=len(ordering)+1,
    speaker_selection_method=custom_speaker_selection_func,
)
manager = GroupChatManager(groupchat=groupchat, 
                           llm_config={"config_list": config_list, "cache_seed": None},
                           is_termination_msg=lambda msg: "TERMINATE" in msg["content"])

# Keep 54 with mistral-16K, executed from idsc_demo as the demo
with Cache.disk(cache_seed=54) as cache:
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