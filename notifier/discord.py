import json
import os
import re
import pytz
from datetime import datetime

import requests
from dotenv import load_dotenv

HOST = os.environ.get("host-url")
chatbotInfo = {
    'discord-logbot': os.environ.get("discord-logbot-hook")
}


def pushDiscordLog(username: str, content: str) -> None:
    requests.post(
        url="https://discord.com/api/webhooks/1100574481656856636/31AW8hMnZRC27TFD2OD-VZ_ltNkFkYaCFiVfwC8D9LdTVgJayTZmahbODNXQUexoLGgn",
        data=json.dumps({
            "username": username,
            "content": content
        }),
        headers={"content-type": "application/json"}
    )
