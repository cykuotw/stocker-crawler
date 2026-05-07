import json

import requests

from crawler.common.util.config import getChatbotInfo


def push(username: str, content: str) -> None:
    config = getChatbotInfo()
    requests.post(
        url=config["slack"],
        data=json.dumps({
            "username": username,
            "text": content
        }),
        headers={"content-type": "application/json"},
        timeout=10
    )
