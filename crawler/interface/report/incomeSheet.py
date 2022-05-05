import json
import math
import random
import time

import pandas as pd
import requests
from crawler.core.basicInfo import crawlSummaryStockNoFromTWSE
from crawler.core.report import crawlIncomeSheet
from crawler.interface.basicInfo import (getFinStatFromServer,
                                         getStockNoBasicInfo,
                                         getSummaryStockNoServerExist)
from crawler.interface.util import (SLEEP_TIME, companyTypes,
                                    incomeSheetKeySel, stockerUrl,
                                    transformHeaderNoun)


def getIncomeSheet(companyID=1101, westernYearIn=2019, seasonIn=1):
    """
    @Description:
        爬取及更新個別上市/上櫃公司綜合損益表\n
        Crawl and update quarterly income sheet of single sii/otc company
    @Param:
        companyID => int (stock id)
        westernYearIn => int (western year)
        seasonIn => int (1, 2, 3, 4)
    @Return:
        dict (stock id & status)
    """      
    try:
        data = crawlIncomeSheet(companyID, westernYearIn, seasonIn)
    except ConnectionError as ce:
        return {"stock_id": companyID, "status": ce.args[0]}
    except IndexError:
        return {"stock_id": companyID, "status": 'IndexError'}
    except Exception as e:
        return {"stock_id": companyID, "status": e.args[0]}

    data = transformHeaderNoun(data, 'income_sheet')

    dataPayload = {}
    # Key-select is used to select the data to be saved.


    # ratioIgnore is used to ignore the proportion of data
    # that does not need to be stored in the database.
    ratioIgnore = set(["營業收入合計", "營業成本合計", "營業外收入及支出合計"])

    # if the key is in key_select file, then put data into datapayload
    # if key need to store ration,
    # key+'率' becomes the new key value for store
    for key in incomeSheetKeySel:
        try:
            if key in data.index:
                if key == "母公司業主淨利":
                    if isinstance(data.loc[key], pd.DataFrame):
                        dataPayload[key] = data.loc[key].iloc[0][0]
                    else:
                        dataPayload[key] = data.loc[key][0]
                else:
                    dataPayload[key] = data.loc[key][0]
                    if not math.isnan(data.loc[key][1])\
                            and key not in ratioIgnore:
                        dataPayload[key+'率'] = round(data.loc[key][1], 2)
            else:
                dataPayload[key] = None
        except Exception as ex:
            print(key)
            print(ex)

    if "母公司業主淨利" not in dataPayload or dataPayload["母公司業主淨利"] is None:
        if "母公司業主淨利" not in data:
            dataPayload["母公司業主淨利"] = dataPayload["本期淨利"]
        elif len(data.loc["母公司業主淨利"]) >= 2:
            dataPayload["母公司業主淨利"] = data.loc["母公司業主淨利"].iloc[0][0]

    # The fourth quarter financial statements are annual reports
    # So we must use the data from the first three quarters to subtract them
    # to get the fourth quarter single-quarter financial report.
    if seasonIn == 4:
        preSeasonsData = []
        for season in range(1, 4):
            preData = getFinStatFromServer(
                companyID, westernYearIn, season, 'income_sheet')
            if preData is not None:
                preSeasonsData.append(preData[0])

        for data in preSeasonsData:
            for key in incomeSheetKeySel:
                if dataPayload[key] is None:
                    continue
                elif data[key] is not None:
                    dataPayload[key] -= data[key]

        # Recalculate percentage of specific value
        for key in dataPayload.keys():
            if '率' in key:
                if dataPayload['營業收入合計'] == 0:
                    dataPayload[key] = 0
                elif dataPayload['營業收入合計'] is None:
                    dataPayload[key] = None
                else:
                    dataPayload[key] = round((dataPayload[
                        key.replace('率', '')]/dataPayload['營業收入合計'])*100, 2)

        basicInfoUrl = "{}/basic_information/{}".format(stockerUrl, companyID)

        basicInfo = requests.get(basicInfoUrl)

        if basicInfo.status_code != 404:
            basicInfoData = json.loads(basicInfo.text)
            if basicInfoData["已發行普通股數或TDR原發行股數"] != 0:
                dataPayload["基本每股盈餘"] = round(
                    dataPayload["母公司業主淨利"]*1000/
                    basicInfoData["已發行普通股數或TDR原發行股數"], 2)

    dataPayload['year'] = westernYearIn
    dataPayload['season'] = str(seasonIn)

    incomeSheetApi = "{}/income_sheet/{}".format(stockerUrl, companyID)
    res = requests.post(incomeSheetApi, data=json.dumps(dataPayload))

    if res.status_code == 201:
        return {"stock_id": companyID, "status": "ok"}
    else:
        return {"stock_id": companyID, "status": res.status_code}

def updateIncomeSheet(westernYearIn=2019, season=1):
    """
    @Description:
        更新所有上市/上櫃公司綜合損益表\n
        Update income sheet of all sii/otc companies to
        stocker server\n
        1. Get list should be updated
        2. Update income sheet of each company with getIncomeSheet
    @Param:
        westernYearIn => int (western year)
        seasonIn => int (1, 2, 3, 4)
    @Return:
        N/A
    """

    existStockNo = getSummaryStockNoServerExist(
        westernYearIn, season, 'income_sheet')
    validStockNo = getStockNoBasicInfo()

    crawlList = []
    for companyType in companyTypes:
        targetStockNo = crawlSummaryStockNoFromTWSE(
            'income_sheet', companyType, westernYearIn, season)
        if len(targetStockNo) == 0:
            continue
        if len(existStockNo) != 0:
            for no in targetStockNo:
                if str(no) not in existStockNo and\
                   str(no) in validStockNo:
                    crawlList.append(no)
        else:
            crawlList.extend(targetStockNo)
        time.sleep(SLEEP_TIME + random.randrange(0, 4))

    total = len(crawlList)
    exceptList = []

    for idx, stock in enumerate(crawlList):
        print("(" + str(idx) + "/" + str(total) + ")", end=' ')
        crawlerResult = getIncomeSheet(stock, westernYearIn, season)
        print(crawlerResult['stock_id'], crawlerResult['status'])
        if crawlerResult["status"] == 'IndexError':
            time.sleep(90)
        if crawlerResult["status"] != 'ok':
            exceptList.append({
                "stock_id": crawlerResult["stock_id"],
                "retry_times": 0
            })
        time.sleep(SLEEP_TIME + random.randrange(0, 4))

    while(len(exceptList)):
        reCrawler = getIncomeSheet(
            exceptList[0]["stock_id"], westernYearIn, season)
        if reCrawler["status"] == 'ok':
            del exceptList[0]
        elif exceptList[0]["retry_times"] == 2:
            print("cancel stock_id: %s, retry over 3 times."
                  % reCrawler["stock_id"])
            del exceptList[0]
        else:
            tmpStock = exceptList.pop(0)
            tmpStock["retry_times"] = tmpStock["retry_times"]+1
            exceptList.append(tmpStock)
        time.sleep(SLEEP_TIME + random.randrange(0, 4))

