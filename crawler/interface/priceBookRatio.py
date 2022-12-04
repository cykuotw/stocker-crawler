import requests
import json

from crawler.core.priceBookRatio import crawlSiiPeRatioAnalysis, crawlOtcPeRatioAnalysis
from crawler.interface.util import stockerUrl


def updatePeRatioAnalysis(stock_id, pe_ratio_data):
    dailyInfoApi = "{}/daily_information/{}".format(stockerUrl, stock_id)
    res = requests.post(dailyInfoApi, data=json.dumps(pe_ratio_data))


def handleDailyPeRatioAnalysis(date_time):
    pe_ratio_data = []

    pe_ratio_data += crawlSiiPeRatioAnalysis(date_time)
    pe_ratio_data += crawlOtcPeRatioAnalysis(date_time)

    for i in range(len(pe_ratio_data)):
        updatePeRatioAnalysis(pe_ratio_data[i]['stock_id'], pe_ratio_data[i])


if __name__ == '__main__':
    handleDailyPeRatioAnalysis()
