import json

import requests

from crawler.core.derivatives import crawlStockFuture, crawlVolatility
from crawler.interface.util import stockerUrl
from notifier.discord import pushDiscordVolatility


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
                dataPayload["stock_option"] = isinstance(
                    row["是否為股票選擇權標的"], str)
            elif row["標準型證券股數"] == 100:
                dataPayload["small_stock_future"] = isinstance(
                    row["是否為股票期貨標的"], str)

            dataPayload["stock_id"] = row["證券代號"]
            print(dataPayload)
            res = requests.post(
                "{}/{}".format(
                    serverStockCommodityApi, dataPayload['stock_id']),
                data=json.dumps(dataPayload))


def updateDailyVolatility() -> None:
    data = crawlVolatility()

    message = "**" + data['商品'] + "**\n\t"
    message += "成交價: " + data['成交價'] + "\t"
    message += "漲跌: " + data['漲跌'] + "\t"
    message += "震幅: " + data['震幅'] + "\n\t"
    message += "**點數差: " + data['點數差'] + "**\t"
    message += "最高: " + data['最高'] + "\t"
    message += "最低: " + data['最低']

    pushDiscordVolatility("每日台指波動", message)
