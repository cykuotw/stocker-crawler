# coding=utf-8
import json
import random
import time
from datetime import datetime
from io import StringIO

import pandas as pd
import requests

SLEEPTIME = 10

def crawlBasicInformation(companyType):
    """
    @Description:
        爬取上市/上櫃/興櫃/公開發行個股的基本資料\n
        Crawl basic information of all sii/otc/rotc/pub companies.
    @Parameter:
        companyType => string("sii", "otc", "rotc", "pub")
    @Return:
        dataFrame (sorted basicInfo)
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
    """
    @Description:
        爬取上市/上櫃個股的下市資訊\n
        Crawl basic information of all sii/otc/rotc/pub companies.
    @Parameter:
        companyType => string("sii", "otc")
    @Return:
        list (delisted company ID)
    """
    currentYear = datetime.now().year
    lastYear = currentYear - 1
    res = []

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

        res = html_df['上市編號'].values.tolist()

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
        
        res = html_df['股票代號'].values.tolist()

    return res

def crawlSummaryStockNoFromTWSE(
        reportTypes='income_sheet',
        companyType='sii',
        westernYearIn=2019,
        seasonIn=3):
    """
    @Description:
        Crawl entire stock id for entire finance report.
    @Parameters:
        companyType: string(sii, otc)
        westernYearIn: western year
        seasonIn: Financial quarter(1, 2, 3, 4)
    @Return:
        list (entire stock id)
    @Raises:
        Exception: no table in request result or others things.
    """
    season = str(seasonIn).zfill(2)
    print(reportTypes + " " + companyType + " summary "
          + str(westernYearIn) + 'Q' + str(season), end='...')
    year = str(westernYearIn - 1911)

    if reportTypes == 'balance_sheet':
        url = "https://mops.twse.com.tw/mops/web/ajax_t163sb05"
    else:
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "isQuery": 'Y',
        "TYPEK": companyType,
        "year": year,
        "season": season,
    }

    retry = 0
    stockNums = []

    while(True):
        try:
            req = requests.post(url, headers, timeout=(2, 25))
            print("request")
            req.encoding = "utf-8"
            html_df = pd.read_html(req.text, converters={'公司代號': str})
            print("done.")
        except ValueError:
            print('%s no %s data for %sQ0%s'
                  % (datetime.today().strftime("%Y-%m-%d"),
                     reportTypes,
                     westernYearIn,
                     seasonIn))
            break
        except Exception as ex:
            if retry == 2:
                return []
            retry = retry + 1
            delay = SLEEPTIME + random.randrange(0, 4)
            print("  ", end="")
            print(type(ex).__name__, end=" ")
            print("catched. Retry in %s sec." % (delay))
            time.sleep(delay)
        else:
            for idx in range(1, len(html_df)):
                stockNums += list(html_df[idx]['公司代號'])
            break

    return stockNums
