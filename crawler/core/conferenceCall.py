import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup


def crawlConferenceCallInfo(exchange_type, dateTime_in) -> list:
    url = "https://mops.twse.com.tw/mops/web/ajax_t100sb02_1"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    data = {
        "step": 1,
        "firstin": 1,
        "TYPEK": exchange_type,
        "year": dateTime_in.year-1911,
        "month": dateTime_in.strftime('%m')
    }
    res = requests.post(url, headers=headers, data=data)
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.findChildren('table')[0].findChildren('tr')
    current_date = f'{dateTime_in.year-1911}/{dateTime_in.strftime("%m")}/{dateTime_in.strftime("%d")}'
    messages = []
    for i in range(2, len(rows)):
        cells = rows[i].findChildren('td')
        if not cells:
            continue
        if re.match('^[0-9]{3}\/[0-9]{2}\/[0-9]{2}$', str(cells[2].text)):
            if cells[2].text == current_date:
                # messages.append(f'{cells[0].text}\t{cells[1].text}\t{cells[2].text}t{cells[4].text.strip()}\n\n')
                messages.append({
                    "companyId": cells[0].text,
                    "companyName": cells[1].text,
                    "date": cells[2].text,
                    "location": cells[4].text
                })
        else:
            date_range = cells[2].text.split(' 至 ')
            opening_day = date_range[0].split('/')
            opening_day[0] = str(int(opening_day[0]) + 1911)
            opening_day = datetime.strptime('-'.join(opening_day), '%Y-%m-%d')
            closing_day = date_range[1].split('/')
            closing_day[0] = str(int(closing_day[0]) + 1911)
            closing_day = datetime.strptime('-'.join(closing_day), '%Y-%m-%d')+ timedelta(days=1)
            if opening_day < dateTime_in < closing_day:
                # messages.append(f'{cells[0].text}\t{cells[1].text}\t{cells[2].text}\t{cells[4].text.strip()}\n\n')
                messages.append({
                    "companyId": cells[0].text,
                    "companyName": cells[1].text,
                    "date": cells[2].text,
                    "location": cells[4].text
                })
    return messages