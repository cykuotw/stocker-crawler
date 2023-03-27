import json
import os
import re
import pytz
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ.get("host-url")
chatbotInfo = {
    'telegram-message-url': os.environ.get("telegram-message-url"),
    'telegram-chat-id': os.environ.get("telegram-chat-id"),
    'slack': os.environ.get("slack-hook")
}

with open('configs/critical_info_filter.json') as criticalInfoReader:
    criticalInfo = json.loads(criticalInfoReader.read())

def postStockerAnnouncement(infoList):
    """
    Post every critical information to stocker server
    """
    tw = pytz.timezone('Asia/Taipei')
    for info in infoList:
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

def filterKeyword(infolist):
    """
    Filter critical information with positive/negative keywords.
    - Positive keyword: add matched keyword into tags
    - Negative keyword: tag with negativeTag if there is any match
    """
    criteria_pos = criticalInfo["criteria_pos"]
    criteria_neg = criticalInfo["criteria_neg"]

    for index in range(len(infolist)):
        infolist[index]['tags'] = []
        infolist[index]['negativeTag'] = False
        for crp in criteria_pos:
            if infolist[index]['主旨'].find(crp) != -1:
                infolist[index]['tags'].append(crp)
        for crn in criteria_neg:
            if infolist[index]['主旨'].find(crn) != -1:
                infolist[index]['negativeTag'] = True
                break
    return infolist

def infoSender(data, debug=False):
    """
    Post filtered critical information to telegram channel.
    Info with True negativeTag is neglected.
    """
    postURL = chatbotInfo['telegram-message-url']
    chatID = chatbotInfo['telegram-chat-id']
    parse_mode = "markdown"
    contentType = "application/x-www-form-urlencoded"

    if debug:
        text = "This is test\n"
    else:
        text = ""
    cnt = 0

    for index in range(len(data)):
        if data[index]['negativeTag'] or len(data[index]['tags']) == 0:
            continue
        text += toMarkdown(data[index])
        cnt += 1

        if debug:
            print(text)
            postData = {
                'Content-Type': contentType,
                'chat_id': chatID,
                'text' : text,
                'parse_mode' : parse_mode
            }
            r = requests.post(postURL, postData)
            break
        else:
            if cnt == 10 or (index == len(data)-1 and cnt != 0):
                postData = {
                    'Content-Type': contentType,
                    'chat_id': chatID,
                    'text' : text,
                    'parse_mode' : parse_mode
                }
                # print(text)
                r = requests.post(postURL, postData)
                text = ""
                cnt = 0


def toMarkdown(data):
    """
    Helper function to infoSender
    """
    text = ""
    text += "*" + str(int(data['股號'])) + "*\t"
    # to unicode asterisk(*)
    text += "*" + re.sub("[*]", "＊", str(data['公司名稱'])) + "*\t"
    text += "(" + str(data['發言日期']) + " "
    text += "" + toStringExchageType(data['type']) + ")\n"
    text += "[" + str(data['主旨']) + "]"
    text += "(%s)\n\n" % str(re.sub(r"[\(\)]+", "-", data['link']))

    return text


def toStringExchageType(exchangeType='sii'):
    """
    Helper function to infoSender
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

def pushSlackMessage(username, content):
    requests.post(
        chatbotInfo['slack'],
        data=json.dumps({
            "username": username,
            "text": content
        }),
        headers = {"content-type": "application/json"})
