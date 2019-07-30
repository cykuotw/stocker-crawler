from crawler import crawlCriticalInformation as info
from telegramParser import sendCriticalInfo as infoSender

data = info(False)
#print(len(data))
#print(data)
if len(data) == 0:
    print("No critical info.")
else:
    infoSender(data)