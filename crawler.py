#coding=utf-8
import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO
from bs4 import BeautifulSoup
from random import randint


def crawlCriticalInformation(parse_to_json = False):
    res = requests.get('https://mops.twse.com.tw/mops/web/ajax_t05sr01_1')
    res.encode = 'utf-8'
    dfs = pd.read_html(StringIO(res.text), header=0, flavor='bs4')

    ret = pd.DataFrame()

    if len(dfs)==1:
        return ret
    # code, name, date, content

    file = open('criticalInfo.json', 'r', encoding='utf-8')
    settings = json.loads(file.read())
    file.close()

    criteria_pos = settings["criteria_pos"]
    criteria_neg = settings["criteria_neg"]

    for index in range(0, len(dfs[1])):
        match = False
        for crp in criteria_pos:
            match = match or ( dfs[1].iloc[index]['主旨'].find(crp) != -1)
            for crn in criteria_neg:
                if dfs[1].iloc[index]['主旨'].find(crn) != -1:
                    match = False

            if (match):
                try:
                    tmp = dfs[1].iloc[index]
                    ret = ret.append(tmp)
                except Exception as err:
                    print(err)
                break
    if parse_to_json:
        colHeader = list(ret.columns.values)
        colHeader.pop(0)
        rowHeader = list(ret.index)

        dataArr = []
        for i in rowHeader:
            try:
                tmpDict = {}
                for k in colHeader:
                    if k == '公司代號':
                        tmpDict[k] = str(int(ret.loc[i][k]))
                    else:
                        tmpDict[k] = ret.loc[i][k]
                dataArr.append(tmpDict)
            except Exception as err:
                print(err)

        ret = json.dumps(dataArr)
    return ret


def crawlDataUseBs4():
    exchangeTypes = ['sii', 'otc', 'rotc', 'pub']
    result = []

    for exchangeType in exchangeTypes:
        res = requests.post(
            'https://mops.twse.com.tw/mops/web/ajax_t05sr01_1',
            data = {
                'encodeURIComponent': 1,
                'TYPEK': 'sii',
                'step': 0
            })
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.findChildren('table')
        rows = table[1].findChildren('tr')

        for i in range(1, len(rows)):
            rowElements = rows[i].findChildren('td')
            formVar = rowElements[5].findChildren(
                'input')[0]['onclick'].split("'")
            formStockNum = formVar[7]
            formDate = formVar[5]
            formTime = formVar[3]
            seqNum = formVar[1]
            title = rowElements[4].getText().replace('\r\n', '')

            i = randint(1,199)
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
                'link': urlLink
            })
    return result

def filterKeyword(infolist):
    ret = []

    for r in infolist:
        if(r['股號'] == '2901'):
            print(r)
    print('\n')
    
    file = open('criticalInfo.json', 'r', encoding='utf-8')
    settings = json.loads(file.read())
    file.close()

    criteria_pos = settings["criteria_pos"]
    criteria_neg = settings["criteria_neg"]

    for index in range(0, len(infolist)):
        match = False
        for crp in criteria_pos:
            match = match or (infolist[index]['主旨'].find(crp) != -1)
            for crn in criteria_neg:
                if infolist[index]['主旨'].find(crn) != -1:
                    match = False
            if(match):
                try:
                    tmp = infolist[index]
                    ret.append(tmp)
                except Exception as err:
                    print(err)
                break
    
    for r in ret:
        if(r['股號'] == '2901'):
            print(r)
    return ret

if __name__ == '__main__':
    data = crawlDataUseBs4()
    # print(len(data))
    data = filterKeyword(data)
    # print(len(data))
    # print(data[0])
