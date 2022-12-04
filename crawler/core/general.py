# coding=utf-8
from io import StringIO
import re
import json

import pandas as pd
import requests

def crawlSiiDailyPrice(dateTime):
    """
    @Description:
        爬取上市每日股價\n
        Crawl daily stock price of sii/otc
    @Param:
        datetime => datetime.datetime
    @Return:
        dataFrame in dict (access with "sii", "otc")
    """
    dateSii = dateTime.strftime("%Y%m%d")
    # dateSii = '"' + "20190909" + '"'
    urlSii = "https://www.twse.com.tw/exchangeReport/"\
        + "MI_INDEX?response=html&date="\
        + dateSii + "&type=ALLBUT0999"

    reqSii = requests.get(urlSii)
    reqSii.encoding = 'utf-8'
    try:
        resultSii = pd.read_html(StringIO(reqSii.text))
        resultSii = resultSii[8]
        resultSii.columns = resultSii.columns.droplevel([0, 1])
    except ValueError as ve:
        if ve.args[0] == "No tables found":
            resultSii = None
        else:
            return ve
    else:
        return resultSii


def crawlOtcDailyPrice(dateTime):
    dateOtc = str(dateTime.year-1911) + dateTime.strftime("/%m/%d")
    urlOtc = "https://www.tpex.org.tw/web/stock/aftertrading/"\
        + "daily_close_quotes/stk_quote_result.php?l=zh-tw"\
        + "&d=" + dateOtc + "&s=0,asc,0"
    reqOtc = requests.get(urlOtc)
    reqOtc.encoding = 'utf-8'
    try:
        resultOtc = json.loads(reqOtc.text)["aaData"]
        resultOtc = filter(lambda data: len(data[0])==4, resultOtc)
    except ValueError as ve:
        print(ve)
        if ve.args[0] == "No tables found":
            resultOtc = None
        else:
            raise ve
    except Exception as ex:
        raise ex
    else:
        return list(resultOtc)


def crawlShareholderCount(companyID, datetime):
    """
    @Description:
        爬取千張持股股東人數，通常在週五\n
        Crawl shareholder count
    @Param:
        companyID => int\n
        datetime => datetime.datetime
    @Return:
        Dataframe (shareholder count)
    """
    coID = str(companyID)
    date = datetime.strftime("%Y%m%d")

    url = "https://www.tdcc.com.tw/smWeb/QryStockAjax.do"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "scaDates": date,
        "scaDate": date,
        "SqlMethod": "StockNo",
        "StockNo": coID,
        "REQ_OPR": "SELECT",
        "clkStockNo": coID
    }

    print('crawling shareholderCount')
    req = requests.post(url, headers)
    req.encoding = 'big5'
    print('crawler complete.')

    print('parsing data')
    html_df = pd.read_html(StringIO(req.text))
    result = html_df[6]
    print('parse complete.')

    return result



