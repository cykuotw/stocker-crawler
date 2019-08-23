import requests

def sendCriticalInfo(df, debug=False):
    postURL = 'https://api.telegram.org/bot730162385:AAGgbRDHlQVVb8A3ovVEvuKHO1U3yqiM9Fw/sendMessage'
    chatID = '@stockerdailyinfo'
    parse_mode = 'HTML'
    contentType = 'application/x-www-form-urlencoded'   

    if debug:
        text = "This is test\n"
    else:
        text = ""
    cnt = 0

    for index in range(0, len(df)):
        # url = "https://mops.twse.com.tw/mops/web/t05st02?step=1&off=1&firstin=1&"

        text += "<b>" + str(int(df.iloc[index]['公司代號'])) + "</b>\t"
        text += "<b>" + str(df.iloc[index]['公司簡稱']) + "</b>\t"
        text += "(" + str(df.iloc[index]['發言日期']) + ")\n"
        text += "<code>" + str(df.iloc[index]['主旨']) + "</code>\n\n"
        # text += "<a href="'%s'">公告連結</a>" % url

        cnt = cnt + 1
        if debug:
            print(text)
            text = ""
            cnt = 0
        else:
            if cnt == 4 or (index == len(df)-1 and cnt != 0):
                text = text + "\n" + "https://mops.twse.com.tw/mops/web/t05sr01_1"
                postData = {
                    'Content-Type': contentType, 
                    'chat_id': chatID, 
                    'text' : text, 
                    'parse_mode' : parse_mode}
                r = requests.post(postURL, postData)
                text = ""
                cnt = 0
    pass