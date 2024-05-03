import json

import requests

from crawler.common.util.config import CHAT_BOT_INFO


def pushLog(username: str, content: str) -> None:
    """
    Push logs
    """
    requests.post(
        url=CHAT_BOT_INFO["discord-logbot"],
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
    requests.post(
        url=CHAT_BOT_INFO["discord-criticalinfobot"],
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
    requests.post(
        url=CHAT_BOT_INFO["discord-concallbot"],
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
    requests.post(
        url=CHAT_BOT_INFO["discord-volatilitybot"],
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"},
        timeout=10
    )
