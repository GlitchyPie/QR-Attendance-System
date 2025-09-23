var ATTENDANCE_LIST = ATTENDANCE_LIST || (function(){
    function registerList(listId){
        document.addEventListener('DOMContentLoaded',()=>{
            let currentList = document.getElementById(listId);
            let previousResponseHtml = clearWhiteSpace(currentList.parentElement.innerHTML);

            const l = document.documentElement.lang??'en';
            const localeOpts = {
                hour:'2-digit',
                minute: '2-digit'
            }

            function clearWhiteSpace(s){
                if(s === undefined){return '';}
                return s.replace(/\s+/g,'');
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

            function confirmDelete(event){
                event.preventDefault()
                const btn = this;
                const container = btn.parentElement;
                const btn_delete = container.getElementsByClassName('delete-button icon')[0]
                const btn_yes = container.getElementsByClassName('delete-button yes')[0]
                const btn_no = container.getElementsByClassName('delete-button no')[0]

                btn_delete.style.display = 'none'
                btn_yes.style.display = 'revert'
                btn_no.style.display = 'revert'
            }
            function hideConfirmDelete(event){
                event.preventDefault();
                const btn = this;
                const container = btn.parentElement;
                const btn_delete = container.getElementsByClassName('delete-button icon')[0]
                const btn_yes = container.getElementsByClassName('delete-button yes')[0]
                const btn_no = container.getElementsByClassName('delete-button no')[0]
                btn_delete.style.display = 'revert'
                btn_yes.style.display = 'none'
                btn_no.style.display = 'none'
            }
            function performDelete(event){
                event.preventDefault();
                const btn = this;
                const deletePath = currentList.dataset.deletepath;
                const refererpath = currentList.dataset.refererpath;
                const csrf = currentList.dataset.csrftoken;

                const xhr = new XMLHttpRequest();
                xhr.open('POST', deletePath, true);
                // Send the proper header information along with the request
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                xhr.send(`attendance_record=${btn.value}&next=${encodeURIComponent(refererpath)}&csrfmiddlewaretoken=${encodeURIComponent(csrf)}`);
            }
            function applyDeleteFunctions(li){
                const button_icon = li.getElementsByClassName('delete-button icon')[0];
                const button_yes = li.getElementsByClassName('delete-button yes')[0];
                const button_no = li.getElementsByClassName('delete-button no')[0];

                if(!!button_icon){
                    button_icon.addEventListener('click',confirmDelete);
                }
                if(!!button_yes){
                    button_yes.addEventListener('click',performDelete);
                }
                if(!!button_no){
                    button_no.addEventListener('click',hideConfirmDelete);
                }
            }
            
            function mouseLeftListItem(event){
                hideConfirmDelete.call(this.getElementsByTagName('BUTTON')[0], event);
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
                request.addEventListener('load', XMLHttpRequestLoad);
                request.open('GET', currentList.dataset.querypath, true);
                request.send();
            }
            
            function XMLHttpRequestLoad(){
                const parser = new DOMParser();
                const domDoc = parser.parseFromString(this.responseText, 'text/html');
                const ul = domDoc.getElementsByTagName("UL")[0]; //('student_present_list');
                const newUL = ul.cloneNode(true);
                
                currentList.dataset.deletepath = newUL.dataset.deletepath;
                currentList.dataset.refererpath = newUL.dataset.refererpath;
                currentList.dataset.csrftoken = newUL.dataset.csrftoken;

                //Check if the list itself has changed in any way
                const A = clearWhiteSpace(newUL.innerHTML);
                const B = previousResponseHtml;
                if(A != B){
                    previousResponseHtml = A;
                    processUL(newUL);
                    currentList.replaceWith(newUL);
                    currentList = newUL;
                }
                setTimeout(lookForUpdate, 2000);
            }
            
            
            setTimeout(lookForUpdate, 2000)

            processUL(currentList);
        });
    }

    return {
        register: registerList
    }
}());

