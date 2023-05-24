from crawler.core.conferenceCall import crawlConferenceCallInfo
from datetime import datetime
from notifier.discord import pushDiscordConCallInfo
from crawler.interface.criticalInfo import toStringExchageType


def updateConferenceCallInfo() -> None:
    now = datetime.now()
    for exchangeType in ['sii', 'otc']:
        data = crawlConferenceCallInfo(exchangeType, now)

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

            if cnt == step or (i == len(data)-1 and cnt != 0):
                pushDiscordConCallInfo("法說會資訊", message)
                message = ""
                cnt = 0
                break
