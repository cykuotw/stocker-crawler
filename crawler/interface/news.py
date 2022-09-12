import json
from datetime import datetime
from time import sleep

import requests
from crawler.core.news import crawlNewsCnyes, crawlNewsCtee
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

    # Get CNYES News
    marketList = ["tw", "us"]

    for market in marketList:
        tmp = crawlNewsCnyes(datetimeIn, market)
        for index in range(int(tmp['data_count'])):
            if tmp['data'][index] not in data:
                count += 1
                data.append(tmp['data'][index])

    # Get Ctee News
    tmp = crawlNewsCtee(datetimeIn)
    for index in range(int(tmp['data_count'])):
        if tmp['data'][index] not in data:
            count += 1
            data.append(tmp['data'][index])

    if count == 0:
        return

    # Update to stocker server
    newsApi = "{url}/feed".format(url=stockerUrl)
    print(newsApi)
    for index in range(count):
        try:
            requests.post(newsApi, data=json.dumps(data[index]))
            sleep(0.01)
        except Exception as ex:
            print("ERROR: {}".format(ex))


if __name__ == '__main__':
    updateDailyNews()
