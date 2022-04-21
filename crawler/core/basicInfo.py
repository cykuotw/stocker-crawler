# coding=utf-8
import json
from datetime import datetime
from io import StringIO

import pandas as pd
import requests

def crawlBasicInformation(companyType):
    """
    @description:
        爬取上市/上櫃/興櫃/公開發行個股的基本資料
    @return:
        dataFrame (sorted basicInfo)
    @param:
        companyType => string("sii", "otc", "rotc", "pub")
    """
    url = "https://mops.twse.com.tw/mops/web/ajax_t51sb01"
    headers = {
        'User-Agent': """Mozilla/5.0
                      (Macintosh; Intel Mac OS X 10_10_1)
                      AppleWebKit/537.36 (KHTML, like Gecko)
                      Chrome/39.0.2171.95 Safari/537.36""",
        'Content-Type': 'application/x-www-form-urlencoded',
        'encodeURIComponent': '1',
        'step': '1',
        'firstin': '1',
        'off': '1',
        'TYPEK': companyType,
    }
    result = requests.get(url, headers, timeout=(2, 15))
    print("crawling basicInfo " + companyType, end='...')
    result.encoding = 'utf-8'
    html_df = pd.read_html(StringIO(result.text), header=0)
    print("done.")
    ret = html_df[0]

    # take out all special char out
    ret = ret.replace(r'\,', '/', regex=True)
    ret = ret.fillna("0")

    # remove invalid row
    drop_index = []
    for i in ret.index:
        if ret.iloc[i]["公司代號"] == "公司代號":
            drop_index.append(i)
    ret = ret.drop(ret.index[drop_index])

    return ret


def crawlDelistedCompany(companyType):
    currentYear = datetime.now().year
    lastYear = currentYear - 1
    if companyType == 'sii':
        url = 'https://www.twse.com.tw/company/suspendListingCsvAndHtml\
            ?type=html&lang=zh'
        resultCurrent = requests.get(
            '%s&selectYear=%d' % (url, currentYear), timeout=(2, 15))
        resultLast = requests.get(
            '%s&selectYear=%d' % (url, lastYear), timeout=(2, 15))
        resultCurrent.encoding = 'utf-8'
        resultLast.encoding = 'utf-8'
        html_dfCurr = pd.read_html(StringIO(resultCurrent.text), header=1)
        html_dfLast = pd.read_html(StringIO(resultLast.text), header=1)
        html_df = pd.concat([html_dfCurr[0], html_dfLast[0]])
        # html_df.drop(["終止上市日期", "公司名稱"], axis=1, inplace=True)

        return html_df['上市編號'].values.tolist()
    elif companyType == 'otc':
        url = 'https://www.tpex.org.tw/web/regular_emerging/deListed/de-listed_companies.php?l=zh-tw'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'Submit': '查詢',
                        'select_year': str(currentYear - 1911),
            'DELIST_REASON': '-1'
        }
        body['select_year'] = str(currentYear - 1911)
        resultCurrent = requests.post(
            url,
            headers=headers,
            data=json.dumps(body),
            timeout=(2, 15))
        body['select_year'] = str(lastYear - 1911)
        resultLast = requests.post(
            url,
            headers=headers,
            data=json.dumps(body),
            timeout=(2, 15))
        resultCurrent.encoding = 'utf-8'
        resultLast.encoding = 'utf-8'
        html_dfCurr = pd.read_html(StringIO(resultCurrent.text), header=0)
        html_dfLast = pd.read_html(StringIO(resultLast.text), header=0)
        html_df = pd.concat([html_dfCurr[0], html_dfLast[0]])
        return html_df['股票代號'].values.tolist()
