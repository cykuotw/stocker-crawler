import json
import gc
from datetime import datetime

import requests
from crawler.core.general import crawlSiiDailyPrice, crawlOtcDailyPrice
from crawler.interface.util import stockerUrl
from notifier.util import pushSlackMessage


def updateSiiDailyPrice(datetimeIn=datetime.now()):
    try:
        data = crawlSiiDailyPrice(datetimeIn)
    except Exception as e:
        raise e
    
    if data is None or data.shape[0] < 5:
        del data
        gc.collect()
        return

    stockNumsApi = "{}/stock_number?type={}".format(stockerUrl, 'sii')
    stockIDs = json.loads(requests.get(stockNumsApi).text)

    for id in stockIDs:
        try:
            dataStock = data.loc[data['證券代號'] == id]
            print(dataStock)
        except Exception as ex:
            print(ex)
            break

        dailyInfoApi = "{}/daily_information/{}".format(stockerUrl, id)
        dataPayload = {}

        try:
            dataPayload['本日收盤價'] = float(dataStock['收盤價'].iloc[0])
            if dataStock['漲跌(+/-)'].iloc[0] == '除息':
                dataPayload['本日漲跌'] = 0
            elif dataStock['漲跌(+/-)'].iloc[0] == '-':
                dataPayload['本日漲跌'] = float(dataStock['漲跌價差'].iloc[0] * -1)
            else:
                dataPayload['本日漲跌'] = float(dataStock['漲跌價差'].iloc[0])
        except ValueError as ve:
            print("%s get into ValueError with %s"% (id, ve))
        except IndexError as ie:
            print("%s get into IndexError with %s"% (id, ie))
        except Exception as ex:
            print("{} {}: {}".format(id, dataStock))
        else:
            try:
                requests.post(dailyInfoApi, data=json.dumps(dataPayload))
            except Exception as ex:
                print("ERROR: {}".format(ex))


def updateOtcDailyPrice(datetimeIn=datetime.now()):
    try:
        data = crawlOtcDailyPrice(datetimeIn)
    except Exception as e:
        raise e

    if data is None:
        del data
        gc.collect()
        return

    for stock_price in data:
        dailyInfoApi = "{}/daily_information/{}".format(stockerUrl, stock_price[0])
        dataPayload = {}

        try:
            if stock_price[2].strip() != '---':
                dataPayload['本日收盤價'] = float(stock_price[2])
            
            if stock_price[3].strip() == '---':
                dataPayload['本日漲跌'] = 0
            else:
                dataPayload['本日漲跌'] = float(stock_price[3])
        except ValueError as ve:
            print("%s get into ValueError with %s"% (id, ve))
        except IndexError as ie:
            print("%s get into IndexError with %s"% (id, ie))
        except Exception as ex:
            print("{} {}: {}".format(id, dataStock, ex))
        else:
            try:
                res = requests.post(dailyInfoApi, data=json.dumps(dataPayload))
            except Exception as ex:
                print("ERROR: {}".format(ex))


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
    curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    pushSlackMessage("Stocker股價更新", '{} crawler work start.'.format(curTime))
    
    try:
        updateSiiDailyPrice(datetimeIn)
        updateOtcDailyPrice(datetimeIn)
    except Exception as ex:
        pushSlackMessage("Stocker股價更新", f'股價更新錯誤: {ex}')    
    finally:
        curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        pushSlackMessage("Stocker股價更新", '{} crawler work done.'.format(curTime))

