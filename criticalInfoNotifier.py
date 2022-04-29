from datetime import datetime

from crawler.core.criticalInfo import crawlDataUseBs4
from notifier.util import (filterKeyword, infoSender,
                                   postStockerAnnouncement, pushSlackMessage)

# data = info(False)
curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
pushSlackMessage("Stocker每日重訊", '{} crawler work start.'.format(curTime))

try:
    data = crawlDataUseBs4()
    data = filterKeyword(data)

    if len(data) == 0:
        print("No critical info.")
    else:
        postStockerAnnouncement(data)
        if datetime.now().hour >= 21 and datetime.now().hour <= 22:
            infoSender(data, False)
except Exception as e:
    curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    pushSlackMessage("Stocker每日重訊", '{} crawler error.'.format(curTime, e))
finally:
    curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    pushSlackMessage("Stocker每日重訊", '{} crawler work done.'.format(curTime))
