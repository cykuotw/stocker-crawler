import requests
import pandas as pd
from io import StringIO

def crawlCriticalInformation():
    res = requests.get('http://mops.twse.com.tw/mops/web/ajax_t05sr01_1')
    res.encode = 'utf-8'
    dfs = pd.read_html(StringIO(res.text))

    ret = pd.DataFrame()
    # code, name, date, content

    criteria = ['財務報', '盈餘']

    for index in range(0, len(dfs[1])):
        match = False
        for cr in criteria:
            match = match or ( dfs[1].iloc[index]['主旨'].find(cr) != -1)
            if(match):
                    try:
                        tmp = dfs[1].iloc[index]
                        ret = ret.append(tmp)
                    except Exception as err:
                        print(err)
                    break      
    return ret
