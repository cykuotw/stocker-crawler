from crawler.crawlerCriticalInfo import crawlCriticalInformation as info
from crawler.crawlerCriticalInfo import crawlDataUseBs4
from notifier.notifierTool import filterKeyword, postStockerAnnouncement, infoSender
from datetime import datetime

# data = info(False)
data = crawlDataUseBs4()
data = filterKeyword(data)

if len(data) == 0:
    print("No critical info.")
else:
    postStockerAnnouncement(data)
    # if datetime.now().hour >= 21 and datetime.now().hour <= 22:
    infoSender(data, False)
