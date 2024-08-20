import requests
from typing_extensions import Annotated
def post_message(message:Annotated[str, "message to be posted"],mode='groupchat'):
    url = 'https://hooks.slack.com/services/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'
    if mode == "groupchat":
        content = message['content']
        myobj = {
        "text": str(content)
        }
        requests.post(url, json = myobj)
    else:
        myobj = {
        "text": message
        }
        requests.post(url, json = myobj)
    

def post_internal_message(message,sender="Agent",mode="groupchat"):
    url = "https://hooks.slack.com/services/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"
    if mode == "groupchat":
        sender = message['name'].upper()
        content = message['content']
        myobj = {
        "text": sender + ": \n" + str(content)
        }
        requests.post(url, json = myobj)
    else:
        myobj = {
        "text": message
        }
        requests.post(url, json = myobj)