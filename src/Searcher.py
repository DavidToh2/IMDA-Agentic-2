import http.client
import json
import os

def search(query,urls=3):
    """
    returns a list of urls produced by serper.dev on google search
    """
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": query,
        "gl": "sg"
    })
    headers = {
        'X-API-KEY': os.environ['SERPER_DEV_API_KEY'],
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data.decode("utf-8"))
    
    return [res["link"] for res in data["organic"][0:urls]]
    





