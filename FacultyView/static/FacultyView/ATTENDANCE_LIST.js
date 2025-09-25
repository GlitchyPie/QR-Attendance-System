var ATTENDANCE_LIST = ATTENDANCE_LIST || (function(){

    function serializeForQuery(obj) {
        var str = [];
        for(var p in obj)
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
        return str.join("&");
    }

    function formatDates(li){
        const nodes_sname = li.getElementsByClassName('student-name');
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

    function show_ConfirmDelete(event){
        event.preventDefault()
        const btn = this;
        const container = btn.parentElement;
        if(!!container){
            const btn_delete = container.getElementsByClassName('delete-button icon')[0]
            const btn_yes = container.getElementsByClassName('delete-button yes')[0]
            const btn_no = container.getElementsByClassName('delete-button no')[0]

            btn_delete.style.display = 'none'
            btn_yes.style.display = 'revert'
            btn_no.style.display = 'revert'
        }
    }
    function hide_ConfirmDelete(event){
        event.preventDefault();
        const btn = this;
        const container = btn.parentElement;
        if(!!container){
            const btn_delete = container.getElementsByClassName('delete-button icon')[0]
            const btn_yes = container.getElementsByClassName('delete-button yes')[0]
            const btn_no = container.getElementsByClassName('delete-button no')[0]
            btn_delete.style.display = 'revert'
            btn_yes.style.display = 'none'
            btn_no.
            style.display = 'none'
        }
    }
    
    const localeOpts = {
        hour:'2-digit',
        minute: '2-digit'
    }
    let l;
    document.addEventListener('DOMContentLoaded',()=>{l = document.documentElement.lang??'en';});

    function registerList(listId){
        document.addEventListener('DOMContentLoaded',()=>{
            let currentList = document.getElementById(listId);
            let etag;

            function post_delete(event){
                event.preventDefault();
                const btn = this;
                const deletePath = currentList.dataset.deletepath;
                const refererpath = currentList.dataset.refererpath;
                const csrf = currentList.dataset.csrftoken;

                const xhr = new XMLHttpRequest();
                xhr.open('POST', deletePath, true);
                // Send the proper header information along with the request
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                const queryString = serializeForQuery({
                    'attendance_record':btn.value,
                    'next':refererpath,
                    'csrfmiddlewaretoken':csrf
                });
                xhr.send(queryString);
            }

            function applyDeleteFunctions(li){
                const button_icon = li.getElementsByClassName('delete-button icon')[0];
                const button_yes = li.getElementsByClassName('delete-button yes')[0];
                const button_no = li.getElementsByClassName('delete-button no')[0];

                if(!!button_icon){
                    button_icon.addEventListener('click',show_ConfirmDelete);
                }
                if(!!button_yes){
                    button_yes.addEventListener('click',post_delete);
                }
                if(!!button_no){
                    button_no.addEventListener('click',hide_ConfirmDelete);
                }
            }
            
            function mouseLeftListItem(event){
                hide_ConfirmDelete.call(this.getElementsByTagName('BUTTON')[0], event);
            }
            function applyMouseLeaveFunction(li){          
                li.addEventListener('mouseleave',mouseLeftListItem);
            }

            function processUL(ul){
                const li_items = ul.getElementsByTagName('LI');
                for (const li of li_items){
                    formatDates(li);
                    applyDeleteFunctions(li);
                    applyMouseLeaveFunction(li);
                }         
            }

            function lookForUpdate(){
                const request = new XMLHttpRequest();
                //request.addEventListener('load', lookForUpdateDoUpdate);
                request.addEventListener('readystatechange',(event)=>lookForUpdateReadystateChange(event,request));
                request.open('GET', currentList.dataset.querypath, true);
                if(!!etag){
                    request.setRequestHeader('If-None-Match', etag);
                }
                request.send();
            }
            function lookForUpdateReadystateChange(event,xhr){
                if(xhr.readyState === 4){
                    if(xhr.status === 200){
                        etag = xhr.getResponseHeader("ETag"); // save new ETag
                        lookForUpdateDoUpdate.call(xhr);
                    }else if(xhr.status === 304){

                    }
                    setTimeout(lookForUpdate, 2000);
                }
            }
            function lookForUpdateDoUpdate(){
                const parser = new DOMParser();
                const domDoc = parser.parseFromString(this.responseText, 'text/html');
                const ul = domDoc.getElementsByTagName("UL")[0]; //('student_present_list');
                const newUL = ul.cloneNode(true);

                processUL(newUL);
                currentList.replaceWith(newUL);
                currentList = newUL;

                const alc = currentList.parentElement.querySelector('.attendance-list-count');
                if(!!alc){
                    alc.innerText = currentList.children.length;
                }
            }
            
            setTimeout(lookForUpdate, 2000)

            processUL(currentList);
        });
    }

    return {
        register: registerList
    }
}());

