import calendar
import gc
import json
from datetime import datetime, timedelta
from time import sleep

import feedparser
import pytz
import requests
from bs4 import BeautifulSoup
from dateutil import tz

# export example:
# {
#     "data_count": "1",
#     "data":[
#         {
#             "link": "example.com.tw/5566789",
#             "stocks": [
#              "2330", "2454" ...
#             ],
#             "title": "blahblahblahblah",
#             "source": "cynes",
#             "releaseTime": 2022-12-22T14:35:06 // iso format
#             "feedType" = "news",
#             "tags" = []
#             "description" = 'dafsdfasfd'
#         },
#         ...
#     ]
# }


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
        'User-Agent': """Mozilla/5.0
                    (Macintosh; Intel Mac OS X 10_10_1)
                    AppleWebKit/537.36 (KHTML, like Gecko)
                    Chrome/39.0.2171.95 Safari/537.36""",
        'Content-Type': 'text/xml;'
    }

    url = f"https://tw.stock.yahoo.com/rss?s={companyID}"

    waitTime = 5
    feed = None
    for _ in range(5):
        rsp = requests.get(url, headers, timeout=10)

        # if status code is not 200 ok
        # retry 5 times max, each time extend wait time by 2x
        if rsp.status_code != 200:
            sleep(waitTime)
            waitTime *= 2
            continue

        feed = feedparser.parse(rsp.text)

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

    result = {}
    result['data_count'] = len(data)
    result['data'] = data

    return result


def crawlNewsCnyes(date: datetime = datetime.today(), market: str = "tw"):
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
    url = f"""https://api.cnyes.com/media/api/v1/newslist/category/{market}?
                startAt={str(todayStartSec)}&endAt={str(todayEndSec)}&limit=30&page=1"""

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
            newsUrl = f"https://news.cnyes.com/news/id/{newsid}"

            stockId = []
            # append 'code' to stock_id if tag 'market' exist
            if 'market' in element:
                for i in range(len(element['market'])):
                    # check if it is tw stock
                    if 'TWS' in element['market'][i]['symbol']:
                        stockId.append(element['market'][i]['code'])
            # check stock_id not empty
            # if len(stock_id) != 0:
            dataCount += 1

            tmp = {}
            tmp['link'] = newsUrl
            tmp['stocks'] = stockId
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


def crawlNewsCtee(newsType: str = "industry"):
    """
    @Description:
        爬取工商時報科技版每日新聞\n
        Crawl daily news of tech from CTEE\n
    @Param:
        newsType => string (default: "industry")
                        "industry": industrial headline
                        "tech": technology headlines
                        "world": world headlines
    @Return:
        json (see example)
    """

    if newsType not in ["industry", "tech", "world"]:
        return json.dumps({})

    # request header
    headers = {
        'User-Agent': ("Mozilla/5.0 "
                       "(Macintosh; Intel Mac OS X 10_10_1) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/39.0.2171.95 Safari/537.36"),
        'Content-Type': 'text/xml;'
    }

    url = f"https://www.ctee.com.tw/rss_web/livenews/{newsType}"

    waitTime = 15
    entries = None
    for _ in range(5):
        rsp = requests.get(url, headers=headers, timeout=5)

        # if status code is not 200 ok
        # retry 5 times max, each time extend wait time by 2x
        if rsp.status_code != 200:
            sleep(waitTime)
            waitTime *= 2
            continue

        feed = feedparser.parse(rsp.text)
        entries = feed['entries']

    if entries is None:
        return {}

    dataCount = 0
    data = []
    for _, e in enumerate(entries):
        publishTime = datetime.strptime(
            e['published'], '%Y-%m-%dT%H:%M:%S')
        title = e['title']
        link = e['link']
        description = e['summary'].replace("\n", "")

        tmp = {}
        tmp['link'] = link
        tmp['stocks'] = []
        tmp['title'] = title
        tmp['source'] = 'ctee'
        tmp['releaseTime'] = publishTime.isoformat()
        tmp['feedType'] = 'news'
        tmp['tags'] = []
        tmp['description'] = description

        data.append(tmp)
        dataCount += 1

    res = {}
    res["data_count"] = str(dataCount)
    res["data"] = data
    return res


def crawlNewsUdn(newsType: str = "stock/head"):
    """
    @Description:
        爬取經濟日報產業版每日新聞\n
        Crawl daily news of tech from CTEE\n
    @Param:
        newsType => string (default: "stock/head")
                        "stock/head": stock headline news
                        "stock/sii": stock listed section
                        "stock/otc": stock otc section
                        "ind/head": industrial headline news
                        "int/head": international headline news

    @Return:
        json (see example)(empty if @Param newsType is not in the list)
    """
    gc.enable()
    # Assume machine timezone is CST

    if newsType not in ["stock/head", "stock/sii", "stock/otc",
                        "ind/head", "int/head"]:
        return json.dumps({})

    # request header
    headers = {
        'User-Agent': """Mozilla/5.0
                    (Macintosh; Intel Mac OS X 10_10_1)
                    AppleWebKit/537.36 (KHTML, like Gecko)
                    Chrome/39.0.2171.95 Safari/537.36""",
        'Content-Type': 'text/html; charset=UTF-8'
    }

    # data container
    dataCount = 0
    data = []

    # time
    today = datetime.now(tz=tz.gettz('Asia/Taipei'))
    todayTmp = today
    prevTmp = today

    # while loop prep
    pageNo = 1
    flag = True

    while flag and pageNo < 100:
        url = ""
        if newsType == "stock/head":
            url = f"https://money.udn.com/money/get_article/{pageNo}/1001/5590/5607"
        elif newsType == "stock/sii":
            url = f"https://money.udn.com/money/get_article/{pageNo}/1001/5590/5710"
        elif newsType == "stock/otc":
            url = f"https://money.udn.com/money/get_article/{pageNo}/1001/5590/11074"
        elif newsType == "ind/head":
            url = f"https://money.udn.com/money/get_article/{pageNo}/1001/5591/5612"
        elif newsType == "int/head":
            url = f"https://money.udn.com/money/get_article/{pageNo}/1001/5588/5599"

        result = requests.get(url, headers, timeout=(2, 15))
        result.encoding = 'utf-8'

        liList = BeautifulSoup(result.text, 'html.parser').find_all('li')
        for _, li in enumerate(liList):
            title = li.find('a').get('title').strip()
            link = f"https://money.udn.com/{li.find('a').get('href')}"
            publishDate = todayTmp.replace(
                hour=int(li.find('span').string[:2]),
                minute=int(li.find('span').string[-2:]),
                second=0, microsecond=0).astimezone(tz=pytz.timezone('Asia/Taipei'))

            diff = today - publishDate
            # publish time cross 12 am
            if pageNo > 2 and diff < timedelta(days=0):
                if today.day-1 <= 0:
                    publishDate = publishDate.replace(
                        month=today.month-1,
                        day=calendar.monthrange(today.year, today.month-1)[1])
                else:
                    publishDate = publishDate.replace(day=today.day-1)
                diff = today - publishDate
            # publish time is eariler yesterday's current time
            if pageNo != 1 and (prevTmp-publishDate) < timedelta(days=0):
                flag = False
                break

            if diff < timedelta(days=1):
                dataCount += 1
                publishDate = publishDate.astimezone(tz=pytz.utc)

                tmp = {}
                tmp['link'] = link
                tmp['stocks'] = []
                tmp['title'] = title
                tmp['source'] = 'money'
                tmp['releaseTime'] = publishDate.isoformat()
                tmp['feedType'] = 'news'
                tmp['tags'] = []
                tmp['description'] = ''

                data.append(tmp)
                prevTmp = publishDate
            else:
                flag = False
                break
        pageNo += 1

    gc.collect()
    gc.disable()

    res = {}
    res["data_count"] = str(dataCount)
    res["data"] = data
    return res
