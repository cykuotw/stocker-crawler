import json

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

    stockerURL = getStockerConfig()['STOCKER_URL']

    url = f"{stockerURL}/stock_number"
    if startWith != 0:
        url = f"{stockerURL}/stock_number?stock_number_start_with={startWith}"
    res = requests.get(url, timeout=10)
    ids = None

    try:
        ids = json.loads(res.text)
    except json.decoder.JSONDecodeError:
        return []

    return ids


def updateNewsToServer(data: list = None):
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

    stockerURL = getStockerConfig()['STOCKER_URL']
    newsApi = f"{stockerURL}/feed"
    for _, d in enumerate(data):
        try:
            requests.post(newsApi,
                          data=json.dumps(d),
                          timeout=10)
        except Exception as ex:
            pushNewsMessge(f"stocker server error: {ex}")
