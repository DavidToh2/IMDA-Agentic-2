import re
import requests
from typing_extensions import Annotated
from langchain_core.messages import AnyMessage

class MessagePoster:
    def __init__(self):
        self.URL_OUTPUT = 'https://hooks.slack.com/services/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'
        self.URL_LOG = 'https://hooks.slack.com/services/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'

    def post_message(self, message : AnyMessage, mode='groupchat'):

        if mode == "groupchat":
            content = self._format_message(message.content)
            for p in content.split("\n\n"):
                myobj = {
                    "blocks": [{
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": p
                        }
                    }]
                }
                requests.post(self.URL_OUTPUT, json = myobj)
        else:
            for p in self._format_message(message).split("\n\n"):
                myobj = {
                    "blocks": [{
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": p
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

    def _format_message(self, msg_str):
        return str(msg_str).replace("**", "*").replace("–","-")

# p = MessagePoster()

# msg="""
# **INTERNAL INFORMATION PROFILE:**

# Lee Kuan Yew (16 September 1923 - 23 March 2015), often referred to by his initials LKY, was a Singaporean statesman and lawyer who served as the first Prime Minister of Singapore from 1959 to 1990. He is widely recognized for his leadership in transforming Singapore into a modern, developed nation-state.

# An advocate for Asian values and pragmatic governance, Lee's premiership was characterized by authoritarian elements, including restrictions on press freedoms, protests, labor movements, and defamation lawsuits against political opponents. Despite these controversial policies, he maintained that they were necessary for Singapore's stability and progress.

# Lee was born in Singapore during British colonial rule. After graduating from Raffles Institution, he won a scholarship to study at Raffles College (now the National University of Singapore). During the Japanese occupation, Lee avoided being targeted by evading capture while working as an administration service officer for the Japanese propaganda office. Post-war, he briefly attended the London School of Economics before transferring to Fitzwilliam College, Cambridge, where he studied law and was called to the Bar at Middle Temple, London in 1950.

# After returning to Singapore, Lee practiced law and became involved in politics, co-founding the People's Action Party (PAP) in 1954. He served as its Secretary-General until 1992 and held various ministerial portfolios throughout his career. Lee passed away on 23 March 2015 at the age of 91.

# **COMBINED PROFILE:**

# Lee Kuan Yew (16 September 1923 - 23 March 2015), often referred to by his initials LKY, was a Singaporean statesman and lawyer who served as the first Prime Minister of Singapore from 1959 to 1990. He is widely recognized for his leadership in transforming Singapore into a modern, developed nation-state.

# An advocate for Asian values and pragmatic governance, Lee's premiership was characterized by both significant achievements and controversial policies. These include restrictions on press freedoms, protests, labor movements, and defamation lawsuits against political opponents, which he maintained were necessary for Singapore's stability and progress. Despite these measures, Lee is credited with turning Singapore into a global economic powerhouse.

# Lee was born in Singapore during British colonial rule. After graduating from Raffles Institution, he won a scholarship to study at Raffles College (now the National University of Singapore). During the Japanese occupation, Lee avoided being targeted by evading capture while working as an administration service officer for the Japanese propaganda office. Post-war, he briefly attended the London School of Economics before transferring to Fitzwilliam College, Cambridge, where he studied law and was called to the Bar at Middle Temple, London in 1950.

# After returning to Singapore, Lee practiced law and became involved in politics, co-founding the People's Action Party (PAP) in 1954. He served as its Secretary-General until 1992 and held various ministerial portfolios throughout his career, including Minister for Transport, Minister for Finance, Deputy Prime Minister, and Senior Minister. Lee passed away on 23 March 2015 at the age of 91.

# DONE"""

# p.post_message("TEST", mode="debug")
# p.post_message(msg, mode="debug")