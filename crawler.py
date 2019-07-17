import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO

def crawlCriticalInformation(parse_to_json = False):
    res = requests.get('https://mops.twse.com.tw/mops/web/ajax_t05sr01_1')
    res.encode = 'utf-8'
    dfs = pd.read_html(StringIO(res.text))

    ret = pd.DataFrame()
    # code, name, date, content

    criteria_pos = ['財務報', '盈餘']
    criteria_neg = ['比率']

    for index in range(0, len(dfs[1])):
        match = False
        for crp in criteria_pos:
            match = match or ( dfs[1].iloc[index]['主旨'].find(crp) != -1)
            for crn in criteria_neg:
                if dfs[1].iloc[index]['主旨'].find(crn) != -1:
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
                    if k == '公司代號':
                        tmpDict[k] = str(int(ret.loc[i][k]))
                    else:
                        tmpDict[k] = ret.loc[i][k]
                dataArr.append(tmpDict)
            except Exception as err:
                print(err)

        ret = json.dumps(dataArr)
    return ret