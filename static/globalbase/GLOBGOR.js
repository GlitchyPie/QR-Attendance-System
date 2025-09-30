var GLOBGOR = GLOBGOR || (function(){
    const localeOpts_times = {
        hour:'2-digit',
        minute: '2-digit'
    }
    const localeOpts_YMD = {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
    }
    let lang;
    document.addEventListener('DOMContentLoaded',()=>{lang = document.documentElement.lang??'en';});

    function format_time(elem){
        if((!!elem.dataset) && (!!elem.dataset.isotime)){
            const utcDateStr = elem.dataset.isotime;
            const utcDate = new Date(utcDateStr);
            elem.innerText = utcDate.toLocaleString(lang, localeOpts_times);
        }
    }
    function format_date(elem){
        if((!!elem.dataset) && (!!elem.dataset.isodate)){
            const utcDateStr = elem.dataset.isodate;
            const utcDate = new Date(utcDateStr);
            elem.innerText = utcDate.toLocaleString(lang, localeOpts_YMD);
        }
    }
    function format_opt(elem){
        if((!!elem.dataset) && (!!elem.dataset.isoopt)){
            const utcDateStr = elem.dataset.isoopt;
            const utcDate = new Date(utcDateStr);
            if(!!elem.dataset.localeopts){
                elem.innerText = utcDate.toLocaleString(lang, elem.dataset.localeopts);
            }else{
                elem.innerText = utcDate.toLocaleString(lang);
            }
        }
    }
    function format_dates_times(context){
        const c = context ?? document;
        const times = c.querySelectorAll('*[data-ISOTime');
        const dates = c.querySelectorAll('*[data-ISODate');
        const customs = c.querySelectorAll('*[data-ISOOpt');
        times.forEach(format_time);
        dates.forEach(format_date);
        customs.forEach(format_opt);
    }

    function serializeForQuery(obj) {
        var str = [];
        for(var p in obj){
            if(!!obj){
                str.push(`${encodeURIComponent(p)}=${encodeURIComponent(obj[p])}`);
            }else{
                str.push(`${encodeURIComponent(p)}=`);
            }
        }
        return str.join("&");
    }

    function createXHR(url, method, readystatechange, customHeaders = undefined){
        const xhr = new XMLHttpRequest();
        if(!(!!readystatechange)){
            readystatechange = ()=>{}
        }
        xhr.addEventListener('readystatechange',(event)=>readystatechange(event,xhr));
        xhr.open(method, url, true);

        if(!!customHeaders){
            for(var p in customHeaders)
                xhr.setRequestHeader(p, customHeaders[p]);
        }
        return xhr;
    }
    function postXHR(url, data, readystatechange, customHeaders = undefined){
        const xhr = createXHR(url, 'POST', readystatechange, customHeaders);
        
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

        if(!!data){
            const q = serializeForQuery(data);
            xhr.send(q);
        } else {
            xhr.send();
        }
        return xhr;
    }
    function getXHR(url, data, readystatechange, customHeaders = undefined){
        let q = '';
        if(!!data){
            q = `?${serializeForQuery(data)}`;
        }

        const xhr = createXHR(`${url}${q}`, 'GET', readystatechange, customHeaders);
        xhr.send(q);

        return xhr;
    }

    return {
        'format':{
            'date' : format_date,
            'time' : format_time,
             'all' : format_dates_times,
        },
        'urls': {
            'serializeQuery' : serializeForQuery,
        },
        'xhr': {
            'create' : createXHR,
              'post' : postXHR,
               'get' : getXHR,
        }
    }
}());