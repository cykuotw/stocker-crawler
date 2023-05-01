import json
from datetime import datetime

import requests
from notifier.util import pushSlackMessage
from notifier.discord import pushDiscordLog
from crawler.core.news import crawlNewsCnyes, crawlNewsCtee, crawlNewsUdn
from crawler.interface.util import stockerUrl


def updateDailyNews(datetimeIn=datetime.today()):
    """
    @Description:
        更新每日鉅亨網/工商日報的所有新聞\n
        Update all daily news related to tw stock market
        from cnyes/ctee to stocker server\n
    @Param:
        datetimeIn => datetime.datetime (default: today)
    @Return:
        N/A
    """

    count = 0
    data = []

    pushSlackMessage("Stocker每日新聞", "{} crawler work start".format(
        datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
    pushDiscordLog("Stocker每日新聞", "{} crawler work start".format(
        datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))

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
        pushSlackMessage("Stocker每日新聞", "{} CNYES crawler work error: {}".format(
            datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ex))
        pushDiscordLog("Stocker每日新聞", "{} CNYES crawler work error: {}".format(
            datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ex))

    try:
        # Get Ctee News
        tmp = crawlNewsCtee(datetimeIn)
        for index in range(int(tmp['data_count'])):
            if tmp['data'][index] not in data:
                count += 1
                data.append(tmp['data'][index])
    except Exception as ex:
        pushSlackMessage("Stocker每日新聞", "{} CTEE crawler work error: {}".format(
            datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ex))
        pushDiscordLog("Stocker每日新聞", "{} CTEE crawler work error: {}".format(
            datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ex))

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
        pushSlackMessage("Stocker每日新聞", "{} UDN crawler work error: {}".format(
            datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ex))
        pushDiscordLog("Stocker每日新聞", "{} UDN crawler work error: {}".format(
            datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ex))

    if count == 0:
        return

    # Update to stocker server
    newsApi = "{url}/feed".format(url=stockerUrl)
    for index in range(count):
        try:
            requests.post(newsApi, data=json.dumps(data[index]))
        except Exception as ex:
            pushSlackMessage("Stocker每日新聞", "{} server error: {}".format(
                datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ex))
            pushDiscordLog("Stocker每日新聞", "{} server error: {}".format(
                datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ex))

    pushSlackMessage("Stocker每日新聞", "{} crawler work done".format(
        datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
    pushDiscordLog("Stocker每日新聞", "{} crawler work done".format(
        datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))


if __name__ == '__main__':
    updateDailyNews()
