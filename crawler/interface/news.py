import json
import random
import time
from datetime import datetime

import requests

from crawler.core.news import crawlNewsCnyes, crawlNewsUdn, crawlNewsYahoo
from crawler.interface.basicInfo import getStockNoBasicInfo
from crawler.interface.util import stockerUrl
from notifier.discord import pushDiscordLog
from notifier.util import pushSlackMessage


def updateDailyNewsYahoo():
    """
    @Description:
        更新每日Yahoo的新聞\n
        Update all daily news related to tw stock market
        from yahoo to stocker server\n
    @Param:
        N/A
    @Return:
        N/A
    """
    pushLog("Stocker每日新聞 Yahoo", "crawler work start")

    try:
        # Get Yahoo News
        idList = getStockNoBasicInfo()
        for _, stockId in enumerate(idList):
            data = crawlNewsYahoo(str(stockId))
            updateNewsToServer(data)
    except Exception as ex:
        pushLog("Stocker每日新聞 Yahoo", f"Yahoo crawler work error: {ex}")

    pushLog("Stocker每日新聞 Yahoo", "crawler work done")


def updateDailyNews(datetimeIn: datetime = datetime.today()):
    """
    @Description:
        更新每日鉅亨網/工商日報/經濟日報/Yahoo的所有新聞\n
        Update all daily news related to tw stock market
        from cnyes/ctee/udn/yahoo to stocker server\n
    @Param:
        datetimeIn => datetime.datetime (default: today)
    @Return:
        N/A
    """

    data = []

    pushLog("Stocker每日新聞", "crawler work start")

    try:
        # Get CNYES News
        marketList = ["tw", "us"]

        for market in marketList:
            tmp = crawlNewsCnyes(datetimeIn, market)
            for index in range(int(tmp['data_count'])):
                if tmp['data'][index] not in data:
                    data.append(tmp['data'][index])
    except Exception as ex:
        pushLog("Stocker每日新聞", f"CNYES crawler work error: {ex}")

    try:
        # Get Udn News
        newsList = ["stock/head", "stock/sii", "stock/otc",
                    "ind/head", "int/head"]
        for news in newsList:
            tmp = crawlNewsUdn(news)
            for index in range(int(tmp['data_count'])):
                if tmp['data'][index] not in data:
                    data.append(tmp['data'][index])
    except Exception as ex:
        pushLog("Stocker每日新聞", f"UDN crawler work error: {ex}")

    updateNewsToServer(data)
    pushLog("Stocker每日新聞", "crawler work done")


def pushLog(title: str = "Stocker每日新聞", msg: str = "") -> None:
    """
    @Description:
        推送Log訊息\n
        Push log message\n
    @Param:
        title: str, title of the message (default: "Stocker每日新聞")
        msg: str, message content (default: "")
    @Return:
        N/A
    """
    pushSlackMessage(
        title, f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} {msg}")
    pushDiscordLog(
        title, f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} {msg}")


def updateNewsToServer(data: list = None):
    """
    @Description:
        推送當日新聞到Stocker server\n
        Push daily news to the Stocker server\n
    @Param:
        data: list of maps (default: [])
    @Return:
        N/A
    """
    if data is None:
        return

    # Update to stocker server
    newsApi = f"{stockerUrl}/feed"
    for _, item in enumerate(data):
        try:
            rsp = requests.post(newsApi, data=json.dumps(item), timeout=10)
            if rsp.status_code < 200 or rsp.status_code > 299:
                raise ConnectionError
        except ConnectionError:
            pushLog("Stocker每日新聞", "server error: connection failure")
            break
        except Exception as ex:
            pushLog("Stocker每日新聞", f"server error: {ex}")
