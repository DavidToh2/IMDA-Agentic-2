import os

from autogen import ConversableAgent, UserProxyAgent

config_list = [
        {
            "model": "mistral-16K:latest", 
            "api_key": "ollama", 
            "base_url": "http://localhost:11434/v1", 
        }
    ]


student_agent = UserProxyAgent(
    name="Student_Agent",
    system_message="You are a student willing to learn.",
    code_execution_config={"use_docker": False}

)
teacher_agent = ConversableAgent(
    name="Teacher_Agent",
    system_message="You are a math teacher.",
    llm_config={"config_list": config_list},
    code_execution_config={"use_docker": False},
)

chat_result = teacher_agent.initiate_chat(
    student_agent,
    message="Ask me any question about mathematics.",
    summary_method="reflection_with_llm",
    max_turns=3,
)