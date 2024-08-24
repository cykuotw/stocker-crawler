from datetime import datetime
from time import sleep

import feedparser
import requests

from crawler.common.notifier import pushNewsMessge
from crawler.common.util.config import getYahooConfig
from crawler.common.util.server import getStockNoBasicInfo, updateNewsToServer


def crawlNewsYahoo(companyID: str = '2330'):
    """
    @Description:
        爬取Yahoo Stock個股每日新聞\n
        Crawl daily news of specific companyID form Yahoo Stock\n
    @Param:
        companyID => string (default: '2330')
    @Return:
        json (see example) (empty if companyID not valid)
    """

    headers = {
        'User-Agent': ("Mozilla/5.0 "
                       "(Macintosh; Intel Mac OS X 10_10_1) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/39.0.2171.95 Safari/537.36"),
        'Content-Type': 'text/xml;'
    }

    url = f"https://tw.stock.yahoo.com/rss?s={companyID}"

    waitTime = 1  # second
    i, maxRetry = 0, 3
    done = False
    feed = None

    while not done and i < maxRetry:
        try:
            rsp = requests.get(url, headers, timeout=10)
        except requests.Timeout:
            sleep(waitTime)
            waitTime *= 2
            i += 1
            continue

        # if status code is not 200 ok
        # retry 5 times max, each time extends wait time by 2x
        if rsp.status_code != 200:
            sleep(waitTime)
            waitTime *= 2
            i += 1
            continue

        feed = feedparser.parse(rsp.text)
        done = True

    if feed is None:
        return {}

    data = []
    for item in feed['entries']:
        publishTime = datetime.strptime(
            item['published'], '%a, %d %b %Y %H:%M:%S %Z')
        tmp = {}
        tmp['link'] = item['link']
        tmp['stocks'] = [companyID]
        tmp['title'] = item['title']
        tmp['source'] = 'yahoo'
        tmp['releaseTime'] = publishTime.isoformat()
        tmp['feedType'] = "news"
        tmp['tags'] = []
        tmp['description'] = item['summary']

        data.append(tmp)

    return data


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
    config = getYahooConfig()
    totalSlices = config['total-slices']
    currentSlices = config['current-slices']

    pushNewsMessge(f"Yahoo crawler ({currentSlices}/{totalSlices}) start")

    idList = getStockNoBasicInfo()
    start = round(len(idList) * (currentSlices-1) / totalSlices)
    end = round(len(idList) * (currentSlices) / totalSlices)
    idList = idList[start:end]

    try:
        for _, stockId in enumerate(idList):
            news = crawlNewsYahoo(str(stockId))
            updateNewsToServer(news)
            sleep(0.005)

    except Exception as ex:
        pushNewsMessge(f"Yahoo crawler error: {ex}")

    pushNewsMessge(f"Yahoo crawler ({currentSlices}/{totalSlices}) done")
