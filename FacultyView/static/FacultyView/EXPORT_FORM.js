var EXPORT_FORM = (function(){
    function registerForm(formId){
        document.addEventListener('DOMContentLoaded',()=>{
            const FORM = document.getElementById(formId);
            const btn_export_today = FORM.querySelector('button[name="btn-export-today"]');
            const btn_export_yesterday = FORM.querySelector('button[name="btn-export-yesterday"]');
            const btn_view_today = FORM.querySelector('button[name="btn-view-today"]');
            const btn_view_yesterday = FORM.querySelector('button[name="btn-view-yesterday"]');
            const btn_export_current = FORM.querySelector('button[name="btn-export-date"]');
            const btn_view_current = FORM.querySelector('button[name="btn-view-date"]');

            const moduleSelect = FORM.querySelector('select[name="select-export-module"]');
            const classSelect = FORM.querySelector('select[name="select-export-class"]');
            const picker = FORM.querySelector('input[name="export-date-picker"]');

            function getPath(action, dte){
                function isValidDate(ob){
                    if(Object.prototype.toString.call(ob) === '[object Date]'){
                        if(!isNaN(ob)){
                            return true
                        }
                    }
                    return false;
                }

                if(Number.isInteger(dte)){
                    const D = new Date()
                    D.setDate(D.getDate() + dte);
                    dte = D
                }else if(!isValidDate(dte)){
                    dte = new Date();
                }
                const classId = classSelect.value;
                const moduleId = moduleSelect.value;

                let path = "/attendance/";
                if(classId != '*'){
                    path = `${path}class/${classId}/`;
                }else if(moduleId != '*'){
                    path = `${path}module/${moduleId}/`;
                }

                path = `${path}${dte.getFullYear()}/${dte.getMonth() + 1}/${dte.getDate()}/${action}/`;

                return path;
            }
            function goto_export(dte){
                window.location = getPath('export',dte);
            }
            function goto_view(dte){
                window.location = getPath('view',dte);
            }
            function gotoModule(event){
                classSelect.value = '*';
                goto_view(new Date(picker.value))  
            }
            function updateClassPicker(event){
                const v = moduleSelect.value;
                if(v == '*'){
                    for (const element of classSelect.children) {
                        element.style.display = 'initial';
                    }
                }else{
                    for (const element of classSelect.children) {
                        if(element.value != '*'){
                            if(element.dataset.moduleid != v){
                                element.style.display = 'none';
                            }else{
                                element.style.display = 'initial';
                            }
                        }
                    }
                }
            }

            updateClassPicker();

            btn_export_today.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_export();
            });
            btn_export_yesterday.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_export(-1);
            });

            btn_view_today.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_view();
            });
            btn_view_yesterday.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_view(-1);
            });

            btn_export_current.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_export(new Date(picker.value));
            });
            btn_view_current.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_view(new Date(picker.value));
            });

            moduleSelect.addEventListener('input', gotoModule);
            classSelect.addEventListener('input',()=>goto_view(new Date(picker.value)));
            picker.addEventListener('input',()=>goto_view(new Date(picker.value)));
        });
    }

    return {
        register:registerForm
    }
}());