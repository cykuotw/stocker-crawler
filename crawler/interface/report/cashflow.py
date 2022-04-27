import json
import random
import time

import requests
from crawler.core.basicInfo import crawlSummaryStockNoFromTWSE
from crawler.core.report import crawlCashFlow
from crawler.interface.basicInfo import (getStockNoBasicInfo,
                                         getSummaryStockNoServerExist)
from crawler.interface.util import (SLEEP_TIME, companyTypes, logger,
                                    stockerUrl, transformHeaderNoun)


def getCashFlow(
        companyID=2330, westernYearIn=2019, seasonIn=2):
    try:
        data = crawlCashFlow(companyID, westernYearIn, seasonIn)
    except Exception as e:
        return {"stock_id": companyID, "status": e.args[0]}

    data = transformHeaderNoun(data, "cashflow")
    dataPayload = {}
    with open('settings/data_key_select/cashflow_key_select.txt',
            encoding='utf-8') as cashflow_key_select:
        cashflowKeySel = set(
            line.strip() for line in cashflow_key_select)

    for key in cashflowKeySel:
        try:
            if key in data.index:
                dataPayload[key] = int(data.loc[key][0])
            else:
                dataPayload[key] = None
        except KeyError as ke:
            if ke.args[0] == 0:
                dataPayload[key] = int(data.loc[key].iloc[0])
        except Exception as ex:
            return {"stock_id": companyID, "status": ex.__class__.__name__}
            # TODO: write into log file

    dataPayload['year'] = westernYearIn
    dataPayload['season'] = str(seasonIn)

    cashflowApi = "{}/cash_flow/{}".format(stockerUrl, companyID)

    idx = 0
    while(True):
        try:
            res = requests.post(cashflowApi, data=json.dumps(dataPayload))
            break
        except Exception as ex:
            if idx == 5:
                print("Retry fail exceed %d times, abort." % (idx+1))
                res = ""
                break
            else:
                print(ex.__class__.__name__)
                time.sleep(8)

    print(res, end=" ")
    return {"stock_id": companyID, "status": "ok"}


def updateCashFlow(westernYearIn=2019, season=1):
    existStockNo = getSummaryStockNoServerExist(
        westernYearIn, season, 'cashflow')
    validStockNo = getStockNoBasicInfo()
    print("\t" + str(len(existStockNo)) + " existing stocks")

    crawlList = []
    for companyType in companyTypes:
        targetStockNo = crawlSummaryStockNoFromTWSE(
            'balance_sheet', companyType, westernYearIn, season)
        if len(targetStockNo) == 0:
            continue
        if len(existStockNo) != 0:
            for no in targetStockNo:
                if str(no) not in existStockNo and\
                   str(no) in validStockNo:
                    crawlList.append(no)
        else:
            crawlList.extend(targetStockNo)

    total = len(crawlList)
    print("\t" + str(total) + " stocks to update")
    exceptList = []

    for idx, stock in enumerate(crawlList):
        print("(" + str(idx) + "/" + str(total) + ")" + str(stock), end=' ')
        crawlerResult = getCashFlow(stock, westernYearIn, season)
        print(crawlerResult['status'])
        if crawlerResult["status"] == "IndexError":
            time.sleep(90)
        if crawlerResult["status"] != "ok":
            exceptList.append({
                "stock_id": crawlerResult["stock_id"],
                "retry_times": 0
            })
        time.sleep(SLEEP_TIME + random.randrange(0, 4))

    while(len(exceptList)):
        # print("(len=" + str(len(exceptList)) + ")", end=" ")
        print("Retry " + str(exceptList[0]["stock_id"])
              + " " + str(exceptList[0]["retry_times"]), end=" ")
        reCrawler = getCashFlow(
            exceptList[0]["stock_id"], westernYearIn, season)
        if reCrawler["status"] == "ok":
            print("ok")
            del exceptList[0]
        elif exceptList[0]["retry_times"] == 2:
            print("cancel stock_id: %s, retry over 3 times."
                  % reCrawler["stock_id"])
            logger.error("cancel stock_id: %s in %s-%s, retry exceeded."
                         % (reCrawler["stock_id"], westernYearIn, season))
            del exceptList[0]
        else:
            print("retry")
            tmpStock = exceptList.pop(0)
            tmpStock["retry_times"] = tmpStock["retry_times"]+1
            exceptList.append(tmpStock)
        time.sleep(SLEEP_TIME + random.randrange(0, 4))
