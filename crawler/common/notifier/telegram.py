import json

import requests

from crawler.common.util.config import CHAT_BOT_INFO


def push(content: str) -> None:
    requests.post(
        url=CHAT_BOT_INFO["telegram-message-url"],
        data=json.dumps({
            "chat_id": CHAT_BOT_INFO['telegram-chat-id'],
            "parse_mode": "markdown",
            "text": content
        }),
        headers={"Content-Type": "application/json"},
        timeout=10
    )
