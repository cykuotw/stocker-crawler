import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
chatbotInfo = {
    'discord-logbot': os.environ.get("discord-logbot-hook"),
    'discord-criticalinfobot': os.environ.get("discord-criticalinfobot-hook"),
    'discord-concallbot': os.environ.get('discord-concallbot-hook'),
    'discord-volatilitybot':os.environ.get('discrod-volatility-hook')
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


def pushDiscordConCallInfo(username: str, content: str) -> None:
    requests.post(
        url=chatbotInfo["discord-concallbot"],
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"}
    )

def pushDiscordVolatility(username: str, content: str) -> None:
    requests.post(
        url=chatbotInfo["discord-volatilitybot"],
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"}
    )