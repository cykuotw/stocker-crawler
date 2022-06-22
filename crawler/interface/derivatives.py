import json
import requests
import math

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
                dataPayload["stock_future"] = isinstance(row["是否為股票期貨標的"], str)
                dataPayload["stock_option"] = isinstance(row["是否為股票選擇權標的"], str)
            elif row["標準型證券股數"] == 100:
                dataPayload["small_stock_future"] = isinstance(row["是否為股票期貨標的"], str)

            dataPayload["stock_id"] = row["證券代號"]
            print(dataPayload)
            res = requests.post(
                    "{}/{}".format(
                        serverStockCommodityApi, dataPayload['stock_id']),
                    data=json.dumps(dataPayload))
