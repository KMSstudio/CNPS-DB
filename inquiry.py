import requests
from datetime import datetime
from bs4 import BeautifulSoup

def cj_inquiry(invoice):
    global db
    url = "http://nexs.cjgls.com/web"
    suffix = "/info.jsp"
    headers = { "Content-Type": "application/json;charset=UTF-8" }
    params = { 'slipno': str(invoice) }

    try:
        response = requests.get(url+suffix, headers=headers, params=params)
    except:
        return {'success': False, 'msg': 'request timesrror'}

    soup = BeautifulSoup(response.text, 'html5lib')
    items = soup.select('body > center > table:nth-child(9) > tbody > tr')
    inquiry = []
    inqLine = {}
    
    if items[1].select('td')[0].text == "해당 정보가 없습니다.":
        return {'success': False, 'msg': 'false invoice'}
    for item in items[1:]:
        temp = item.select('body > center > table:nth-child(9) > tbody > tr > td')
        inqLine['dateTime'] = int(datetime.strptime( temp[0].text.strip() + " " + temp[1].text.strip() , '%Y-%m-%d %H:%M:%S').timestamp())//60
        inqLine['loc'] = temp[2].text[:temp[2].text.index('Tel')].strip()
        if '(' in inqLine['loc']:
            inqLine['loc'] = inqLine['loc'][:inqLine['loc'].index('(')] + inqLine['loc'][inqLine['loc'].index(')')+1:]
        if '[' in inqLine['loc']:
            inqLine['loc'] = inqLine['loc'][:inqLine['loc'].index('[')] + inqLine['loc'][inqLine['loc'].index(']')+1:]
        inqLine['process'] = temp[3].text.strip()
        inquiry.append(inqLine.copy())

    if len(inquiry) <= 1:
        return {'success': False, 'msg': 'delivery is not finished'}

    result = []
    for line in inquiry[1:]:
        date = datetime.fromtimestamp(line['dateTime'] * 60)
        prog = f"{max(date.weekday()-3, 0)}T{date.hour // 2}_{line['loc']}_{line['process']}"

        result.append((prog, inquiry[0]['dateTime'] - line['dateTime']))
    result.append(('cj', result[-1][1]))

    return {'success': True, 'res': result}

def po_inquiry(invoice):
    global db
    url = "https://service.epost.go.kr"
    suffix = "/trace.RetrieveDomRigiTraceList.comm"
    headers = { "Content-Type": "application/json;charset=UTF-8" }
    params = { 'sid1': str(invoice) }

    try:
        response = requests.get(url+suffix, headers=headers, params=params)
    except:
        return {'success': False, 'msg': 'request timesrror'}

    soup = BeautifulSoup(response.text, 'html5lib')
    items = soup.select('body > #sbody_layout > #contents_layout > .contents > .h4_wrap > #print > :nth-child(6) > table > tbody > tr')

    inquiry = []
    inqLine = {}
    
    if len(items) == 0:
        return {'success': False, 'msg': 'false invoice'}

    for item in items:
        temp = item.select('td')
        
        inqLine['dateTime'] = int(datetime.strptime( temp[0].text.strip() + " " + temp[1].text.strip() , '%Y.%m.%d %H:%M').timestamp())//60
        inqLine['loc'] = temp[2].text.strip()
        for char in ['(', '[', 'TEL', '\n', '\t']:
            if char in inqLine['loc'].upper():
                inqLine['loc'] = inqLine['loc'][:inqLine['loc'].upper().index(char)]
        inqLine['process'] = temp[3].text.strip()
        for char in ['(', '[', 'TEL', '\n', '\t']:
            if char in inqLine['process'].upper():
                inqLine['process'] = inqLine['process'][:inqLine['process'].upper().index(char)]
        inquiry.append(inqLine.copy())

    if len(inquiry) <= 1:
        return {'success': False, 'msg': 'delivery is not finished'}

    result = []
    for line in inquiry[:-1]:
        date = datetime.fromtimestamp(line['dateTime'] * 60)
        prog = f"{max(date.weekday()-3, 0)}T{date.hour // 2}_{line['loc']}_{line['process']}"

        result.append((prog, inquiry[-1]['dateTime'] - line['dateTime']))
    result.append(('po', result[0][1]))

    return {'success': True, 'res': result}

def hj_inquiry(invoice):
    global db
    url = "https://www.hanjin.com"
    suffix = "/kor/CMS/DeliveryMgr/WaybillResult.do"
    headers = { "Content-Type": "application/json;charset=UTF-8" }
    params = { 'mCode': 'MN038', 'schLang': 'KR', 'wblnumText2': str(invoice) }

    try:
        response = requests.get(url+suffix, headers=headers, params=params)
    except:
        return {'success': False, 'msg': 'request timesrror'}

    soup = BeautifulSoup(response.text, 'html5lib')
    items = soup.select('body > #doc-wrap > #container-wrap > #container > #contents #cont > #delivery-wr > .cont-box > .waybill-tbl > table > tbody > tr')

    inquiry = []
    inqLine = {}
    
    if len(items) == 0:
        return {'success': False, 'msg': 'false invoice'}

    for item in items:
        temp = item.select('td')
        
        inqLine['dateTime'] = int(datetime.strptime( temp[0].text.strip() + " " + temp[1].text.strip() , '%Y-%m-%d %H:%M').timestamp())//60
        inqLine['loc'] = temp[2].text.strip()
        for char in ['(', '[', 'TEL', '\n', '\t']:
            if char in inqLine['loc'].upper():
                inqLine['loc'] = inqLine['loc'][:inqLine['loc'].upper().index(char)]
        
        tempS = temp[3].text
        if '입고' in tempS:
            inqLine['process'] = '입고'
        elif '접수' in tempS:
            inqLine['process'] = '접수'
        elif '준비' in tempS:
            inqLine['process'] = '배송준비'
        elif '출발' in tempS:
            inqLine['process'] = '배송출발'
        elif '완료' in tempS:
            inqLine['process'] = '배송완료'
        else:
            inqLine['process'] = '이동'#'간선상차'
        inquiry.append(inqLine.copy())
    if len(inquiry) <= 1:
        return {'success': False, 'msg': 'delivery is not finished'}

    result = []
    for line in inquiry[:-1]:
        date = datetime.fromtimestamp(line['dateTime'] * 60)
        prog = f"{max(date.weekday()-3, 0)}T{date.hour // 2}_{line['loc']}_{line['process']}"

        result.append((prog, inquiry[-1]['dateTime'] - line['dateTime']))
    result.append(('hj', result[0][1]))

    return {'success': True, 'res': result}

def lg_inquiry(invoice):
    global db
    url = "https://www.ilogen.com/"
    suffix = "/web/personal/trace/" + str(invoice)
    headers = { "Content-Type": "application/json;charset=UTF-8" }
    params = {  }

    try:
        response = requests.get(url+suffix, headers=headers, params=params)
    except:
        return {'success': False, 'msg': 'request timesrror'}

    soup = BeautifulSoup(response.text, 'html5lib')
    items = soup.select('body > div.contents.personal.tkSearch > section > div > div.tab_container > div > table.data.tkInfo > tbody > tr')

    inquiry = []
    inqLine = {}
    
    if len(items) == 0:
        return {'success': False, 'msg': 'false invoice'}
    for item in items:
        temp = item.select('td')
        
        inqLine['dateTime'] = int(datetime.strptime( temp[0].text.strip() , '%Y.%m.%d %H:%M').timestamp())//60
        inqLine['loc'] = temp[1].text.strip()
        inqLine['process'] = temp[2].text.strip()
        inquiry.append(inqLine.copy())
    if len(inquiry) <= 1:
        return {'success': False, 'msg': 'delivery is not finished'}

    result = []
    for line in inquiry[:-1]:
        date = datetime.fromtimestamp(line['dateTime'] * 60)
        prog = f"{max(date.weekday()-3, 0)}T{date.hour // 2}_{line['loc']}_{line['process']}"

        result.append((prog, inquiry[-1]['dateTime'] - line['dateTime']))
    result.append(('lg', result[0][1]))

    return {'success': True, 'res': result }

func = {'cj': cj_inquiry, 'po': po_inquiry, 'hj': hj_inquiry, 'lg': lg_inquiry}

if __name__ == "__main__":
    #print(f'{6892049692080}: {po_inquiry(6892049692080)}')
    print(f'{6892049692081}: {po_inquiry(6892049692081)}')