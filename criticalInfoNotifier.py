from crawler import crawlCriticalInformation as info
from telegramParser import sendCriticalInfo as infoSender

data = info(False)
if data == None:
    print("No critical info.")
else:
    infoSender(data)