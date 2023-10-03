from crawler.interface.priceBookRatio import handleDailyPeRatioAnalysis
from notifier.util import pushSlackMessage
from datetime import datetime

if __name__ == '__main__':
    try:
        curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        pushSlackMessage("Stocker PE更新", '{} PE work start.'.format(curTime))
        #date_time = datetime.strptime('2023-08-18', '%Y-%m-%d')
        date_time = datetime.now()
        #print(date_time)
        handleDailyPeRatioAnalysis(date_time)
    except Exception as ex:
        print(ex)
        pushSlackMessage('Stocker淨值更新', ex)
    else:
        curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        pushSlackMessage("Stocker PE更新", '{} PE work end.'.format(curTime))

