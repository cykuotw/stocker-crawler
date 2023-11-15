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

    count = 0
    data = []

    pushSlackMessage(
        "Stocker每日新聞",
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} crawler work start")
    pushDiscordLog(
        "Stocker每日新聞",
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} crawler work start")

    try:
        # Get CNYES News
        marketList = ["tw", "us"]

        for market in marketList:
            tmp = crawlNewsCnyes(datetimeIn, market)
            for index in range(int(tmp['data_count'])):
                if tmp['data'][index] not in data:
                    count += 1
                    data.append(tmp['data'][index])
    except Exception as ex:
        pushSlackMessage(
            "Stocker每日新聞",
            f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} CNYES crawler work error: {ex}")
        pushDiscordLog(
            "Stocker每日新聞",
            f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} CNYES crawler work error: {ex}")

    try:
        # Get Ctee News
        newsList = ["industry", "tech", "world"]
        for news in newsList:
            tmp = crawlNewsCtee(newsList)

            for index in range(int(tmp['data_count'])):
                if tmp['data'][index] not in data:
                    count += 1
                    data.append(tmp['data'][index])
    except Exception as ex:
        pushSlackMessage(
            "Stocker每日新聞",
            f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} CTEE crawler work error: {ex}")
        pushDiscordLog(
            "Stocker每日新聞",
            f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} CTEE crawler work error: {ex}")

    try:
        # Get Udn News
        newsList = ["stock/head", "stock/sii", "stock/otc",
                    "ind/head", "int/head"]
        for news in newsList:
            tmp = crawlNewsUdn(news)
            for index in range(int(tmp['data_count'])):
                if tmp['data'][index] not in data:
                    count += 1
                    data.append(tmp['data'][index])
    except Exception as ex:
        pushSlackMessage(
            "Stocker每日新聞",
            f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} UDN crawler work error: {ex}")
        pushDiscordLog(
            "Stocker每日新聞",
            f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} UDN crawler work error: {ex}")

    try:
        # Get Yahoo News
        idList = getStockNoBasicInfo()

        for _, stockId in enumerate(idList):
            tmp = crawlNewsYahoo(str(stockId))
            for _, news in enumerate(tmp['data']):
                if news not in data:
                    count += 1
                    data.append(news)
    except Exception as ex:
        pushSlackMessage(
            "Stocker每日新聞",
            f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} Yahoo crawler work error: {ex}")
        pushDiscordLog(
            "Stocker每日新聞",
            f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} Yahoo crawler work error: {ex}")

    if count == 0:
        return

    # Update to stocker server
    newsApi = f"{stockerUrl}/feed"
    for index in range(count):
        try:
            requests.post(newsApi,
                          data=json.dumps(data[index]),
                          timeout=(2, 5))
        except Exception as ex:
            pushSlackMessage(
                "Stocker每日新聞",
                f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} server error: {ex}")
            pushDiscordLog(
                "Stocker每日新聞",
                f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} server error: {ex}")

    pushSlackMessage(
        "Stocker每日新聞", f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} crawler work done")
    pushDiscordLog(
        "Stocker每日新聞", f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} crawler work done")


if __name__ == '__main__':
    updateDailyNews()
