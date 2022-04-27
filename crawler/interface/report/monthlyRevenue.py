import json

import requests
from crawler.core.report import crawlMonthlyRevenue
from crawler.interface.util import stockerUrl, transformHeaderNoun


def getMonthlyRevenue(westernYearIn=2013, monthIn=1):
    # year, month: start at 2013, 1
    data = crawlMonthlyRevenue(westernYearIn, monthIn)
    data = transformHeaderNoun(data, 'month_revenue')

    for i in range(len(data)):
        dataPayload = json.loads(data.iloc[i].to_json(force_ascii=False))
        dataPayload['year'] = westernYearIn
        dataPayload['month'] = str(monthIn)
        url = "{}/month_revenue/{}".format(stockerUrl, dataPayload['stock_id'])
        requests.post(url, data=json.dumps(dataPayload))
