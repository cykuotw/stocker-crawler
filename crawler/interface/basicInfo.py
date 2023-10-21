import json

import requests
from crawler.core.basicInfo import crawlBasicInformation, crawlDelistedCompany
from crawler.interface.util import stockerUrl, transformHeaderNoun


def getBasicInfo(dataType='sii'):
    """
    @Description:
        更新所有上市櫃公司基本資料\n
        Update all sii/otc basic information to stocker server\n
    @Param:
        dataType => string(sii, otc, rotc, pub)
    @Return:
        N/A
    """

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
        dataPayload['exchange_type'] = dataType
        url = "{}/basic_information/{}".format(stockerUrl, dataPayload['id'])
        requests.post(url, data=json.dumps(dataPayload))


def getSummaryStockNoServerExist(
        westernYearIn=2019, seasonIn=2, reportType='balance_sheet'):
    """
    @Description:
        從伺服器索取單季財務報表的有效股號\n
        Query exist stock id in finance report 
        (balance sheet/ income sheet, cashflow)
        from stocker server\n
    @Param:
        westernYearIn => int (western year)\n
        seasonIn => int (1, 2, 3, 4)\n
        reportType => string ('balance_sheet', 'income_sheet', 'cashflow')
    @Return:
        json 
    """

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
    """
    @Description:
        從伺服器索取基本資料表中的有效股號\n
        Query exist stock id in basic information stocker server\n
    @Param:
        N/A
    @Return:
        json 
    """

    url = "{}/stock_number".format(stockerUrl)
    res = requests.get(url)
    return json.loads(res.text)

def getFinStatFromServer(stock_id, westernYear, season,
                        reportTypes='income_sheet'):
    """
    @Description:
        從伺服器索取單季財務報表資料\n
        Query data of single quarter finance report 
        (balance sheet/ income sheet, cashflow)
        from stocker server\n
    @Param:
        stock_id => string\n
        westernYearIn => int (western year)\n
        seasonIn => int (1, 2, 3, 4)\n
        reportType => string ('balance_sheet', 'income_sheet', 'cashflow')
    @Return:
        json 
    """

    finStatApi = "{url}/{reportType}/{stockId}?mode=single&year={year}&season={season}"\
    .format(url=stockerUrl, reportType=reportTypes, stockId=stock_id,
            year=westernYear, season=season)

    data = requests.get(finStatApi)
    if data.status_code == 404:
        return None
    else:
        return data.json()

def updateDelistedCompany():
    """
    @Description:
        更新所有下市/櫃公司資料\n
        Update all delisted companies to stocker server
    @Param:
        N/A
    @Return:
        N/A
    """

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
