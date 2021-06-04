import requests
import re

def sendCriticalInfo(data, debug=False):
    postURL = 'https://api.telegram.org/bot730162385:AAGgbRDHlQVVb8A3ovVEvuKHO1U3yqiM9Fw/sendMessage'
    chatID = '@stockerdailyinfo'
    parse_mode = 'markdown'
    contentType = 'application/x-www-form-urlencoded'

    if debug:
        text = "This is test\n"
    else:
        text = ""
    cnt = 0

    for index in range(len(data)):
        if data[index]['negativeTag']:
            continue
        text += "*" + str(int(data[index]['股號'])) + "*\t"
        text += "*" + str(data[index]['公司名稱']) + "*\t"
        text += "(" + str(data[index]['發言日期']) + ")\n"
        text += "[" + str(data[index]['主旨']) + "]"
        text += "(%s)\n\n" % str(re.sub(r"[\(\)]+", "-", data[index]['link']))
        cnt = cnt + 1

        if debug:
            print(text)
            break
        else:
            if cnt == 10 or (index == len(data)-1 and cnt != 0):
                postData = {
                    'Content-Type': contentType,
                    'chat_id': chatID,
                    'text' : text,
                    'parse_mode' : parse_mode
                }
                # print(text)
                r = requests.post(postURL, postData)
                text = ""
                cnt = 0


if __name__ == '__main__':
    postURL = 'https://api.telegram.org/bot730162385:AAGgbRDHlQVVb8A3ovVEvuKHO1U3yqiM9Fw/sendMessage'
    chatID = '@stockerdailyinfo'
    # parse_mode = 'HTML'
    parse_mode = 'markdown'
    contentType = 'application/x-www-form-urlencoded'

    text = ''
    # text += '<b>2443</b>\t<b>互盛電</b>\t(110/03/11)\n<code>代重要子公司震旦開發(股)公司公告發放股利</code>\n'
    text += '*2443*\t*互盛電*\t(110/03/11)\n'
    url = 'https://mops.twse.com.tw/mops/web/t05st02?step=1&off=1&firstin=1&TYPEK=sii&i=175&h1750=互盛電&h1751=2433&h1752=20210311&h1753=232005&h1754=代重要子公司震旦開發(股)公司公告發放股利&h1755=2&pgname=t05st02'
    # text += '<a href="%s">公告連結</s>' % url.encode(encoding='UTF-8')
    url = re.sub(r"[\(\)]+", "-", url)
    # text += '[代重要子公司震旦開發(股)公司公告發放股利](%s)' % s.tinyurl.short(url)
    text += '[代重要子公司震旦開發(股)公司公告發放股利](%s)' % url


    print(text)
    # print(len(text))

    postData = {
        'Content-Type': contentType,
        'chat_id': chatID,
        'text' : text,
        'parse_mode' : parse_mode}
    r = requests.post(postURL, postData)
