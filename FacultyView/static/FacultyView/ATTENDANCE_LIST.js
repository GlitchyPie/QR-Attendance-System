var ATTENDANCE_LIST = ATTENDANCE_LIST || (function(){
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

    function registerList(listId){
        document.addEventListener('DOMContentLoaded',()=>{
            let currentList = document.getElementById(listId);
            let etag;
            let last_modified = new Date();

            function post_delete(event){
                event.preventDefault();
                const btn = this;
                const deletePath = currentList.dataset.deletepath;
                const refererpath = currentList.dataset.refererpath;
                const csrf = currentList.dataset.csrftoken;

                GLOBGOR.xhr.post(
                    deletePath,
                    {
                        'attendance_record':btn.value,
                        'next':refererpath,
                        'csrfmiddlewaretoken':csrf
                    }
                )
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
                GLOBGOR.format.all(ul);

                const li_items = ul.getElementsByTagName('LI');
                for (const li of li_items){
                    applyDeleteFunctions(li);
                    applyMouseLeaveFunction(li);
                }         
            }

            function lookForUpdate(){
                GLOBGOR.xhr.get(
                    currentList.dataset.querypath,
                    undefined,
                    lookForUpdateReadystateChange,
                    {
                        'If-None-Match' : etag,
                         'X-list-count' : currentList.children.length,
                        'If-Modified-Since' : last_modified.toUTCString(),
                    }
                )
            }
            function lookForUpdateReadystateChange(event,xhr){
                if(xhr.readyState === 4){
                    if(xhr.status === 200){
                        etag = xhr.getResponseHeader("ETag"); // save new ETag
                        last_modified = new Date();
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

                const alc = currentList.parentElement.querySelector('.attendance-list-count') ?? currentList.parentElement.parentElement.querySelector('.attendance-list-count');

                if(!!alc){
                    alc.innerText = currentList.children.length;
                }
            }
            
            processUL(currentList);
            setTimeout(lookForUpdate, 2000)
        });
    }

    return {
        register: registerList
    }
}());

