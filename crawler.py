#coding=utf-8
import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO

def crawlCriticalInformation(parse_to_json = False):
    res = requests.get('https://mops.twse.com.tw/mops/web/ajax_t05sr01_1')
    res.encode = 'utf-8'
    dfs = pd.read_html(StringIO(res.text), header=0, flavor='bs4')

    ret = pd.DataFrame()
    
    if len(dfs)==1:
        return ret
    # code, name, date, content

    #print(dfs[1])

    criteria_pos = [u'財務報', u'盈餘']
    criteria_neg = [u'比率', u'百分', u'補', u'重']

    for index in range(0, len(dfs[1])):
        match = False
        for crp in criteria_pos:
            match = match or ( dfs[1].iloc[index][u'主旨'].find(crp) != -1)
            for crn in criteria_neg:
                if dfs[1].iloc[index][u'主旨'].find(crn) != -1:
                    match = False

            if(match):
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
        #print(dfs.loc[rowHeader[1]])

        dataArr = []

        for i in rowHeader:
            try:
                tmpDict = {}
                for k in colHeader:
                    if k == u'公司代號':
                        tmpDict[k] = str(int(ret.loc[i][k]))
                    else:
                        tmpDict[k] = ret.loc[i][k]
                dataArr.append(tmpDict)
            except Exception as err:
                print(err)

        ret = json.dumps(dataArr)
    return ret