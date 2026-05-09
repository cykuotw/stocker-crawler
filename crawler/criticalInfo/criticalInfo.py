import asyncio
import json
import re
from datetime import datetime

import aiohttp
import pytz
from bs4 import BeautifulSoup

from crawler.common.notifier import (
    discord,
    pushCriticalInfoMessage,
    pushErrorMessage,
    telegram,
)
from crawler.common.util.config import getStockerConfig

with open('configs/critical_info_filter.json', encoding='utf-8') as criticalInfoReader:
    criticalInfo = json.loads(criticalInfoReader.read())


def parseCriticalInfoHtml(html: str, exchangeType: str) -> list:
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.findChildren('table')
    if len(table) == 1:
        return []
    rows = table[1].findChildren('tr')

    result = []
    for i in range(1, len(rows)):
        rowElements = rows[i].findChildren('td')
        formVar = rowElements[5].findChildren(
            'input')[0]['onclick'].split("'")
        formStockNum = re.sub('[a-zA-Z]', '', formVar[7])
        formDate = formVar[5]
        formTime = formVar[3]
        seqNum = formVar[1]
        title = rowElements[4].getText().replace('\r\n', '')

        i = formStockNum[0:2]
        urlLink = (
            "https://mopsov.twse.com.tw/mops/web/t05st02?step=1&off=1&firstin=1&"
            f"TYPEK={exchangeType}&"
            f"i={i}&"
            f"h{i}0={rowElements[1].getText()}&"
            f"h{i}1={formStockNum}&"
            f"h{i}2={formDate}&"
            f"h{i}3={formTime}&"
            f"h{i}4={title}&"
            f"h{i}5={seqNum}&pgname=t05st02"
        )

        result.append({
            '股號': rowElements[0].getText(),
            '公司名稱': rowElements[1].getText(),
            '發言日期': rowElements[2].getText(),
            '發言時間': rowElements[3].getText(),
            '主旨': title,
            'link': urlLink,
            'type': exchangeType
        })

    return result


async def crawlCriticalInfo(session: aiohttp.ClientSession = None):
    """
    @Description:
        Crawl everyday critical infomation
    @Parameter:
        N/A
    @Return:
        list (critical information in json)
    """
    # exchangeTypes = ['sii', 'otc', 'rotc', 'pub']
    exchangeTypes = ['sii', 'otc', 'rotc']

    async def crawlExchangeType(
        activeSession: aiohttp.ClientSession,
        exchangeType: str,
    ):
        async with activeSession.post(
            'https://mopsov.twse.com.tw/mops/web/ajax_t05sr01_1',
            data={
                'encodeURIComponent': 1,
                'TYPEK': exchangeType,
                'step': 0
            },
            timeout=aiohttp.ClientTimeout(total=10),
        ) as res:
            html = await res.text()

        return await asyncio.to_thread(
            parseCriticalInfoHtml,
            html,
            exchangeType,
        )

    closeSession = session is None
    if closeSession:
        session = aiohttp.ClientSession()

    try:
        exchangeResults = await asyncio.gather(*[
            crawlExchangeType(session, exchangeType)
            for exchangeType in exchangeTypes
        ])
    finally:
        if closeSession:
            await session.close()

    result = []
    for exchangeResult in exchangeResults:
        result.extend(exchangeResult)

    return result


async def updateCriticalInfoAsync() -> None:
    """
    @Description:
        Update everyday critical infomation
    @Parameter:
        N/A
    @Return:
        N/A
    """
    pushCriticalInfoMessage("crawler work start.")

    data = []
    try:
        async with aiohttp.ClientSession() as session:
            data = await crawlCriticalInfo(session=session)
    except Exception as e:
        pushErrorMessage(f"crawler error: {e}", crawler="criticalInfo")
        pushCriticalInfoMessage("crawler work done.")
        return

    # filter keyword
    criteriaPos = criticalInfo["criteria_pos"]
    criteriaNeg = criticalInfo["criteria_neg"]

    for index, info in enumerate(data):
        info['tags'] = []
        info['negativeTag'] = False
        for crp in criteriaPos:
            if info['主旨'].find(crp) != -1:
                info['tags'].append(crp)
        for crn in criteriaNeg:
            if info['主旨'].find(crn) != -1:
                info['negativeTag'] = True
                break

    if len(data) == 0:
        pushCriticalInfoMessage("no data")
        pushCriticalInfoMessage("crawler work done.")
        return

    # post stocker announcement
    stockerConfig = getStockerConfig()
    stockerURL = stockerConfig.get('STOCKER_URL')
    stockerBearerToken = stockerConfig.get('STOCKER_BEARER_TOKEN')

    url = f"{stockerURL}/feed"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {stockerBearerToken}",
    }

    tw = pytz.timezone('Asia/Taipei')
    failed_feeds = []

    async def postFeed(session: aiohttp.ClientSession, info: dict):
        dateArr = info['發言日期'].split('/')
        dateArr[0] = str(int(dateArr[0])+1911)

        dateTime = '-'.join(dateArr) + ' ' + info['發言時間']
        dateTime = datetime.strptime(dateTime, '%Y-%m-%d %H:%M:%S')
        dateTime = tw.localize(dateTime)
        dateTime = dateTime.astimezone(tz=pytz.UTC).isoformat()

        infoJson = {
            'feedType': "announcement",
            'releaseTime': dateTime,
            'title': info['主旨'],
            'link': info['link'],
            'tags': info['tags'],
            'stocks': [info['股號']],
            'source': 'mops'
        }

        try:
            async with session.post(
                url,
                json=infoJson,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                responseText = await response.text()

                if not 200 <= response.status < 300:
                    failed_feeds.append({
                        'stock': infoJson['stocks'][0],
                        'title': infoJson['title'],
                        'status': response.status,
                        'message': responseText,
                    })
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"request error: {e}")
            failed_feeds.append({
                'stock': infoJson['stocks'][0],
                'title': infoJson['title'],
                'status': 'request-error',
                'message': str(e),
            })

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[
            postFeed(session, info)
            for info in data
        ])

    if failed_feeds:
        pushErrorMessage(
            "crawler post feed failed",
            crawler="criticalInfo",
            details=failed_feeds,
        )

    # push to discord everyday between 20:00 to 22:00
    if datetime.now(tw).hour < 20 or datetime.now(tw).hour > 22:
        pushCriticalInfoMessage("crawler work done.")
        return

    content = ""
    cnt = 0
    for index, info in enumerate(data):
        if info['negativeTag'] or len(info['tags']) == 0:
            continue

        content += f"**{info['股號']}**\t"
        # to unicode asterisk(*)
        content += f"**{re.sub('[*]', '＊', info['公司名稱'])}**\t"
        content += f"({info['發言日期']} "
        content += f"{toStringExchageType(info['type'])})\n"
        content += f"[{info['主旨']}]"
        content += "(%s)\n" % re.sub(r"[ ]", "%20",
                                     re.sub(r"[\(\)]+", "-", info['link']))

        cnt += 1

        if cnt == 5 or (index == len(data)-1 and cnt != 0):
            await asyncio.gather(
                asyncio.to_thread(discord.pushInfo, content=content),
                asyncio.to_thread(telegram.push, content),
            )
            content = ""
            cnt = 0

    pushCriticalInfoMessage("crawler work done.")


def updateCriticalInfo() -> None:
    """
    @Description:
        Update everyday critical infomation
    @Parameter:
        N/A
    @Return:
        N/A
    """
    asyncio.run(updateCriticalInfoAsync())


def toStringExchageType(exchangeType: str = 'sii') -> str:
    """
    @Description:
        Lookup table translate exchange type code into Manderin
    @Parameter:
        exchangeType: str
    @Return:
        ManderinExchangeType: str
    """
    if exchangeType == 'sii':
        tp = "上市"
    elif exchangeType == 'otc':
        tp = "上櫃"
    elif exchangeType == 'rotc':
        tp = "興櫃"
    elif exchangeType == 'pub':
        tp = "公開發行"
    else:
        tp = ""

    return tp
