import calendar
import gc
import json
from datetime import datetime, timedelta

import pytz
import requests
from bs4 import BeautifulSoup
from dateutil import tz

from crawler.common.notifier import pushNewsMessge
from crawler.common.util.server import updateNewsToServer


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
        'User-Agent': ("Mozilla/5.0 "
                       "(Macintosh; Intel Mac OS X 10_10_1) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/39.0.2171.95 Safari/537.36"),
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
            link = f"https://money.udn.com{li.find('a').get('href')}"
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

    # result = {}
    # result['data_count'] = len(data)
    # result['data'] = data
    return data


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
    pushNewsMessge("UDN crawler start")
    try:
        newsType = ["stock/head", "stock/sii", "stock/otc",
                    "ind/head", "int/head"]
        for t in newsType:
            news = crawlNewsUdn(t)
            updateNewsToServer(news)
    except Exception as ex:
        pushNewsMessge(f"UDN crawler work error: {ex}")
    pushNewsMessge("UDN crawler done")
