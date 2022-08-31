from datetime import datetime
import requests
import json
from crawler.core.news import crawlNewsCnyes
from crawler.interface.util import stockerUrl


def updateDailyNews(datetimeIn=datetime.today()):
    """
    @Description:
        更新每日鉅亨網的所有新聞\n
        Update all daily news related to tw stock market
        from cnyes to stocker server\n
    @Param:
        datetimeIn => datetime.datetime (default: today)
    @Return:
        N/A
    """

    # Get News
    marketList = ["tw", "us"]

    newsData = {
        'data_count': '0',
        'data': []
    }
    count = 0
    for market in marketList:
        tmp = crawlNewsCnyes(datetimeIn, market)
        for index in range(int(tmp['data_count'])):
            if tmp['data'][index] not in newsData['data']:
                count += 1
                newsData['data'].append(tmp['data'][index])
    newsData['data_count'] = count

    if count == 0:
        return

    # Update to stocker server
    newsApi = "{url}/feeds/{datestr}".format(url=stockerUrl, datestr=datetimeIn.strftime("%Y%m%d"))
    try:
        requests.post(newsApi, data=json.dumps(newsData))
    except Exception as ex:
        print("ERROR: {}".format(ex))
    
if __name__ == '__main__':
    updateDailyNews()
