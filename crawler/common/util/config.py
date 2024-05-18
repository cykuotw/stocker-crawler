import os

from dotenv import load_dotenv

load_dotenv()


def getStockerConfig():
    """
    Get Stocker Server Config
    """
    return {
        'STOCKER_URL': os.environ.get("SERVER_API_URL")
    }


def getChatbotInfo():
    """
    Get Chatbot Config
    """
    return {
        "telegram-message-url": os.environ.get("TELEGRAM_MESSAGE_URL"),
        "telegram-chat-id": os.environ.get("TELEGRAM_CHAT_ID"),

        "slack": os.environ.get("SLACK_HOOK"),

        'discord-logbot': os.environ.get("DISCORD_LOGBOT_HOOK"),
        'discord-criticalinfobot': os.environ.get("DISCORD_CRITICALiNFOBOT_HOOK"),
        'discord-concallbot': os.environ.get('DISCORD_CONCALLBOT_HOOK'),
        'discord-volatilitybot': os.environ.get('DISCORD_VOLATILITY_HOOK'),
    }


def getWebhookConfig():
    """
    Get Webhook Config
    """
    return {
        'slack': os.environ.get("SLACK_HOOK"),
        'stocker': os.environ.get("STOCKER_HOOK"),
        'gugugu': os.environ.get("GUGUGU_HOOK")
    }


def getYahooConfig():
    """
    Get Yahoo Config
    """
    return {
        'total-slices': int(os.environ.get("YAHOO_TOTAL_SLICE", "1")),
        'current-slices': int(os.environ.get("YAHOO_CURRENT_SLICE", "5")),
    }
