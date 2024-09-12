from datetime import datetime

import pytz

from crawler.common.notifier import discord, slack


def pushNewsMessge(message: str = ""):
    """
    @Description:
        推送log\n
        push log messges\n
    @Param:
        message => str (default: "")
    @Return:
        N/A
    """
    if message == "":
        return

    tw = pytz.timezone('Asia/Taipei')
    slack.push(
        "Stocker每日新聞",
        f"{datetime.now(tw).strftime('%m/%d/%Y, %H:%M:%S')} {message}")
    discord.pushLog(
        "Stocker每日新聞",
        f"{datetime.now(tw).strftime('%m/%d/%Y, %H:%M:%S')} {message}")


def pushCriticalInfoMessage(message: str = ""):
    """
    @Description:
        推送log\n
        push log messges\n
    @Param:
        message => str (default: "")
    @Return:
        N/A
    """
    if message == "":
        return

    tw = pytz.timezone('Asia/Taipei')
    slack.push(
        "Stocker每日重訊",
        f"{datetime.now(tw).strftime('%m/%d/%Y, %H:%M:%S')} {message}")
    discord.pushLog(
        "Stocker每日重訊",
        f"{datetime.now(tw).strftime('%m/%d/%Y, %H:%M:%S')} {message}")
