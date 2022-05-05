import json

import requests
from crawler.core.derivatives import crawlStockFuture
from crawler.interface.util import stockerUrl


def updateStockCommodity():
    """
    @Description:
        更新所有上市櫃公司每日股價\n
        Update all sii/otc daily price to stocker server\n
    @Param:
        N/A
    @Return:
        N/A
    """

    data = crawlStockFuture()
    serverStockCommodityApi = "{}/stock_commodity".format(stockerUrl)
    for index, row in data.iterrows():
        dataPayload = {}
        if row["標準型證券股數"] in [2000, 100]:
            if row["標準型證券股數"] == 2000:
                dataPayload["stock_future"] = row["是否為股票期貨標的"]==u"\u25CF"
                dataPayload["stock_option"] = row["是否為股票選擇權標的"]==u"\u25CF"
            elif row["標準型證券股數"] == 100:
                dataPayload["small_stock_future"] = row["是否為股票期貨標的"]==u"\u25CF"

            dataPayload["stock_id"] = row["證券代號"]
            res = requests.post(
                    "{}/{}".format(
                        serverStockCommodityApi, dataPayload['stock_id']),
                    data=json.dumps(dataPayload))
