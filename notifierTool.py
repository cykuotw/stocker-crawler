import json
import requests
from datetime import datetime


def postStockerAnnouncement(infoList):
    with open('criticalInfo.json') as criticalInfoReader:
        criticalInfo = json.loads(criticalInfoReader.read())
    HOST = criticalInfo['HOST']

    for info in infoList:
        url = f"http://{HOST}/api/v0/feed/{info['股號']}"
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
    with open('criticalInfo.json') as criticalInfoReader:
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
