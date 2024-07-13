import json

import requests

from crawler.common.util.config import getChatbotInfo


def pushLog(username: str, content: str) -> None:
    """
    Push logs
    """
    config = getChatbotInfo()
    requests.post(
        url=config["discord-logbot"],
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"},
        timeout=10
    )


def pushInfo(username: str, content: str) -> None:
    """
    Push critical information
    """
    config = getChatbotInfo()
    requests.post(
        url=config["discord-criticalinfobot"],
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"},
        timeout=10
    )


def pushConCallInfo(username: str, content: str) -> None:
    """
    Push conference call information
    """
    config = getChatbotInfo()
    requests.post(
        url=config["discord-concallbot"],
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"},
        timeout=10
    )


def pushVolatility(username: str, content: str) -> None:
    """
    Push volatility information
    """
    config = getChatbotInfo()
    requests.post(
        url=config["discord-volatilitybot"],
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"},
        timeout=10
    )
