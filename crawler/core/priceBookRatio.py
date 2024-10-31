import requests
import json
from datetime import datetime


def crawlSiiPeRatioAnalysis(date_time):
    sii_url = "https://www.twse.com.tw/zh/exchangeReport/BWIBBU_d"
    data = {
        "response": "json",
        "date": date_time.strftime("%Y%m%d"),
        "selectType": "ALL"
    }
    res = requests.post(sii_url, data)
    dataset = json.loads(res.text)
    result = []
    if dataset['stat'] == 'OK':
        for data in dataset['data']:
            tmp = {
                "stock_id": data[0],
                "本益比": None if data[4] == "-" else data[4],
                "殖利率": data[2],
                "股價淨值比": data[5]
            }
            result.append(tmp)
        return result
    else:
        return result


def crawlOtcPeRatioAnalysis(date_time):
    otc_date = str(date_time.year-1911) + date_time.strftime("/%m/%d")
    otc_url = (
        "https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php"
        + "?l=zh-tw"
        + f"&d={otc_date}"
    )
    res = requests.get(otc_url)
    dataset = json.loads(res.text)

    result = []
    for data in dataset['tables'][0]['data']:
        tmp = {
            "stock_id": data[0],
            "本益比": None if data[2] == "N/A" else data[2],
            "殖利率": data[5],
            "股價淨值比": data[6]
        }
        result.append(tmp)

    return result

