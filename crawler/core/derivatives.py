from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


def crawlStockFuture():
    """
    @Description:
        Crawl stock list with derivatives such as option and future
    @Parameter:
        N/A
    @Return:
        Dataframe (stock id, future exist, option exist, share represented)
    """
    data = requests.get("https://www.taifex.com.tw/cht/2/stockLists", verify=False)
    dfs = pd.read_html(data.text, converters={'證券代號': str})
    return dfs[1][["證券代號", "是否為股票期貨標的", "是否為股票選擇權標的", "標準型證券股數"]]


def crawlDailyIndexOptOI():
    """
    @Description:
        Crawl OI (open interest) of TWE index option
    @Parameter:
        N/A
    @Return:
        list (json with keys: 'date', 'contract', 'expireDate', 'strikePrice',
        'optType', 'openInterest')
    """

    res = requests.get('https://www.taifex.com.tw/cht/3/optDailyMarketReport')
    soup = BeautifulSoup(res.text, 'lxml')
    table = soup.findChildren('table', attrs={'class':'table_f'})
    rows = table[0].findChildren('tr')

    header = rows[0].findChildren('th')
    if len(header) != 19:
        return []

    result = [] 
    for i in range(1, len(rows)-1):
        rowElement = rows[i].findChildren('td')

        expiry = rowElement[1].getText()
        if i == 1:
            recentExpiry = expiry
        if expiry == recentExpiry:
            result.append({
                'date': str(datetime.now().date()),
                'contract': ''.join(e for e in rowElement[0].getText() if e.isalnum()),
                'expireDate': rowElement[1].getText(),
                'strikePrice': rowElement[2].getText(),
                'type': rowElement[3].getText(),
                'openInterest': rowElement[14].getText()
            })
        else:
            break
    
    return result
