import json

import requests
from crawler.core.basicInfo import crawlBasicInformation, crawlDelistedCompany
from crawler.interface.util import stockerUrl, transformHeaderNoun


def getBasicInfo(dataType='sii'):
    # dataType: otc, sii, rotc, pub
    while(True):
        try:
            data = crawlBasicInformation(dataType)
            break
        except Exception as ex:
            print(ex.__class__.__name__, end=" ")
            print("catched. Retrying.")
            continue

    data = transformHeaderNoun(data, 'basic_information')

    for i in range(len(data)):
        dataPayload = json.loads(
            data.iloc[i].to_json(force_ascii=False))
        dataPayload['exchangeType'] = dataType
        url = "{}/basic_information/{}".format(stockerUrl, dataPayload['id'])
        requests.post(url, data=json.dumps(dataPayload))

def getSummaryStockNoServerExist(
        westernYearIn=2019, seasonIn=2, reportType='balance_sheet'):
    stockNumUrl = "{}/stock_number".format(stockerUrl)
    payload = {}
    payload['year'] = westernYearIn
    payload['season'] = seasonIn
    payload['reportType'] = reportType
    print("exist " + reportType + " " +
          str(westernYearIn) + "Q" + str(seasonIn), end='...')
    res = requests.post(stockNumUrl, data=json.dumps(payload))
    print("done.")
    return json.loads(res.text)

def getStockNoBasicInfo():
    url = "{}/stock_number".format(stockerUrl)
    res = requests.get(url)
    return json.loads(res.text)

def getFinStatFromServer(stock_id, westernYear, season,
                        reportTypes='income_sheet'):
    finStatApi = "{url}/{reportType}/{stockId}?mode=single&year={year}&season={season}"\
    .format(url=stockerUrl, reportType=reportTypes, stockId=stock_id,
            year=westernYear, season=season)

    data = requests.get(finStatApi)
    if data.status_code == 404:
        return None
    else:
        return data.json()

def updateDelistedCompany():
    companyTypes = ['sii', 'otc']
    dataPayload = {}
    dataPayload['exchangeType'] = 'delist'
    for companyType in companyTypes:
        data = crawlDelistedCompany(companyType)
        for d in data:
            serverBasicInfoApi = "{}/basic_information/{}".format(stockerUrl, d)
            requests.patch(
                serverBasicInfoApi,
                data=json.dumps(dataPayload))
