import json
from datetime import datetime

import requests
from crawler.core.general import crawlDailyPrice
from crawler.interface.util import stockerUrl


def updateDailyPrice(datetimeIn=datetime.now()):
    """
    @Description:
        更新所有上市/上櫃公司每日股價\n
        Update daily stock price of all sii/otc companies to
        stocker server\n
    @Param:
        datetimeIn => datetime.datetime
    @Return:
        N/A
    """

    data = crawlDailyPrice(datetimeIn)
    stockTypes = ['sii', 'otc']
    for stockType in stockTypes:
        if data[stockType] is None or data[stockType].shape[0] < 5:
            continue
        stockNumsApi = "{}/stock_number?type={}".format(stockerUrl, stockType)
        stockIDs = json.loads(requests.get(stockNumsApi).text)

        for id in stockIDs:
            if stockType == 'sii':
                colCol = '證券代號'
                priceCol = '收盤價'
                priceDiffCol = '漲跌價差'
                priceDiffSignCol = '漲跌(+/-)'
            elif stockType == 'otc':
                colCol = '代號'
                priceCol = '收盤'
                priceDiffCol = '漲跌'

            try:
                dataStock = data[stockType].loc[
                    data[stockType][colCol] == id]
            except:
                break

            dailyInfoApi = "{}/daily_information/{}".format(stockerUrl, id)
            dataPayload = {}

            try:
                dataPayload['本日收盤價'] = float(dataStock[priceCol].iloc[0])
                # otc have no priceDiffSignCol column
                if stockType == 'sii':
                    if dataStock[priceDiffSignCol].iloc[0] == '除息':
                        dataPayload['本日漲跌'] = 0
                    elif dataStock[priceDiffSignCol].iloc[0] == '-':
                        dataPayload['本日漲跌'] = float(dataStock[priceDiffCol].iloc[0] * -1)
                    else:
                        dataPayload['本日漲跌'] = float(dataStock[priceDiffCol].iloc[0])
                else:
                    dataPayload['本日漲跌'] = float(dataStock[priceDiffCol].iloc[0])
            except ValueError as ve:
                print("%s get into ValueError with %s"% (id, ve))
            except IndexError as ie:
                print("%s get into IndexError with %s"% (id, ie))
            except Exception as ex:
                print(ex)
                print("{}: {}".format(id, dataStock))
            else:
                try:
                    requests.post(dailyInfoApi, data=json.dumps(dataPayload))
                except Exception as ex:
                    print("ERROR: {}".format(ex))
