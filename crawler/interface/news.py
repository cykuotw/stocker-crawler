import json
from datetime import datetime

import requests

from crawler.core.news import (
    crawlNewsCnyes,
    crawlNewsCtee,
    crawlNewsUdn,
    crawlNewsYahoo,
)
from crawler.interface.basicInfo import getStockNoBasicInfo
from crawler.interface.util import stockerUrl
from notifier.discord import pushDiscordLog
from notifier.util import pushSlackMessage


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

    pushSlackMessage(
        "Stocker每日新聞",
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} {message}")
    pushDiscordLog(
        "Stocker每日新聞",
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} {message}")


def updateNewsToServer(data: list = None):
    """
    @Description:
        推送當日新聞至Stocker伺服器\n
        Update daily news stocker server\n
    @Param:
        data => list of dict (default: None)
    @Return:
        N/A
    """
    if data is None or len(data) == 0:
        return

    newsApi = f"{stockerUrl}/feed"
    for _, d in enumerate(data):
        try:
            requests.post(newsApi,
                          data=json.dumps(d),
                          timeout=(2, 5))
        except Exception as ex:
            pushNewsMessge(f"stocker server error: {ex}")


def updateDailyNewsCnyes(datetimeIn: datetime = datetime.today()):
    """
    @Description:
        更新每日鉅亨網新聞\n
        Update all daily news related to tw stock market
        from cnyes to stocker server\n
    @Param:
        datetimeIn => datetime.datetime (default: today)
    @Return:
        N/A
    """
    try:
        marketList = ["tw", "us"]

        for market in marketList:
            news = crawlNewsCnyes(datetimeIn, market)
            updateNewsToServer(news['data'])
    except Exception as ex:
        pushNewsMessge(f"CNYES crawler work error: {ex}")


def updateDailyNewsCtee():
    """
    @Description:
        更新每日工商日報新聞\n
        Update all daily news related to tw stock market
        from ctee to stocker server\n
    @Param:
        N/A
    @Return:
        N/A
    """
    try:
        newsType = ["industry", "tech", "world"]
        for t in newsType:
            news = crawlNewsCtee(t)
            updateNewsToServer(news)
    except Exception as ex:
        pushNewsMessge(f"CTEE crawler work error: {ex}")


def updateDailyNewsUdn():
    """
    @Description:
        更新每日經濟日報新聞\n
        Update all daily news related to tw stock market
        from udn to stocker server\n
    @Param:
        N/A
    @Return:
        N/A
    """
    try:
        newsType = ["stock/head", "stock/sii", "stock/otc",
                    "ind/head", "int/head"]
        for t in newsType:
            news = crawlNewsUdn(t)
            updateNewsToServer(news)
    except Exception as ex:
        pushNewsMessge(f"UDN crawler work error: {ex}")


def updateDailyNewsYahoo():
    """
    @Description:
        更新每日Yahoo新聞\n
        Update all daily news related to tw stock market
        from yahoo to stocker server\n
    @Param:
        N/A
    @Return:
        N/A
    """
    try:
        idList = getStockNoBasicInfo()

        for _, stockId in enumerate(idList):
            news = crawlNewsYahoo(str(stockId))
            updateNewsToServer(news)
    except Exception as ex:
        pushNewsMessge(f"Yahoo crawler work error: {ex}")


def updateDailyNews():
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
    pushNewsMessge("crawler work start")

    updateDailyNewsCnyes()
    updateDailyNewsCtee()
    updateDailyNewsUdn()
    updateDailyNewsYahoo()

    pushNewsMessge("crawler work stop")


if __name__ == '__main__':
    updateDailyNews()
