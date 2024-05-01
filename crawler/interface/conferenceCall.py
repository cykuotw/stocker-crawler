import re
import requests
import json

from crawler.core.conferenceCall import crawlConferenceCallInfo
from datetime import datetime
from notifier.discord import pushDiscordConCallInfo
from crawler.interface.criticalInfo import toStringExchageType
from crawler.interface.util import stockerUrl


def postEarningsCall(earnings_call_data):
    earnings_call_pi = "{}/earnings_call".format(stockerUrl)
    res = requests.post(earnings_call_pi, data=json.dumps(earnings_call_data))


def updateConferenceCallInfo() -> None:
    now = datetime.now()
    for exchangeType in ['sii', 'otc']:
        data = crawlConferenceCallInfo(exchangeType, now)
        #print(data)
        step = 10
        cnt = 0
        message = ""
        for i in range(len(data)):
            message += "**" + str(data[i]['companyId']) + "**\t"
            message += "**" + str(data[i]['companyName']) + "**\t"
            message += "*(" + str(data[i]['date']) + " "
            message += toStringExchageType(exchangeType) + ")*\t\t"
            message += "**" + data[i]['location'] + "**\n"

            cnt += 1

            if re.match('^[0-9]{3}\/[0-9]{2}\/[0-9]{2}$', str(data[i]['date'])):
                meeting_date = str(data[i]['date'])
                meeting_end_date = None
            else:
                meeting_date, meeting_end_date = str(data[i]['date']).split(' 至 ')

            postEarningsCall({
                "stock_id": str(data[i]['companyId']),
                "meeting_date": meeting_date,
                "meeting_end_date": meeting_end_date,
                "location": data[i]['location'],
                "description": data[i]['description'],
                "file_name_chinese": data[i]['file_name_chinese'] 
            })

            if cnt == step or (i == len(data)-1 and cnt != 0):
                pushDiscordConCallInfo("法說會資訊", message)
                message = ""
                cnt = 0

