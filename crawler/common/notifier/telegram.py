import json

import requests

from crawler.common.util.config import getChatbotInfo


def push(content: str) -> None:
    config = getChatbotInfo()
    requests.post(
        url=config["telegram-message-url"],
        data=json.dumps({
            "chat_id": config['telegram-chat-id'],
            "parse_mode": "markdown",
            "text": content
        }),
        headers={"Content-Type": "application/json"},
        timeout=10
    )
