import json
import re
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup

from crawler.common.notifier import (
    discord,
    pushCriticalInfoMessage,
    pushErrorMessage,
    telegram,
)
from crawler.common.util.config import getStockerConfig

with open('configs/critical_info_filter.json', encoding='utf-8') as criticalInfoReader:
    criticalInfo = json.loads(criticalInfoReader.read())


def crawlCriticalInfo():
    """
    @Description:
        Crawl everyday critical infomation
    @Parameter:
        N/A
    @Return:
        list (critical information in json)
    """
    # exchangeTypes = ['sii', 'otc', 'rotc', 'pub']
    exchangeTypes = ['sii', 'otc', 'rotc']
    result = []

    for exchangeType in exchangeTypes:
        res = requests.post(
            'https://mopsov.twse.com.tw/mops/web/ajax_t05sr01_1',
            data={
                'encodeURIComponent': 1,
                'TYPEK': exchangeType,
                'step': 0
            }, timeout=10)

        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.findChildren('table')
        if len(table) == 1:
            continue
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
                "https://mopsov.twse.com.tw/mops/web/t05st02?step=1&off=1&firstin=1&"
                f"TYPEK={exchangeType}&"
                f"i={i}&"
                f"h{i}0={rowElements[1].getText()}&"
                f"h{i}1={formStockNum}&"
                f"h{i}2={formDate}&"
                f"h{i}3={formTime}&"
                f"h{i}4={title}&"
                f"h{i}5={seqNum}&pgname=t05st02"
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
    return result


def updateCriticalInfo() -> None:
    """
    @Description:
        Update everyday critical infomation
    @Parameter:
        N/A
    @Return:
        N/A
    """
    pushCriticalInfoMessage("crawler work start.")

    data = []
    try:
        data = crawlCriticalInfo()
    except Exception as e:
        pushErrorMessage(f"crawler error: {e}", crawler="criticalInfo")
        pushCriticalInfoMessage("crawler work done.")
        return

    # filter keyword
    criteriaPos = criticalInfo["criteria_pos"]
    criteriaNeg = criticalInfo["criteria_neg"]

    for index, info in enumerate(data):
        info['tags'] = []
        info['negativeTag'] = False
        for crp in criteriaPos:
            if info['主旨'].find(crp) != -1:
                info['tags'].append(crp)
        for crn in criteriaNeg:
            if info['主旨'].find(crn) != -1:
                info['negativeTag'] = True
                break

    if len(data) == 0:
        pushCriticalInfoMessage("no data")
        pushCriticalInfoMessage("crawler work done.")
        return

    # post stocker announcement
    stockerConfig = getStockerConfig()
    stockerURL = stockerConfig.get('STOCKER_URL')
    stockerBearerToken = stockerConfig.get('STOCKER_BEARER_TOKEN')

    url = f"{stockerURL}/feed"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {stockerBearerToken}",
    }

    tw = pytz.timezone('Asia/Taipei')
    failed_feeds = []
    for info in data:
        dateArr = info['發言日期'].split('/')
        dateArr[0] = str(int(dateArr[0])+1911)

        dateTime = '-'.join(dateArr) + ' ' + info['發言時間']
        dateTime = datetime.strptime(dateTime, '%Y-%m-%d %H:%M:%S')
        dateTime = tw.localize(dateTime)
        dateTime = dateTime.astimezone(tz=pytz.UTC).isoformat()

        infoJson = {
            'feedType': "announcement",
            'releaseTime': dateTime,
            'title': info['主旨'],
            'link': info['link'],
            'tags': info['tags'],
            'stocks': [info['股號']],
            'source': 'mops'
        }

        try:
            response = requests.post(
                url,
                data=json.dumps(infoJson),
                headers=headers,
                timeout=10,
            )

            if not response.ok:
                failed_feeds.append({
                    'stock': infoJson['stocks'][0],
                    'title': infoJson['title'],
                    'status': response.status_code,
                    'message': response.text,
                })
        except requests.RequestException as e:
            print(f"request error: {e}")
            failed_feeds.append({
                'stock': infoJson['stocks'][0],
                'title': infoJson['title'],
                'status': 'request-error',
                'message': str(e),
            })

    if failed_feeds:
        pushErrorMessage(
            "crawler post feed failed",
            crawler="criticalInfo",
            details=failed_feeds,
        )

    # push to discord everyday between 20:00 to 22:00
    if datetime.now(tw).hour < 20 or datetime.now(tw).hour > 22:
        pushCriticalInfoMessage("crawler work done.")
        return

    content = ""
    cnt = 0
    for index, info in enumerate(data):
        if info['negativeTag'] or len(info['tags']) == 0:
            continue

        content += f"**{info['股號']}**\t"
        # to unicode asterisk(*)
        content += f"**{re.sub('[*]', '＊', info['公司名稱'])}**\t"
        content += f"({info['發言日期']} "
        content += f"{toStringExchageType(info['type'])})\n"
        content += f"[{info['主旨']}]"
        content += "(%s)\n" % re.sub(r"[ ]", "%20",
                                     re.sub(r"[\(\)]+", "-", info['link']))

        cnt += 1

        if cnt == 5 or (index == len(data)-1 and cnt != 0):
            discord.pushInfo(content=content)
            telegram.push(content)
            content = ""
            cnt = 0

    pushCriticalInfoMessage("crawler work done.")


def toStringExchageType(exchangeType: str = 'sii') -> str:
    """
    @Description:
        Lookup table translate exchange type code into Manderin
    @Parameter:
        exchangeType: str
    @Return:
        ManderinExchangeType: str
    """
    if exchangeType == 'sii':
        tp = "上市"
    elif exchangeType == 'otc':
        tp = "上櫃"
    elif exchangeType == 'rotc':
        tp = "興櫃"
    elif exchangeType == 'pub':
        tp = "公開發行"
    else:
        tp = ""

    return tp
