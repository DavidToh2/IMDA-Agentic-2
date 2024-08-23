import requests
from typing_extensions import Annotated
import os
def post_message(message:Annotated[str, "message to be posted"],mode='groupchat'):
    url = os.environ.get('URL_OUTPUT')
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
    url = os.environ.get('URL_LOG')
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