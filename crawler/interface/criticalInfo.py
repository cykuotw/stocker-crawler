import json
import os
import re
from datetime import datetime

import pytz
import requests
from dotenv import load_dotenv

from crawler.core.criticalInfo import crawlDataUseBs4
from notifier.discord import pushDiscordLog, pushDiscordInfo
from notifier.util import pushTelegramMessage

load_dotenv()

HOST = os.environ.get("host-url")

with open('configs/critical_info_filter.json') as criticalInfoReader:
    criticalInfo = json.loads(criticalInfoReader.read())


def updateCriticalInfo() -> None:
    pushDiscordLog("Stocker每日重訊", '{} crawler work start.'.format(
        datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))

    try:
        # crawl raw critical info
        data = crawlDataUseBs4()

        # filter keyword
        criteria_pos = criticalInfo["criteria_pos"]
        criteria_neg = criticalInfo["criteria_neg"]

        for index in range(len(data)):
            data[index]['tags'] = []
            data[index]['negativeTag'] = False
            for crp in criteria_pos:
                if data[index]['主旨'].find(crp) != -1:
                    data[index]['tags'].append(crp)
            for crn in criteria_neg:
                if data[index]['主旨'].find(crn) != -1:
                    data[index]['negativeTag'] = True
                    break

        if len(data) == 0:
            pushDiscordLog("Stocker每日重訊", '{} no data.'.format(
                datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
            pushDiscordLog("Stocker每日重訊", '{} crawler work done.'.format(
                datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
            return

        # post stocker announcement
        tw = pytz.timezone('Asia/Taipei')
        for info in data:
            url = f"{HOST}/api/v0/feed"
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
            requests.post(url, data=json.dumps(infoJson))

        # push to discord everyday between 20:00 to 22:00
        if datetime.now().hour >= 20 and datetime.now().hour <= 22:
            content = ""
            cnt = 0
            for index in range(len(data)):
                if data[index]['negativeTag'] or len(data[index]['tags']) == 0:
                    continue
                print(data[index])
                content += "**" + str(int(data[index]['股號'])) + "**\t"
                # to unicode asterisk(*)
                content += "**" + \
                    re.sub("[*]", "＊", str(data[index]['公司名稱'])) + "**\t"
                content += "(" + str(data[index]['發言日期']) + " "
                content += "" + toStringExchageType(data[index]['type']) + ")\n"
                content += "[" + str(data[index]['主旨']) + "]"
                content += "(%s)\n\n" % str(re.sub(r"[\(\)]+",
                                                "-", data[index]['link']))

                cnt += 1

                if cnt == 10 or (index == len(data)-1 and cnt != 0):
                    pushDiscordInfo("Stocker每日重訊", content)
                    pushTelegramMessage(content)
                    content = ""
                    cnt = 0
    except Exception as e:
        pushDiscordLog("Stocker每日重訊", '{} crawler error: {}.'.format(
            datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), e))
        pushDiscordLog("Stocker每日重訊", '{} crawler work done.'.format(
            datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
        return

    pushDiscordLog("Stocker每日重訊", '{} crawler work done.'.format(
        datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))


def toStringExchageType(exchangeType: str = 'sii') -> str:
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
