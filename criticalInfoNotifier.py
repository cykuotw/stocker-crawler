from crawler import crawlCriticalInformation as info
from crawler import crawlDataUseBs4
from telegramParser import sendCriticalInfo as infoSender

# data = info(False)
data = crawlDataUseBs4()
#print(len(data))
# print(data)
if len(data) == 0:
    print("No critical info.")
else:
    pass
    #print(data)
    #infoSender(data)
