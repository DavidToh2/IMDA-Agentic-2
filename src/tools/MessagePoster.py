
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
            "text": str(content)
            }
            requests.post(self.URL_OUTPUT, json = myobj)
        else:
            myobj = {
            "text": message
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