import requests

def sendCriticalInfo(df):
    postURL = 'https://api.telegram.org/bot730162385:AAGgbRDHlQVVb8A3ovVEvuKHO1U3yqiM9Fw/sendMessage'
    chatID = '@stockerdailyinfo'
    parse_mode = 'HTML'
    contentType = 'application/x-www-form-urlencoded'   

    text = ""
    cnt = 0
    for index in range(0, len(df)):
        text = text + "<b>" + str(int(df.iloc[index]['公司代號'])) + "</b>\t"
        text = text + "<b>" + str(df.iloc[index]['公司簡稱']) + "</b>\t"
        text = text + "(" + str(df.iloc[index]['發言日期']) + ")\n"
        text = text + "<code>" + str(df.iloc[index]['主旨']) + "</code>\n\n"
        
        cnt = cnt + 1
        if cnt == 4 or (index == len(df)-1 and cnt != 0):
            text = text + "\n" + "https://mops.twse.com.tw/mops/web/t05sr01_1"
            postData = {'Content-Type': contentType, 'chat_id': chatID, 'text' : text, 
                        'parse_mode' : parse_mode}
            r = requests.post(postURL, postData)
            text = ""
            cnt = 0
    pass