from crawler import crawlCriticalInformation as info
from crawler import crawlDataUseBs4
from telegramParser import sendCriticalInfo as infoSender
from notifierTool import filterKeyword, postStockerAnnouncement
from datetime import datetime

# data = info(False)
data = crawlDataUseBs4()
data = filterKeyword(data)

if len(data) == 0:
    print("No critical info.")
else:
    postStockerAnnouncement(data)
    if datetime.now().hour >= 21 and datetime.now().hour <= 22:
        infoSender(data, False)
