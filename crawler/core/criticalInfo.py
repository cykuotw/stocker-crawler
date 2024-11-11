# coding=utf-8
import re
from random import randint

import requests
from bs4 import BeautifulSoup


def crawlDataUseBs4():
    """
    @Description:
        Crawl critical infomation of the day
    @Parameter:
        N/A
    @Return:
        list (critical information in json)
    """
    exchangeTypes = ['sii', 'otc', 'rotc', 'pub']
    result = []

    for exchangeType in exchangeTypes:
        try:
            res = requests.post(
                'https://mops.twse.com.tw/mops/web/ajax_t05sr01_1',
                data = {
                    'encodeURIComponent': 1,
                    'TYPEK': exchangeType,
                    'step': 0
                })

            soup = BeautifulSoup(res.text, 'html.parser')
            table = soup.findChildren('table')
            rows = table[1].findChildren('tr')

            for i in range(1, len(rows)):
                rowElements = rows[i].findChildren('td')
                formVar = rowElements[5].findChildren(
                    'input')[0]['onclick'].split("'")
                formStockNum = re.sub('[a-zA-Z]', '', formVar[7])
                formDate = formVar[5]
                formTime = formVar[3]
                seqNum = formVar[1]
                title = rowElements[4].getText().replace('\r\n', '')

                i = formStockNum[0:2]
                urlLink = (
                    "https://mops.twse.com.tw/mops/web/t05st02?"
                    + "step=1&"
                    + "off=1&"
                    + "firstin=1&"
                    + f"TYPEK={exchangeType}&"
                    + f"i={i}&"
                    + f"h{i}0={rowElements[1].getText()}&"
                    + f"h{i}1={formStockNum}&"
                    + f"h{i}2={formDate}&"
                    + f"h{i}3={formTime}&"
                    + f"h{i}4={title}&"
                    + f"h{i}5={seqNum}&"
                    + "pgname=t05st02"
                )
                result.append({
                    '股號': rowElements[0].getText(),
                    '公司名稱': rowElements[1].getText(),
                    '發言日期': rowElements[2].getText(),
                    '發言時間': rowElements[3].getText(),
                    '主旨': title,
                    'link': urlLink,
                    'type': exchangeType
                })
        except:
            pass
    return result


def crawlIncomeSheetFromNotification(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    notificationTable = soup.findChildren('table', {'width': '60%'})
    description = notificationTable[0].findChildren('font', {'size': 2})
    incomeSheetText = description[0].text.split('\n')

    revenue = int(incomeSheetText[3].split('元):')[1].replace(",", ""))
    grossProfit = incomeSheetText[4].split('元):')[1].replace(",", "")
    grossProfit = -1 * \
        int(grossProfit[1:-1]) if re.match('^\(\d+\)$',
                                           grossProfit) else int(grossProfit)
    businessInterest = incomeSheetText[5].split('元):')[1].replace(",", "")
    businessInterest = -1 * int(businessInterest[1:-1]) if re.match(
        '^\(\d+\)$', businessInterest) else int(businessInterest)
    EPS = incomeSheetText[9].split('元):')[1]
    EPS = -1 * float(EPS[1:-1]) if re.match('^\(\d+.\d+\)$',
                                            EPS) else float(EPS)

    print('營業收入: ', revenue)
    print('營業毛利: ', grossProfit)
    print('毛利率:', round((grossProfit/revenue)*100, 3), '%')
    print('營業利益: ', businessInterest)
    print('營業利益率: ', round((businessInterest/revenue)*100, 3), '%')
    print('EPS: ', EPS)


if __name__ == '__main__':
    crawlIncomeSheetFromNotification(
        'https://mops.twse.com.tw/mops/web/t05st02?step=1&off=1&firstin=1&TYPEK=sii&i=174&h1740=%E5%B1%B1%E9%9A%86&h1741=2616&h1742=20210510&h1743=193928&h1744=%E6%89%BF%E8%AA%8D110%E5%B9%B4%E7%AC%AC1%E5%AD%A3%E5%90%88%E4%BD%B5%E8%B2%A1%E5%8B%99%E5%A0%B1%E8%A1%A8&h1745=1&pgname=t05st02')
    # data = crawlDataUseBs4()
    # print(len(data))
    # data = filterKeyword(data)
    # print(len(data))
    # print(data[0])
