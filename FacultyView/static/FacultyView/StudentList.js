document.addEventListener("DOMContentLoaded",()=>{
    let currentList = document.getElementById('student_present_list');
    let previousResponseHtml = clearWhiteSpace(currentList.parentElement.innerHTML);

    const lookupPath = currentList.dataset.rootpath;

    const l = document.documentElement.lang??'en';
    const localeOpts = {
        hour:'2-digit',
        minute: '2-digit'
    }

    function clearWhiteSpace(s){
        if(s === undefined){return "";}
        return s.replace(/\s+/g,"");
    }

    function formatDates(elem){
        const list = elem??document.getElementById('student_present_list');
        const li_items = list.getElementsByTagName('LI');

        for (const li of li_items){
            const nodes_sname = li.getElementsByClassName("student-name");
            if(!!nodes_sname){
                const node_sname = nodes_sname[0];
                if(!!node_sname){
                    const node_date = node_sname.getElementsByClassName('attendance-date')[0];
                    const utcDateStr = node_date.dataset.isodate;
                    const utcDate = new Date(utcDateStr);
            
                    node_date.innerText = utcDate.toLocaleString(l,localeOpts);
                }
            }
        }                    
    }

    function lookForUpdate(){
        const request = new XMLHttpRequest();
        request.addEventListener("load", XMLHttpRequestLoad);
        request.open("GET", lookupPath);
        request.send();
    }
    
    function XMLHttpRequestLoad(){
        const A = this.responseText;
        const B = clearWhiteSpace(A);
        if(previousResponseHtml != B){
            previousResponseHtml = B
            const parser = new DOMParser();
            const domDoc = parser.parseFromString(A, "text/html");
            //console.log(domDoc);
            const ul = domDoc.getElementById('student_present_list');
            const newUL = ul.cloneNode(true);
            formatDates(newUL);

            currentList.replaceWith(newUL);

            currentList = newUL;
        }
        setTimeout(lookForUpdate, 2000);
    }
    
    setTimeout(lookForUpdate, 2000)

    formatDates();
});