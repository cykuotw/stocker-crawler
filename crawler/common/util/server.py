import json

import aiohttp
import requests

from crawler.common.notifier import pushNewsMessge
from crawler.common.util.config import getStockerConfig


def getStockNoBasicInfo(startWith: int = 0) -> list:
    """
    @Description:
        從伺服器索取基本資料表中的有效股號\n
        Query exist stock id in basic information stocker server\n
    @Param:
        startWith: int (stock id prefix, 1 to 0, default 0 means get all)
    @Return:
        json 
    """
    if startWith < 0 or startWith > 9:
        return []

    stockerConfig = getStockerConfig()
    stockerURL = stockerConfig.get('STOCKER_URL')
    stockerBearerToken = stockerConfig.get('STOCKER_BEARER_TOKEN')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {stockerBearerToken}",
    }

    url = f"{stockerURL}/stock_number"
    if startWith != 0:
        url = f"{stockerURL}/stock_number?stock_number_start_with={startWith}"
    res = requests.get(
        url,
        headers=headers,
        timeout=10
    )
    ids = None

    try:
        ids = json.loads(res.text)
    except json.decoder.JSONDecodeError:
        return []

    return ids


async def updateNewsToServer(
    data: list = None,
    session: aiohttp.ClientSession = None,
):
    """
    @Description:
        推送當日新聞至Stocker伺服器\n
        Update daily news stocker server\n
    @Param:
        data => list of dict (default: None)
    @Return:
        N/A
    """
    if data is None or len(data) == 0:
        return

    stockerConfig = getStockerConfig()
    stockerURL = stockerConfig.get('STOCKER_URL')
    stockerBearerToken = stockerConfig.get('STOCKER_BEARER_TOKEN')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {stockerBearerToken}",
    }

    async def postNews(active_session: aiohttp.ClientSession):
        newsApi = f"{stockerURL}/feed"
        for _, d in enumerate(data):
            try:
                async with active_session.post(
                    newsApi,
                    json=d,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as res:
                    await res.read()
            except Exception as ex:
                pushNewsMessge(f"stocker server error: {ex}")

    if session is None:
        async with aiohttp.ClientSession() as active_session:
            await postNews(active_session)
    else:
        await postNews(session)
