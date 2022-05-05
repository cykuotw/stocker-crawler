# coding=utf-8
import requests
from datetime import datetime
import feedparser

def crawlRSSCompanyNews(companyID):
    """
    @Description:
        爬取各股每日新聞\n
        Crawl daily news of all stocks\n
        ** Under Construction **
    @Param:
        companyID => int
    @Return:
        list (news in json)
    """

    coID = str(companyID)
    url = "https://tw.stock.yahoo.com/rss/s/" + coID

    res = requests.get(url)
    res.encoding = "big5"
    feed = feedparser.parse(res.text)
    for item in feed.entries:
        dateTime = datetime.strptime(item.pubDate, '%a, %d %b %Y %H:%M:%S %Z')
        print('datetime', dateTime.isoformat())
        print('title', item.title)
        print('link', item.link)
        print('description', item.description)
        print('stock_id', coID)
        print("======================================")


