import json
from datetime import datetime
from time import sleep

import requests
from notifier.util import pushSlackMessage
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
        pushSlackMessage("Stocker新聞抓取", 'CNYES crawler work error: {}'.format(ex))

    try:
        # Get Ctee News
        tmp = crawlNewsCtee(datetimeIn)
        for index in range(int(tmp['data_count'])):
            if tmp['data'][index] not in data:
                count += 1
                data.append(tmp['data'][index])
    except Exception as ex:
        pushSlackMessage("Stocker新聞抓取", 'CTEE crawler work error: {}'.format(ex))

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
        pushSlackMessage("Stocker新聞抓取", 'UDN crawler work error: {}'.format(ex))

    if count == 0:
        return

    # Update to stocker server
    newsApi = "{url}/feed".format(url=stockerUrl)
    for index in range(count):
        try:
            requests.post(newsApi, data=json.dumps(data[index]))
        except Exception as ex:
            print("ERROR: {}".format(ex))


if __name__ == '__main__':
    updateDailyNews()
