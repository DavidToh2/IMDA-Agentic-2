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

#post_message("Hello DTO!", mode='d')
#post_internal_message("My first log",mode='f')