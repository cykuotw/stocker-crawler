from datetime import datetime

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

    slack.push(
        "Stocker每日新聞",
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} {message}")
    discord.pushLog(
        "Stocker每日新聞",
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} {message}")
