from datetime import datetime
from autogen import (
    Agent,
    AssistantAgent,
    GroupChat,
    GroupChatManager,
    UserProxyAgent,
)
from autogen.cache import Cache
from autogen.coding import LocalCommandLineCodeExecutor

task = (
    f"Today is {datetime.now().date()}. Write a blogpost about the stock price performance of Nvidia in the past month."
)

config_list= [
        {
            "model": "mistral-nemo:latest", # Loaded with LiteLLM command
            "api_key": "ollama", # Not needed
            "base_url": "http://localhost:11434/v1"  # Your LiteLLM URL
        }
    ]

user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin. Give the task, and send instructions to writer to refine the blog post.",
    code_execution_config=False,
)

planner = AssistantAgent(
    name="Planner",
    system_message="""Planner. Given a task, please determine what information is needed to complete the task.
Please note that the information will all be retrieved using Python code. Please only suggest information that can be retrieved using Python code.
""",
    llm_config={"config_list": config_list, "cache_seed": None},
)

engineer = AssistantAgent(
    name="Engineer",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message="""Engineer. You write python/bash to retrieve relevant information. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
Your response should only contain a block of code and nothing else. Include print statements in your code to display results on the terminal. 
""",
)

writer = AssistantAgent(
    name="Writer",
    llm_config={"config_list": config_list, "cache_seed": None},
    system_message="""Writer. Please write blogs in markdown format (with relevant titles) and put the content in pseudo ```md``` code block. You will write it for a task based on previous chat history. """,
)

code_executor = UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="ALWAYS",
    code_execution_config={
        "last_n_messages": 3,
        #Run code in docker for safety
        "executor": LocalCommandLineCodeExecutor(),
        #executor": DockerCommandLineCodeExecutor(image='python-yf'),
    },
)


def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
    """Define a customized speaker selection function.
    A recommended way is to define a transition for each speaker in the groupchat.

    Returns:
        Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
    """
    messages = groupchat.messages

    if len(messages) <= 1:
        # first, let the engineer retrieve relevant data
        return planner

    if last_speaker is planner:
        # if the last message is from planner, let the engineer to write code
        return engineer
    elif last_speaker is user_proxy:
        if messages[-1]["content"].strip() != "":
            # If the last message is from user and is not empty, let the writer to continue
            return writer

    elif last_speaker is engineer:
        if "```python" in messages[-1]["content"]:
            # If the last message is a python code block, let the executor to speak
            return code_executor
        else:
            # Otherwise, let the engineer to continue
            return engineer

    elif last_speaker is code_executor:
        if "exitcode: 1" in messages[-1]["content"]:
            # If the last message indicates an error, let the engineer to improve the code
            return engineer
        else:
            # Otherwise, let the writer to speak
            return writer

    elif last_speaker is writer:
        # Always let the user to speak after the writer
        return user_proxy

    else:
        # default to auto speaker selection method
        return "auto"


groupchat = GroupChat(
    agents=[user_proxy, engineer, writer, code_executor, planner],
    messages=[],
    max_round=20,
    speaker_selection_method=custom_speaker_selection_func,
)
manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list, "cache_seed": None})

with Cache.disk(cache_seed=41) as cache:
    groupchat_history_custom = user_proxy.initiate_chat(
        manager,
        message=task,
    )