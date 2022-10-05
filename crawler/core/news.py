# coding=utf-8
from ast import While
import json
from datetime import datetime, timedelta
from math import fabs

import feedparser
import requests
from bs4 import BeautifulSoup
from crawler.core.util import formatJSON
from dateutil import parser

# export example:
# {
#     "data_count": "1",
#     "data":[
#         {
#             "link": "example.com.tw/5566789",
#             "stock_id": [
#              "2330", "2454" ...
#             ],
#             "title": "blahblahblahblah",
#             "source": "cynes",
#             "releaseTime": 1662024303 //sec from 1970/1/1
#         },
#         ...
#     ]
# }


def crawlNewsYahoo(companyID):
    """
    @Description:
        爬取Yahoo Stock個股每日新聞\n
        Crawl daily news of specific companyID form Yahoo Stock\n
        ** Under Construction **
    @Param:
        companyID => int
    @Return:
        json (see example)
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


def crawlNewsCnyes(date=datetime.today(), market="tw"):
    """
    @Description:
        爬取鉅亨網個股每日新聞\n
        Crawl daily news of all Taiwan stocks from CNYES\n
    @Param:
        date => datetime (default: system current date)
        market => string ("tw", "us")
    @Return:
        json (see example)(empty if @Param market is neither "tw", "us")
    """

    # Check parameter
    if market != "tw" and market != "us":
        return json.dumps({})

    # generate timestamp
    epochTime = datetime(1970, 1, 1)

    todayStart = date.replace(hour=0, minute=0, second=0, microsecond=0)
    todayEnd = todayStart + timedelta(days=1)
    todayStartSec = int((todayStart-epochTime).total_seconds())
    todayEndSec = int((todayEnd-epochTime).total_seconds())

    # generate url
    if market == "tw":
        market = "tw_stock_news"
    elif market == "us":
        market = "us_stock"
    url = """https://api.cnyes.com/media/api/v1/newslist/category/{market}?startAt={start}&endAt={end}&limit=30&page=1""".format(
        market=market, start=todayStartSec, end=todayEndSec)

    # generate header
    headers = {
        'User-Agent': """Mozilla/5.0
                    (Macintosh; Intel Mac OS X 10_10_1)
                    AppleWebKit/537.36 (KHTML, like Gecko)
                    Chrome/39.0.2171.95 Safari/537.36""",
        'Content-Type': 'application/json'
    }

    # get meta data form CNYES json response
    result = requests.get(url, headers, timeout=(2, 15))
    result.encoding = 'utf-8'
    jsdata = json.loads(result.text)

    # iterate all json pages
    dataCount = 0
    data = []
    lastPage = jsdata['items']['last_page']
    for page in range(lastPage):
        # get real all news from CNYES json response
        url = url.split("page=")[0] + "page=" + str(page+1)
        result = requests.get(url, headers, timeout=(2, 15))
        jsdata = json.loads(result.text)

        # iterate all news
        length = int(jsdata['items']['to']) - int(jsdata['items']['from']) + 1
        for index in range(length):
            element = jsdata['items']['data'][index]
            newsid = element['newsId']
            title = element['title']
            releaseTime = element['publishAt']
            releaseTime = epochTime + timedelta(seconds=releaseTime)
            newsUrl = "https://news.cnyes.com/news/id/{id}".format(id=newsid)

            stock_id = []
            # append 'code' to stock_id if tag 'market' exist
            if 'market' in element:
                for i in range(len(element['market'])):
                    # check if it is tw stock
                    if 'TWS' in element['market'][i]['symbol']:
                        stock_id.append(element['market'][i]['code'])
            # check stock_id not empty
            # if len(stock_id) != 0:
            dataCount += 1

            tmp = {}
            tmp['link'] = newsUrl
            tmp['stocks'] = stock_id
            tmp['title'] = title
            tmp['source'] = 'cnyes'
            tmp['releaseTime'] = releaseTime.isoformat()
            tmp['feedType'] = 'news'
            tmp['tags'] = []
            tmp['description'] = ''

            data.append(tmp)

    res = {}
    res["data_count"] = str(dataCount)
    res["data"] = data
    return res


def crawlNewsCtee(date=datetime.today()):
    """
    @Description:
        爬取工商時報科技版每日新聞\n
        Crawl daily news of tech from CTEE\n
    @Param:
        date => datetime (default: system current date)
    @Return:
        json (see example)(empty if @Param market is neither "tw", "us")
    """

    # request header
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'Content-Type': 'text/html; charset=UTF-8'
    }

    # data container
    dataCount = 0
    data = []

    today = date.replace(hour=0, minute=0, second=0,
                         microsecond=0, tzinfo=None)

    # while loop prep
    pageNo = 1
    flag = True

    while flag:
        if pageNo == 1:
            url = 'https://ctee.com.tw/category/news/tech,industry,biotech'
        else:
            url = 'https://ctee.com.tw/category/news/tech,industry,biotech/page/{}'.format(
                pageNo)

        page = requests.get(url, headers=headers, timeout=(2, 15))
        article = BeautifulSoup(page.text, 'html.parser').findAll('article')

        if (len(article) == 0):
            break

        for index in range(len(article)):
            title = article[index].find('a').get('title')
            link = article[index].find('a').get('href')
            publishDate = parser.parse(article[index].find(
                'time').get('datetime')).replace(tzinfo=None)

            diff = publishDate - today
            # Publish date too early, stop all process
            if diff < timedelta(days=0):
                flag = False
                break
            # Publish date within 1 day of given date
            if diff < timedelta(days=1):
                dataCount += 1

                tmp = {}
                tmp['link'] = link
                tmp['stocks'] = []
                tmp['title'] = title
                tmp['source'] = 'ctee'
                tmp['releaseTime'] = publishDate.isoformat()
                tmp['feedType'] = 'news'
                tmp['tags'] = []
                tmp['description'] = ''

                data.append(tmp)
            else:
                # stop while loop
                flag = False
                break
        pageNo += 1

    res = {}
    res["data_count"] = str(dataCount)
    res["data"] = data
    return res


if __name__ == '__main__':
    data = crawlNewsCnyes(market="tw")
    print(formatJSON(data))
