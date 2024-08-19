import requests
from typing_extensions import Annotated
def post_message(message:Annotated[str, "message to be posted"]):
    url = 'https://hooks.slack.com/services/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'
    myobj = {
        "text": message
    }
    requests.post(url, json = myobj)

def post_internal_message(message,sender="Agent"):
    url = "https://hooks.slack.com/services/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"
    try:
        sender = message['name'].upper()
        content = message['content']
    except:
        pass
    myobj = {
        "text": sender + ": \n" + str(content)
    }
    requests.post(url, json = myobj)