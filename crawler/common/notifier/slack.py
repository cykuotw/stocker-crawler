import json

import requests

from crawler.common.util.config import CHAT_BOT_INFO


def push(username: str, content: str) -> None:
    requests.post(
        url=CHAT_BOT_INFO["slack"],
        data=json.dumps({
            "username": username,
            "text": content
        }),
        headers={"content-type": "application/json"},
        timeout=10
    )
