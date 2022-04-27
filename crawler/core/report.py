# coding=utf-8
import random
import time
from datetime import datetime
from io import StringIO

import pandas as pd
import requests

SLEEPTIME = 10

def crawlMonthlyRevenue(westernYearIn, monthIn):
    """
    @description:
        爬取上市/上櫃公司月營收
    @return:
        dataFrame (sorted monthly revenue)
    @param:
        westernYearIn => int (西元年)
        monthIn => int
    """
    year = str(westernYearIn - 1911)
    month = str(monthIn)

    urlSiiDomestic = {
                        "url": "https://mops.twse.com.tw/nas/t21/sii/t21sc03_"
                               + year + "_" + month + "_0.html",
                        "type": "SiiDomestic"
                     }
    urlSiiForiegn = {
                        "url": "https://mops.twse.com.tw/nas/t21/sii/t21sc03_"
                               + year + "_" + month + "_1.html",
                        "type":  "SiiForiegn"
                    }
    urlOtcDomestic = {
                        "url": "https://mops.twse.com.tw/nas/t21/otc/t21sc03_"
                               + year + "_" + month + "_0.html",
                        "type": "OtcDomestic"
                    }
    urlOtcForiegn = {
                        "url": "https://mops.twse.com.tw/nas/t21/otc/t21sc03_"
                               + year + "_" + month + "_1.html",
                        "type": "OtcForiegn"
                    }
    urlRotcDomestic = {
                        "url": "https://mops.twse.com.tw/nas/t21/rotc/t21sc03_"
                               + year + "_" + month + "_0.html",
                        "type": "RotcDomestic"
                    }
    urlRotcForiegn = {
                        "url": "https://mops.twse.com.tw/nas/t21/rotc/t21sc03_"
                               + year + "_" + month + "_1.html",
                        "type": "RotcForiegn"
                    }
    urlPubDomestic = {
                        "url": "https://mops.twse.com.tw/nas/t21/pub/t21sc03_"
                               + year + "_" + month + "_0.html",
                        "type": "PubDomestic"
                    }
    urlPubForiegn = {
                        "url": "https://mops.twse.com.tw/nas/t21/pub/t21sc03_"
                               + year + "_" + month + "_1.html",
                        "type": "PubForiegn"
                    }

    urls = [
        urlSiiDomestic,
        urlSiiForiegn,
        urlOtcDomestic,
        urlOtcForiegn,
        urlRotcDomestic,
        urlRotcForiegn,
        urlPubDomestic,
        urlPubForiegn
    ]

    results = pd.DataFrame()
    print(str(westernYearIn) + "-" + str(monthIn))

    s = requests.session()
    s.keep_alive = False

    for url in urls:
        print("crawling monthlyRevenue " + url["type"], end='...')
        req = s.get(url["url"], timeout=10)
        req.encoding = "big5"
        print("done.")

        try:
            html_df = pd.read_html(StringIO(req.text))
            req.close()
        except ValueError:
            print('%s no %s month revenue data for %s/%s'
                  % (datetime.today().strftime("%Y-%m-%d"),
                     url["type"],
                     westernYearIn,
                     monthIn))
        else:
            dfs = pd.DataFrame()
            for df in html_df:
                if df.shape[1] == 11:
                    dfs = pd.concat([dfs, df], axis=0, ignore_index=True)
            dfs.columns = dfs.columns.droplevel()

            drop_index = []
            for i in dfs.index:
                try:
                    int(dfs.iloc[i]["公司代號"])
                except Exception:
                    drop_index.append(i)
            dfs = dfs.drop(dfs.index[drop_index])
            dfs = dfs.drop(columns=['公司名稱'])

            results = results.append(dfs)

        time.sleep(SLEEPTIME + random.randrange(0, 4))

    return results


def crawlBalanceSheet(companyID, westernYearIn, seasonIn):
    """
    @description:
        爬取個股每季的資產負債表
    @return:
        dataFrame (sorted balance sheet)
    @param:
        companyID => int
        westernYearIn => int (西元年)
        monthIn => int (1, 2...11, 12)
    """
    coID = str(companyID)
    year = str(westernYearIn - 1911)
    season = str(seasonIn)

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb03"

    if companyID == '0009A0' or\
       (int(companyID) not in range(2800, 2900) and
            int(companyID) not in range(5800, 5900)):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "encodeURIComponent": "1",
            "step": "1",
            "firstin": "1",
            "off": "1",
            "queryName": "co_id",
            "inpuType": "co_id",
            "TYPEK": "all",
            "isnew": "false",
            "co_id": coID,
            "year": year,
            "season": season,
            "Connection": "close"
        }
    else:
        headers = {
            'step': '2',
            'year': year,
            'season': season,
            'co_id': coID,
            'firstin': '1',
            "Connection": "close"
        }

    req = requests.post(url, headers)
    req.encoding = "utf-8"
    try:
        html_df = pd.read_html(StringIO(req.text))
        results = html_df[len(html_df)-1]
    except ValueError as ve:
        if ve.args[0] == "No tables found":
            return None
    except Exception as ex:
        print(ex)
        return []

    results.columns = results.columns.droplevel([0, 1])

    # drop invalid column
    results = results.iloc[:, 0:3]
    # rename columns
    amount = results.columns[1][0] + "-" + results.columns[1][1]
    percent = results.columns[2][0] + "-" + results.columns[2][1]
    results.columns = results.columns.droplevel(1)
    results.columns = [results.columns[0], amount, percent]

    resultsCopy = results.copy()
    resultsCopy.set_index("會計項目", inplace=True)

    # drop nan rows
    dropRowIndex = []
    for i in results.index:
        if resultsCopy.iloc[i].isnull().all():
            dropRowIndex.append(i)
    results = results.drop(results.index[dropRowIndex])
    results = results.set_index(results.columns[0])

    return results


def crawlIncomeSheet(companyID, westernYearIn, seasonIn):
    """
    @description:
        爬取個股每季的損益表
    @return:
        dataFrame (sorted income sheet)
    @param:
        companyID => int
        westernYearIn => int (西元年)
        monthIn => int (1,2...11,12)
    """
    coID = str(companyID)
    year = str(westernYearIn - 1911)
    season = str(seasonIn).zfill(2)

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb04"

    if companyID == '0009A0' or\
       (int(companyID) not in range(2800, 2900) and
            int(companyID) not in range(5800, 5900)):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "encodeURIComponent": "1",
            "step": "1",
            "firstin": "1",
            "off": "1",
            "queryName": "co_id",
            "inpuType": "co_id",
            "TYPEK": "all",
            "isnew": "false",
            "co_id": coID,
            "year": year,
            "season": season,
            "Connection": "close"
        }
    else:
        headers = {
            'step': '2',
            'year': year,
            'season': season,
            'co_id': coID,
            'firstin': '1',
            "Connection": "close"
        }

    print("crawling incomeSheet " + str(coID), end=" ")
    print(str(westernYearIn) + "Q" + str(season), end="...")
    s = requests.session()
    s.keep_alive = False
    req = s.post(url, headers, timeout=10)
    req.encoding = "utf-8"
    try:
        html_df = pd.read_html(StringIO(req.text))
        results = html_df[len(html_df)-1]
        req.close()
    except ValueError as ve:
        if ve.args[0] == "No tables found":
            return None
    except Exception as ex:
        print(ex)
        raise ex
    print("done.")

    results.columns = results.columns.droplevel([0, 1])
    # drop invalid column
    results = results.iloc[:, 0:3]

    # rename columns
    amount = results.columns[1][0] + "-" + results.columns[1][1]
    percent = results.columns[2][0] + "-" + results.columns[2][1]
    results.columns = results.columns.droplevel(1)
    results.columns = [results.columns[0], amount, percent]

    resultsCopy = results.copy()
    resultsCopy.set_index("會計項目", inplace=True)

    # drop nan rows
    dropRowIndex = []
    for i in results.index:
        if resultsCopy.iloc[i].isnull().all():
            dropRowIndex.append(i)
    results = results.drop(results.index[dropRowIndex])
    results = results.set_index(results.columns[0])

    return results


def crawlCashFlow(companyID, westernYearIn, seasonIn, recursiveBreak=False):
    """
    @description:
        爬取個股每季的現金流量表
    @return:
        dataFrame (sorted cash flow)
    @param:
        companyID => int
        westernYearIn => int (西元年)
        monthIn => int (1,2...11,12)
        recursiveBreak => boolean
    """
    coID = str(companyID)
    year = str(westernYearIn - 1911)
    season = str(seasonIn)

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb05"

    if companyID == '0009A0' or\
       (int(companyID) not in range(2800, 2900) and
            int(companyID) not in range(5800, 5900)):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "encodeURIComponent": "1",
            "step": "1",
            "firstin": "1",
            "off": "1",
            "queryName": "co_id",
            "inpuType": "co_id",
            "TYPEK": "all",
            "isnew": "false",
            "co_id": coID,
            "year": year,
            "season": season,
            "Connection": "close"
        }
    else:
        headers = {
            'step': '2',
            'year': year,
            'season': season,
            'co_id': coID,
            'firstin': '1',
            "Connection": "close"
        }

    while(True):
        try:
            # print(headers)
            req = requests.post(url, headers, timeout=(2, 15))
            req.encoding = "utf-8"
            html_df = pd.read_html(StringIO(req.text))
            results = html_df[len(html_df)-1]

            # drop invalid column
            results = results.iloc[:, 0:2]

            # rename columns
            amount = results.columns[1][0] + "-" + results.columns[1][1]
            results.columns = results.columns.droplevel(1)
            results.columns = [results.columns[0], amount]
            break
        except ValueError as ve:
            if ve.args[0] == "No tables found":
                return None
        except Exception as ex:
            delay = SLEEPTIME + random.randrange(0, 4)
            print("\n  ", end="")
            print(ex.__class__.__name__, end=" ")
            print("catched. Retry in %s sec." % (delay))
            time.sleep(delay)

    # drop nan rows
    dropRowIndex = []
    for i in results.index:
        if results.iloc[i].isnull().any():
            dropRowIndex.append(i)
    results = results.drop(results.index[dropRowIndex])

    # set row name
    results = results.set_index(results.columns[0])

    if recursiveBreak:
        return results

    # transfer accumulative cashflow into single season
    # sii/otc/rotc issue cashflow report seasonally
    # pub issue report semiannually/seasonally
    if seasonIn != 1:
        time.sleep(SLEEPTIME + random.randrange(0, 4))
        prev = crawlCashFlow(companyID, westernYearIn, seasonIn-1, True)
        if prev is None:
            # pub semiannually report
            if seasonIn == 2:
                return results
            elif seasonIn == 4:
                time.sleep(SLEEPTIME + random.randrange(0, 4))
                prev = crawlCashFlow(companyID, westernYearIn, 2, True)
            else:
                return None
        for index in results.index:
            try:
                results.loc[index] = results.loc[index][0] - prev.loc[index][0]
            except Exception as ex:
                pass

    return results


if __name__ == '__main__':
    print(crawlSummaryStockNoFromTWSE())
