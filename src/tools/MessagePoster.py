
import requests
from typing_extensions import Annotated
from langchain_core.messages import AnyMessage

class MessagePoster:
    def __init__(self):
        self.URL_OUTPUT = 'https://hooks.slack.com/services/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'
        self.URL_LOG = "https://hooks.slack.com/services/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"

    def post_message(self, message : AnyMessage, mode='groupchat'):

        if mode == "groupchat":
            content = message.content
            myobj = {
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": str(content).replace("**", "*")
                    }
                }]
            }
            requests.post(self.URL_OUTPUT, json = myobj)
        else:
            myobj = {
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }]
            }
            requests.post(self.URL_OUTPUT, json = myobj)
        

    def post_internal_message(self, message : AnyMessage, sender="Agent", mode="groupchat"):

        if mode == "groupchat":
            sender = message.name.upper()
            content = message.content
            myobj = {
            "text": sender + ": \n" + str(content)
            }
            requests.post(self.URL_LOG, json = myobj)
        else:
            myobj = {
            "text": message
            }
            requests.post(self.URL_LOG, json = myobj)

# p = MessagePoster()
# msg="""
# **INTERNAL SEARCH: Speaker Profile – Dario Amodei**
# **1. Basic Information**
# - Full Name: Dario Amodei
# - Position: Co-Founder and CEO at Anthropic (AI Safety and Alignment Research)
# - Contact Details:
#   - Email: dario@anthropic.com (business inquiries)
#   - LinkedIn: linkedin.com/in/darioamodei
#   - Twitter:@DarioAmodei
# **2. Biographical Information**
# - Date & Place of Birth: Unknown
# - Educational Background:
#   - PhD in Computer Science, UC Berkeley? [Extra Context Needed]
#   - Undergraduate/Degree from Caltech and Stanford University? [Extra Context Needed]
# **3. Area of Expertise**
# - AI Safety and Alignment Research
# - Large Language Models (LLMs)
# - Current Projects:
#   - Leading Anthropic in developing safer, more aligned LLMs through research collaborations with AI experts worldwide.
# **4. Speaking Style & Experience**
# - Presentation style: Informative and engaging; Dario emphasizes the importance of responsible AI development.
# - Previous Speaking Experience:
#   - Panelist or Speaker at various AI conferences (e.g., NeurIPS, EMNLP) on topics related to AI safety and alignment.
# - **Extra Context Needed**: More details on speaking experiences would help refine this section.
# **5. Preferred Talk Topics**
# - AI Safety and Alignment Research
# - The Importance of Value Alignment in LLMs
# - Current Progress and Challenges at Anthropic
# **6. Language Fluency**
# - Primary language for presentations: English
# """
# p.post_message("PROFILE GENERATED FROM INTERNAL SEARCH:", mode="debug")
# p.post_message(msg.replace("**","*"), mode="debug")