import asyncio
from datetime import datetime
from typing import Optional

import aiohttp
import feedparser

from crawler.common.notifier import pushNewsMessge
from crawler.common.util.config import getYahooConfig
from crawler.common.util.server import getStockNoBasicInfo, updateNewsToServer


MAX_CONCURRENT_REQUESTS = 5


async def crawlNewsYahoo(
    companyID: str = '2330',
    session: Optional[aiohttp.ClientSession] = None,
):
    """
    @Description:
        爬取Yahoo Stock個股每日新聞
        Crawl daily news of specific companyID form Yahoo Stock
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

    feed = None

    async def fetch(active_session: aiohttp.ClientSession):
        waitTime = 1  # second
        i, maxRetry = 0, 3

        while i < maxRetry:
            try:
                async with active_session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as rsp:
                    # if status code is not 200 ok, retry with backoff
                    if rsp.status != 200:
                        await asyncio.sleep(waitTime)
                        waitTime *= 2
                        i += 1
                        continue

                    text = await rsp.text()
                    return await asyncio.to_thread(feedparser.parse, text)
            except (aiohttp.ClientError, asyncio.TimeoutError):
                await asyncio.sleep(waitTime)
                waitTime *= 2
                i += 1

        return None

    if session is None:
        async with aiohttp.ClientSession() as active_session:
            feed = await fetch(active_session)
    else:
        feed = await fetch(session)

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


async def updateDailyNewsYahooAsync():
    """
    @Description:
        非同步更新每日Yahoo新聞
        Async update all daily news related to tw stock market
        from yahoo to stocker server
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

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def updateStockNews(
        stockId: str,
        session: aiohttp.ClientSession,
    ):
        async with semaphore:
            news = await crawlNewsYahoo(str(stockId), session=session)
            await updateNewsToServer(news, session=session)
            await asyncio.sleep(0.005)

    try:
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[
                updateStockNews(stockId, session)
                for stockId in idList
            ])

    except Exception as ex:
        pushNewsMessge(f"Yahoo crawler error: {ex}")

    pushNewsMessge(f"Yahoo crawler ({currentSlices}/{totalSlices}) done")


def updateDailyNewsYahoo():
    """
    @Description:
        更新每日Yahoo新聞
        Update all daily news related to tw stock market
        from yahoo to stocker server
    @Param:
        N/A
    @Return:
        N/A
    """
    asyncio.run(updateDailyNewsYahooAsync())
