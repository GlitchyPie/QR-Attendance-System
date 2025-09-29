var ATTENDANCE_TABLE = ATTENDANCE_TABLE || (function(){
    const localeOpts = {
        hour:'2-digit',
        minute: '2-digit'
    }
    let lang;
    document.addEventListener('DOMContentLoaded',()=>{lang = document.documentElement.lang??'en';});

    function registerPage(){
        document.addEventListener('DOMContentLoaded',()=>{
            const cells = document.querySelectorAll('table.attendance-table td[data-ISODate]');

            for (const node_date of cells) {
                const utcDateStr = node_date.dataset.isodate;
                const utcDate = new Date(utcDateStr);
                node_date.innerText = utcDate.toLocaleString(lang,localeOpts);
            }

        });
    }

    return {
        register: registerPage
    }
}());