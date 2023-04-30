import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
chatbotInfo = {
    'discord-logbot': os.environ.get("discord-logbot-hook"),
    'discord-criticalinfobot': os.environ.get("discord-criticalinfobot-hook")
}


def pushDiscordLog(username: str, content: str) -> None:
    requests.post(
        url=chatbotInfo["discord-logbot"],
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"}
    )


def pushDiscordInfo(username: str, content: str) -> None:
    requests.post(
        url=chatbotInfo["discord-criticalinfobot"],
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"}
    )
