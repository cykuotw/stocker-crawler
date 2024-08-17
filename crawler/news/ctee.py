import gc
import json
from datetime import datetime

import feedparser
import requests

from crawler.common.notifier import pushNewsMessge
from crawler.common.util.server import updateNewsToServer


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
    gc.enable()

    if newsType not in ["industry", "tech", "world"]:
        return json.dumps({})

    # request header
    headers = {
        'User-Agent': (
            "Mozilla/5.0 " +
            "(Macintosh; Intel Mac OS X 10_10_1) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/39.0.2171.95 Safari/537.36"
        ),
        'Accept': "*/*",
        "Sec-Fetch-User": "?1",
        "Content-Type": 'application/rss+xml; charset=utf-8',
        "Referer": "https://www.ctee.com.tw/livenews/industry"
    }

    url = f"https://www.ctee.com.tw/rss_web/livenews/{newsType}"

    result = requests.get(url, headers=headers, timeout=5)
    feed = feedparser.parse(result.text)
    entries = feed['entries']

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

    gc.collect()
    gc.disable()

    # result = {}
    # result['data_count'] = len(data)
    # result['data'] = data
    return data


def updateDailyNewsCtee():
    """
    @Description:
        更新每日工商日報新聞\n
        Update all daily news related to tw stock market
        from ctee to stocker server\n
    @Param:
        N/A
    @Return:
        N/A
    """
    pushNewsMessge("CTEE crawler start")
    try:
        newsType = ["industry", "tech", "world"]
        for t in newsType:
            news = crawlNewsCtee(t)
            updateNewsToServer(news)
    except Exception as ex:
        pushNewsMessge(f"CTEE crawler work error: {ex}")
    pushNewsMessge("CTEE crawler done")
