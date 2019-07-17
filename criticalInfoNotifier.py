from crawler import crawlCriticalInformation as info
from telegramParser import sendCriticalInfo as infoSender

data = info(False)
infoSender(data)