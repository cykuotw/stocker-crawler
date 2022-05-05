# coding=utf-8
import requests
import pandas as pd

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


