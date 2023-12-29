"use strict";

const axios = require("axios");
const iconv = require('iconv-lite');

async function cj(invoice) {
    const html = await axios.get(`http://nplus.doortodoor.co.kr/web/detail.jsp?slipno=${invoice}`, {
        responseType: 'arraybuffer',
    });
    
    const content = iconv.decode(html.data, 'euc-kr').toString();
    const tableList = content.split('<tr')
    var inquiry = [];

    for (var i = 11;i+1 < tableList.length;i+=2){
        var timeList = tableList[i].split('&nbsp');
        var locList = tableList[i+1].split('&nbsp');

        inquiry.push({
            'location': locList[1].slice(1), 
            'status': locList[5].slice(1),
            'time': `${timeList[1].slice(1)} ${timeList[3].slice(1, -3)}`
        });
    }
    return inquiry;
}
async function po(invoice) {
    const html = await axios.get(`https://service.epost.go.kr/trace.RetrieveDomRigiTraceList.comm?sid1=${invoice}`, {
        responseType: 'arraybuffer',
    });
    
    const content = iconv.decode(html.data, 'utf-8').toString();
    const tableList = content.split('<tr')
    var inquiry = [];
    if (tableList.length <= 5){ return inquiry; }

    for (var i = 4;i < tableList.length;i++){
        var locStatus = tableList[i].split('<td>')[3].split('</')[0]
        
        inquiry.push({
            'location': locStatus.split('>')[locStatus.split('>').length-1], 
            'status': locStatus.split('\'')[1],
            'time': `${tableList[i].split('<td>')[1].split('</')[0].split('.').join('-')} ${tableList[i].split('<td>')[2].split('</')[0]}`
        });
    }
    inquiry.reverse();
    return inquiry;
}
async function lg(invoice) {
    const html = await axios.get(`https://www.ilogen.com/web/personal/trace/${invoice}`, {
        responseType: 'arraybuffer',
    });
    
    const content = iconv.decode(html.data, 'utf-8').toString();
    const tableList = content.split('<tr')
    var inquiry = []
    if (tableList.length <= 7){ return inquiry; }

    for (var i = 7;i < tableList.length-3;i++){
        const values = tableList[i].split('<td>').slice(1, 4);
        
        inquiry.push({
            'location': values[1].split('</')[0], 
            'status': values[2].split('\n')[0],
            'time': values[0].split('</')[0].split('.').join('-')
        });
    }
    inquiry.reverse();
    return inquiry;
}
async function hj(invoice) {
    const html = await axios.get(`https://www.hanjin.com/kor/CMS/DeliveryMgr/WaybillResult.do?mCode=MN038&schLang=KR&wblnumText2=${invoice}`, {
        responseType: 'arraybuffer',
    });
    
    const content = iconv.decode(html.data, 'utf-8').toString();
    const tableList = content.split('tbody>')[3].split('<tr');
    var inquiry = []

    for (var i = 1;i < tableList.length;i++){
        const values = tableList[i].split('<td').slice(1, 6);
        var status = '이동'
        if(values[3].includes('접수')) { status = '접수'; }
        else if (values[3].includes('입고')) { status = '입고'; }
        else if (values[3].includes('준비')) { status = '배송준비'; }
        else if (values[3].includes('출발')) { status = '배송출발'; }
        else if (values[3].includes('완료')) { status = '배송완료'; }
        
        inquiry.push({
            'location': values[2].slice(values[2].indexOf('>')+1, values[2].indexOf('</td>')), 
            'status': status,
            'time': values[0].slice(values[0].indexOf('>')+1, values[0].indexOf('</td>')) + ' ' + values[1].slice(values[1].indexOf('>')+1, values[1].indexOf('</td>'))
        });
    }
    inquiry.reverse();
    return inquiry;
}