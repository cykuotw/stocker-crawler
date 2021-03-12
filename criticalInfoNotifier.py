from crawler import crawlCriticalInformation as info
from crawler import crawlDataUseBs4
from crawler import filterKeyword
from telegramParser import sendCriticalInfo as infoSender

# data = info(False)
data = crawlDataUseBs4()
data = filterKeyword(data)

# print(len(data))
# print(data)
if len(data) == 0:
    print("No critical info.")
else:
    # pass
    # print(len(data))
    infoSender(data, False)
