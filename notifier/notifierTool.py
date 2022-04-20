from cgi import print_form
import json
import requests
import re
from datetime import datetime

def postStockerAnnouncement(infoList):
    with open('critical_file/host.json') as hostReader:
        criticalInfo = json.loads(hostReader.read())
    HOST = criticalInfo['HOST']

    for info in infoList:
        url = f"{HOST}/api/v0/feed/{info['股號']}"
        print(url)
        dateArr = info['發言日期'].split('/')
        dateArr[0] = str(int(dateArr[0])+1911)
        dateTime = '-'.join(dateArr) + ' ' + info['發言時間']
        dateTime = datetime.strptime(
            dateTime, '%Y-%m-%d %H:%M:%S').isoformat()
        infoJson = {
            'feedType': "announcement",
            'releaseTime': dateTime,
            'title': info['主旨'],
            'link': info['link'],
            'tags': info['tags']
        }
        requests.post(url, data=json.dumps(infoJson))

def filterKeyword(infolist):
    with open('critical_file/critical_info_filter.json') as criticalInfoReader:
        criticalInfo = json.loads(criticalInfoReader.read())

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
    with open('critical_file/chatbot_info.json') as chatbotReader:
        chatbotInfo = json.loads(chatbotReader.read())
    postURL = chatbotInfo["telegram"]["postURL"]
    chatID = chatbotInfo["telegram"]["chatID"]
    parse_mode = chatbotInfo["telegram"]["parseMode"]
    contentType = chatbotInfo["telegram"]["contentType"]

    if debug:
        text = "This is test\n"
    else:
        text = ""
    cnt = 0

    for index in range(len(data)):
        if data[index]['negativeTag']:
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
    text = ""
    text += "*" + str(int(data['股號'])) + "*\t"
    text += "*" + str(data['公司名稱']) + "*\t"
    text += "(" + str(data['發言日期']) + " "
    text += "" + toStringExchageType(data['type']) + ")\n"
    text += "[" + str(data['主旨']) + "]"
    text += "(%s)\n\n" % str(re.sub(r"[\(\)]+", "-", data['link']))

    return text

def toStringExchageType(exchangeType='sii'):
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