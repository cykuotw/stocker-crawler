import json
import random
import time
from datetime import date, datetime

import requests

from notifier.util import pushSlackMessage
from crawler.interface.util import SLEEP_TIME, companyTypes, stockerUrl, webhook
from crawler.interface.basicInfo import updateDelistedCompany, getBasicInfo
from crawler.interface.general import updateDailyPrice
from crawler.interface.derivatives import updateStockCommodity
from crawler.interface.report.monthlyRevenue import getMonthlyRevenue
from crawler.interface.report.incomeSheet import updateIncomeSheet
from crawler.interface.news import updateDailyNews

def dailyRoutineWork():
    # 差財報三表, shareholder可以禮拜六抓
    curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    pushSlackMessage("Stocker日常工作", '{} crawler work start.'.format(curTime))

    try:
        updateDelistedCompany()
        for type in companyTypes:
            getBasicInfo(type)
            time.sleep(SLEEP_TIME + random.randrange(0, 4))
        updateStockCommodity()

        updateDailyNews()

        if date.today().weekday() in [0,1,2,3,4]:
            updateDailyPrice()

        now = datetime.now()
        if now.month == 1:
            getMonthlyRevenue(now.year-1, 12)
        else:
            getMonthlyRevenue(now.year, now.month-1)

        if 1 <= now.month <= 4:
            updateIncomeSheet(now.year-1, 4)
        if 4 <= now.month <= 5:
            updateIncomeSheet(now.year, 1)
        if 7 <= now.month <= 9:
            updateIncomeSheet(now.year, 2)
        if 10 <= now.month <= 11:
            updateIncomeSheet(now.year, 3)

        if datetime.now().hour >= 21:
            url = "{}/{}?{}"
            queryString = 'option={}&webhook={}'

            for group in ['stocker', 'gugugu']:
                requests.get(
                    url.format(
                        stockerUrl,
                        'screener',
                        queryString.format(
                            'bullish', webhook[group])
                    )
                )

            for filter in ['bearish', '月營收半年新高', '月營收半年新低', '財報偏多選股']:
                requests.get(
                    url.format(
                        stockerUrl,
                        'screener',
                        queryString.format(
                            filter, webhook['stocker'])
                    )
                )      
            
            if (datetime.now().month in (1, 4, 7, 10)):
                requests.get(
                    url.format(
                        stockerUrl,
                        'screener',
                        queryString.format(
                            '月營收篩選', webhook['stocker'])
                    )
                )
    except Exception as e:
        curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        pushSlackMessage("Stocker日常工作", '{} work error: {}'.format(curTime, e))
    finally:
        curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        pushSlackMessage("Stocker日常工作", '{} crawler work done.'.format(curTime))


def crawlHistoryData():
    for type in companyTypes:
        getBasicInfo(type)
    updateDelistedCompany()
    updateStockCommodity()

    if date.today().weekday() in [0,1,2,3,4]:
        updateDailyPrice()

    now = datetime.now()
    for month in range(now.month-1, 1, -1):
        getMonthlyRevenue(now.year, month)

    for year in range(now.year-6, 2012, -1):
        for month in range(12, 0, -1):
            getMonthlyRevenue(year, month)

    for year in range(now.year-1, 2012, -1):
        for season in [1,2,3,4]:
            updateIncomeSheet(year, season)


if __name__ == '__main__':
    '''
    usage: get basic information
    '''
    # for type in companyTypes:
    #     getBasicInfo(type)

    '''
    usage: get monthly revenue
    # '''
    # for year in range(2019, 2012, -1):
    #     for i in range(12, 0, -1):
    #         getMonthlyRevenue(year, i)
    '''
    usage: update incomeSheet/BalanceSheet
    '''
    # years = [2019]
    # seasons = [1, 2, 3, 4]

    # for year in range(2017, 2012, -1):
    #     for season in seasons:
    #         updateIncomeSheet(year, season)

    #         # updateBalanceSheet(year, season)
    #         UpdateCashFlow(year, season)

    dailyRoutineWork()
    # crawlHistoryData()
