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

    //### FORMAT ##################################################
    function format_time(elem){
        if((!!elem.dataset) && (!!elem.dataset.isotime)){
            const utcDateStr = elem.dataset.isotime;
            const utcDate = new Date(utcDateStr);
            elem.textContent = utcDate.toLocaleString(lang, localeOpts_times);
        }
    }
    function format_date(elem){
        if((!!elem.dataset) && (!!elem.dataset.isodate)){
            const utcDateStr = elem.dataset.isodate;
            const utcDate = new Date(utcDateStr);
            elem.textContent = utcDate.toLocaleString(lang, localeOpts_YMD);
        }
    }
    function format_opt(elem){
        if((!!elem.dataset) && (!!elem.dataset.isoopt)){
            const utcDateStr = elem.dataset.isoopt;
            const utcDate = new Date(utcDateStr);
            if(!!elem.dataset.localeopts){
                elem.textContent = utcDate.toLocaleString(lang, elem.dataset.localeopts);
            }else{
                elem.textContent = utcDate.toLocaleString(lang);
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

    //### URLS ##################################################
    function serializeForQuery(obj) {
        if(!(!!obj)){return ''}

        return new URLSearchParams(obj).toString();
    }

    //### XHR ##################################################
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

    //### FETCH ##################################################
    function prepareBody(data, headers, useJSON = false) {
        if (!data) return undefined;

        if(typeof data === 'string' || data instanceof String){
            return data
        }else{
            // If already a FormData or URLSearchParams, just return it
            if (data instanceof FormData){
                delete headers['Content-Type'];// Remove explicit Content-Type header for FormData to let browser set boundaries
                return data;
            }else if(data instanceof URLSearchParams){
                headers['Content-Type'] = 'application/x-www-form-urlencoded';
                return data
            }else if(useJSON){
                // JSON body mode
                headers['Content-Type'] = 'application/json';
                return JSON.stringify(data);
            }else{
                // Otherwise, assume plain object → URL-encoded
                headers['Content-Type'] = 'application/x-www-form-urlencoded';
                return new URLSearchParams(data)
            }
        }
    }    
    function createFetch(url, method, readystatechange, customHeaders = undefined) {
        if (typeof readystatechange !== 'function') {
            readystatechange = () => {};
        }

        const xhrLike = {
            readyState: 0,
            status: 0,
            responseText: '',
            response: null,
            responseJSON: null,
            headers: {},
            abortController: new AbortController(),
            redirected: false,
            abort() {
                this.abortController.abort();
            },
            getResponseHeader(name) {
                if (!xhrLike.headers || typeof xhrLike.headers.get !== 'function') return null;
                return xhrLike.headers.get(name);
            }
        };

        xhrLike.send = async function (body) {
            return new Promise(async (resolve, reject) => {
                try {
                    xhrLike.readyState = 1; // OPENED
                    readystatechange(new Event('readystatechange'), xhrLike);

                    const options = {
                        method,
                        headers: customHeaders || {},
                        signal: xhrLike.abortController.signal,
                        redirect: 'follow',
                    };

                    // Only include body for non-GET/HEAD requests
                    if (method !== 'GET' && method !== 'HEAD' && body) {
                        options.body = body;
                    }

                    xhrLike.readyState = 2; // HEADERS_RECEIVED (simulated)
                    readystatechange(new Event('readystatechange'), xhrLike);

                    const response = await fetch(url, options);

                    xhrLike.readyState = 3; // LOADING
                    readystatechange(new Event('readystatechange'), xhrLike);

                    xhrLike.status = response.status;
                    xhrLike.headers = response.headers;
                    xhrLike.redirected = response.redirected;

                    const contentType = response.headers.get('content-type') || '';
                    if (contentType.includes('application/json')) {
                        xhrLike.responseJSON = await response.json();
                        xhrLike.response = xhrLike.responseJSON;
                        xhrLike.responseText = JSON.stringify(xhrLike.responseJSON);
                    } else {
                        xhrLike.responseText = await response.text();
                        xhrLike.response = xhrLike.responseText;
                    }

                    xhrLike.readyState = 4; // DONE
                    readystatechange(new Event('readystatechange'), xhrLike);

                    resolve(xhrLike);
                } catch (err) {
                    xhrLike.status = 0;
                    xhrLike.error = err;
                    xhrLike.readyState = 4;
                    readystatechange(new Event('error'), xhrLike);
                    reject(err);
                }
            });
        };

        return xhrLike;
    }
    function postFetch(url, data, readystatechange, customHeaders = undefined, useJSON = false) {
        const headers = Object.assign(
            { 'Content-Type': 'application/x-www-form-urlencoded' },
            customHeaders || {}
        );

        const xhrLike = createFetch(url, 'POST', readystatechange, headers);
        const body = prepareBody(data, headers, useJSON);
        const promise = xhrLike.send(body);

        return Object.assign(xhrLike, { promise });
    }
    function getFetch(url, data, readystatechange, customHeaders = undefined) {
        let q = '';
        if (data) {
            if (data instanceof URLSearchParams) {
                q = `?${data.toString()}`;
            } else if (typeof data === 'object' && !(data instanceof FormData)) {
                q = `?${serializeForQuery(data)}`;
            }
        }

        const xhrLike = createFetch(`${url}${q}`, 'GET', readystatechange, customHeaders);
        const promise = xhrLike.send();
        return Object.assign(xhrLike, { promise });
    }

    //### COOKIES ##################################################
    function getCookie(name) {
        return document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')?.pop() || ''
    }

    //### REGISTER ##################################################
    function registerOnDomLoad(f){
        if(document.readyState === 'loading'){
            document.addEventListener("DOMContentLoaded",f);
        }else{
            f();
        }
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
        },
        'fetch':{
            'create' : createFetch,
              'post' : postFetch,
               'get' : getFetch,
        },
        'cookies': {
            'get':getCookie
        },
        'registerOnLoad':registerOnDomLoad,
    }
}());