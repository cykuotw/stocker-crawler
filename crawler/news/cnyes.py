import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from crawler.common.notifier import pushNewsMessge
from crawler.common.util.server import updateNewsToServer


async def crawlNewsCnyes(
    date: datetime = datetime.today(),
    market: str = "tw",
    session: Optional[aiohttp.ClientSession] = None,
):
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
    url = (
        f"https://api.cnyes.com/media/api/v1/newslist/category/{market}?"
        f"startAt={str(todayStartSec)}&endAt={str(todayEndSec)}&limit=30&page=1"
    )

    # generate header
    headers = {
        'User-Agent': ("Mozilla/5.0 "
                       "(Macintosh; Intel Mac OS X 10_10_1) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/39.0.2171.95 Safari/537.36"),
        'Content-Type': 'application/json'
    }

    async def fetchJson(active_session: aiohttp.ClientSession, url: str):
        async with active_session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15, sock_connect=2),
        ) as result:
            text = await result.text(encoding='utf-8')
            return json.loads(text)

    closeSession = session is None
    if closeSession:
        session = aiohttp.ClientSession()

    try:
        # get meta data form CNYES json response
        jsdata = await fetchJson(session, url)

        # iterate all json pages
        dataCount = 0
        data = []
        lastPage = jsdata['items']['last_page']
        for page in range(lastPage):
            # get real all news from CNYES json response
            url = url.split("page=")[0] + "page=" + str(page+1)
            jsdata = await fetchJson(session, url)

            # iterate all news
            length = int(jsdata['items']['to']) - \
                int(jsdata['items']['from']) + 1
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
    finally:
        if closeSession:
            await session.close()

    # result = {}
    # result['data_count'] = len(data)
    # result['data'] = data
    return data


async def updateDailyNewsCnyesAsync(datetimeIn: datetime = datetime.today()):
    """
    @Description:
        更新每日鉅亨網新聞\n
        Update all daily news related to tw stock market
        from cnyes to stocker server\n
    @Param:
        datetimeIn => datetime.datetime (default: today)
    @Return:
        N/A
    """
    pushNewsMessge("CNYES crawler start")
    try:
        marketList = ["tw", "us"]

        async def updateMarketNews(
            market: str,
            session: aiohttp.ClientSession,
        ):
            news = await crawlNewsCnyes(datetimeIn, market, session=session)
            await updateNewsToServer(news, session=session)

        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[
                updateMarketNews(market, session)
                for market in marketList
            ])
    except Exception as ex:
        pushNewsMessge(f"CNYES crawler work error: {ex}")
    pushNewsMessge("CNYES crawler done")


def updateDailyNewsCnyes(datetimeIn: datetime = datetime.today()):
    """
    @Description:
        更新每日鉅亨網新聞\n
        Update all daily news related to tw stock market
        from cnyes to stocker server\n
    @Param:
        datetimeIn => datetime.datetime (default: today)
    @Return:
        N/A
    """
    asyncio.run(updateDailyNewsCnyesAsync(datetimeIn))
