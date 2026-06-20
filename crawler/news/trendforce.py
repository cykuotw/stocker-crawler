import asyncio
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import feedparser

from crawler.common.notifier import pushNewsMessge
from crawler.common.util.server import updateNewsToServer
from crawler.news.headers import (
    MODERN_BROWSER_USER_AGENT,
    RSS_ACCEPT,
    ZH_TW_ACCEPT_LANGUAGE,
)


TRENDFORCE_BASE_URL = "https://www.trendforce.com.tw"

TRENDFORCE_FEEDS = {
    "Semiconductors": {
        "url": "/feed/Semiconductors.html",
        "tag": "半導體",
    },
    "Display": {
        "url": "/feed/Display.html",
        "tag": "顯示器",
    },
    "LED": {
        "url": "/feed/LED.html",
        "tag": "LED",
    },
    "Energy": {
        "url": "/feed/Energy.html",
        "tag": "能源",
    },
    "Consumer_electronics": {
        "url": "/feed/Consumer_electronics.html",
        "tag": "消費性電子",
    },
    "Communication": {
        "url": "/feed/Communication.html",
        "tag": "通訊",
    },
    "Emerging_technology": {
        "url": "/feed/Emerging_technology.html",
        "tag": "新興科技",
    },
    "macroeconomic": {
        "url": "/feed/macroeconomic.html",
        "tag": "總體經濟",
    },
}


def _parseReleaseTime(value: str) -> str:
    if not value:
        return datetime.today().isoformat()

    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return datetime.today().isoformat()


def _isTrendForceNewsLink(link: str) -> bool:
    return (
        link.startswith(f"{TRENDFORCE_BASE_URL}/presscenter/news/")
        and link.endswith(".html")
    )


async def crawlNewsTrendForce(
    newsType: str = "Semiconductors",
    session: Optional[aiohttp.ClientSession] = None,
):
    """
    @Description:
        爬取 TrendForce RSS 新聞\n
        Crawl daily news from TrendForce RSS feeds\n
    @Param:
        newsType => string (default: "Semiconductors")
    @Return:
        list of news dicts
    """
    if newsType not in TRENDFORCE_FEEDS:
        return []

    headers = {
        "User-Agent": MODERN_BROWSER_USER_AGENT,
        "Accept": RSS_ACCEPT,
        "Accept-Language": ZH_TW_ACCEPT_LANGUAGE,
        "Referer": "https://www.trendforce.com.tw/presscenter/rss.html",
    }
    feedConfig = TRENDFORCE_FEEDS[newsType]
    url = urljoin(TRENDFORCE_BASE_URL, feedConfig["url"])

    closeSession = session is None
    if closeSession:
        session = aiohttp.ClientSession()

    try:
        async with session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10, sock_connect=3),
        ) as result:
            text = await result.text()
        feed = await asyncio.to_thread(feedparser.parse, text)
    finally:
        if closeSession:
            await session.close()

    data = []
    for entry in feed.entries:
        link = urljoin(TRENDFORCE_BASE_URL, entry.get("link", ""))
        if not _isTrendForceNewsLink(link):
            continue

        title = entry.get("title", "").strip()
        if not title:
            continue

        description = entry.get("summary", "").replace("\n", "").strip()
        publishTime = _parseReleaseTime(entry.get("published", ""))

        data.append({
            "link": link,
            "stocks": [],
            "title": title,
            "source": "trendforce",
            "releaseTime": publishTime,
            "feedType": "news",
            "tags": [feedConfig["tag"]],
            "description": description,
        })

    return data


async def updateDailyNewsTrendForceAsync():
    """
    @Description:
        更新每日 TrendForce 新聞\n
        Update all daily news from TrendForce to stocker server\n
    @Param:
        N/A
    @Return:
        N/A
    """
    pushNewsMessge("TrendForce crawler start")
    try:
        async def fetchTypeNews(
            newsType: str,
            session: aiohttp.ClientSession,
        ):
            return await crawlNewsTrendForce(newsType, session=session)

        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(*[
                fetchTypeNews(newsType, session)
                for newsType in TRENDFORCE_FEEDS
            ])

            seenLinks = set()
            news = []
            for feedNews in results:
                for item in feedNews:
                    if item["link"] in seenLinks:
                        continue
                    seenLinks.add(item["link"])
                    news.append(item)

            await updateNewsToServer(news, session=session)
    except Exception as ex:
        pushNewsMessge(f"TrendForce crawler work error: {ex}")
    pushNewsMessge("TrendForce crawler done")


def updateDailyNewsTrendForce():
    """
    @Description:
        更新每日 TrendForce 新聞\n
        Update all daily news from TrendForce to stocker server\n
    @Param:
        N/A
    @Return:
        N/A
    """
    asyncio.run(updateDailyNewsTrendForceAsync())
