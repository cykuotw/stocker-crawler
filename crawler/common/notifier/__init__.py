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
    # slack.push(
    #     "Stocker每日新聞",
    #     f"{datetime.now(tw).strftime('%m/%d/%Y, %H:%M:%S')} {message}")
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
    # slack.push(
    #     "Stocker每日重訊",
    #     f"{datetime.now(tw).strftime('%m/%d/%Y, %H:%M:%S')} {message}")
    discord.pushLog(
        "Stocker每日重訊",
        f"{datetime.now(tw).strftime('%m/%d/%Y, %H:%M:%S')} {message}")


def _formatErrorDetail(detail):
    if not isinstance(detail, dict):
        return f"\t{detail}"

    lines = []
    first_line = []
    if 'stock' in detail:
        first_line.append(str(detail['stock']))
    if 'status' in detail:
        first_line.append(f"status={detail['status']}")
    if first_line:
        first_line = "\t".join(first_line)
        lines.append(f"\t{first_line}")

    if 'title' in detail:
        lines.append(f"\ttitle={detail['title']}")
    if 'message' in detail:
        lines.append(f"\tfailmsg={detail['message']}")

    formatted_keys = {'stock', 'status', 'title', 'message'}
    for key, value in detail.items():
        if key not in formatted_keys:
            lines.append(f"\t{key}={value}")

    return "\n".join(lines)


def pushErrorMessage(message: str = "", crawler: str = "crawler", details=None):
    """
    Push error messages
    """
    if message == "" and not details:
        return

    content = message
    if details:
        content = f"{message}: {len(details)} item(s)"
        for detail in details:
            content += f"\n{_formatErrorDetail(detail)}"

    tw = pytz.timezone('Asia/Taipei')
    discord.pushError(
        f"Stocker錯誤通知 - {crawler}",
        f"{datetime.now(tw).strftime('%m/%d/%Y, %H:%M:%S')} "
        f"[{crawler}] {content}")
