import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

chatbotInfo = {
    "telegram-message-url": os.environ.get("telegram-message-url"),
    "telegram-chat-id": os.environ.get("telegram-chat-id"),
    "slack": os.environ.get("slack-hook")
}

def pushSlackMessage(username: str, content: str) -> None:
    requests.post(
        url=chatbotInfo["slack"],
        data=json.dumps({
            "username": username,
            "text": content
        }),
        headers={"content-type": "application/json"})

def pushTelegramMessage(content: str) -> None:
    requests.post(
        url=chatbotInfo["telegram-message-url"],
        data=json.dumps({
            "chat_id": chatbotInfo['telegram-chat-id'],
            "parse_mode": "markdown",
            "text": content
        }),
        headers={"Content-Type": "application/json"}
    )
