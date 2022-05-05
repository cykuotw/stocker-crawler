# coding=utf-8
from io import StringIO

import pandas as pd
import requests

def crawlDailyPrice(dateTime):
    """
    @Description:
        爬取上市/上櫃每日股價\n
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

    dateOtc = str(dateTime.year-1911) + dateTime.strftime("/%m/%d")
    # dateOtc = str(datetime.year-1911) + "/"\
    #     + str(datetime.month).zfill(2) + "/"\
    #     + str(datetime.day).zfill(2)
    # dateOtc = "108/09/09"
    urlOtc = "https://www.tpex.org.tw/web/stock/aftertrading/"\
        + "daily_close_quotes/stk_quote_result.php?l=zh-tw"\
        + "&o=htm&d=" + dateOtc + "&s=0,asc,0"

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


    reqOtc = requests.get(urlOtc)
    reqOtc.encoding = 'utf-8'
    try:
        resultOtc = pd.read_html(StringIO(reqOtc.text))
        resultOtc = resultOtc[0]
        resultOtc.columns = resultOtc.columns.droplevel(0)
    except ValueError as ve:
        if ve.args[0] == "No tables found":
            resultOtc = None
        else:
            return ve

    results = {'sii': resultSii, 'otc': resultOtc}

    return results


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



