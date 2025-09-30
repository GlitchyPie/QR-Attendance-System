var EXPORT_FORM = (function(){
    
    function isValidDate(ob){
        if(Object.prototype.toString.call(ob) === '[object Date]'){
            if(!isNaN(ob)){
                return true
            }
        }
        return false;
    }

    function registerForm(formId){
        document.addEventListener('DOMContentLoaded',()=>{
            const FORM = document.getElementById(formId);
            
            const btn_view_current = FORM.querySelector('button[name="btn-view-date"]');
            const btn_export_current = FORM.querySelector('button[name="btn-export-date"]');
            
            const btn_view_today = FORM.querySelector('button[name="btn-view-today"]');
            const btn_view_yesterday = FORM.querySelector('button[name="btn-view-yesterday"]');
            
            const btn_export_today = FORM.querySelector('button[name="btn-export-today"]');
            const btn_export_yesterday = FORM.querySelector('button[name="btn-export-yesterday"]');
            
            const dateSelectorFieldSet = FORM.querySelector('.fs-date');
            const fieldsetSelectorBtns = dateSelectorFieldSet.querySelectorAll('button[data-isstd]');
            const fieldsetSelectorDivs = dateSelectorFieldSet.querySelectorAll('div[data-isstd]');
            
            const moduleSelect = FORM.querySelector('select[name="select-export-module"]');
            const classSelect = FORM.querySelector('select[name="select-export-class"]');
            
            const datepicker = FORM.querySelector('input[name="export-date-picker"]');
            
            const datepicker_range_start = FORM.querySelector('input[name="export-date-start-picker"]');
            const datepicker_range_end = FORM.querySelector('input[name="export-date-end-picker"]');

            const input_date_year = FORM.querySelector('input[name="export-date-year"]');
            const input_date_month = FORM.querySelector('input[name="export-date-month"]');
            const input_date_day = FORM.querySelector('input[name="export-date-day"]');
            
            function getPath(action, dte){
                let today = (dte === 0);

                const classId = classSelect.value;
                const moduleId = moduleSelect.value;

                let path = "/attendance/";
                if(classId != '*'){
                    path = `${path}class/${classId}/`;
                }else if(moduleId != '*'){
                    path = `${path}module/${moduleId}/`;
                }

                if(today){
                    path = `${path}today/`;

                }else if(Number.isInteger(dte)){
                    const D = new Date();
                    D.setDate(D.getDate() + dte);
                    path = `${path}${D.getFullYear()}/${D.getMonth() + 1}/${D.getDate()}/`

                }else{
                    const isStd = dateSelectorFieldSet.dataset.isstd;
                    switch(isStd){
                        case '1': //Single date
                            const D = new Date(datepicker.value);
                            if(!isValidDate(D)){throw Error('Invalid date selected in date picker');}
                            path = `${path}${D.getFullYear()}/${D.getMonth() + 1}/${D.getDate()}/`
                            break;
                        
                        case '2': //Date range
                            const S = new Date(datepicker_range_start.value);
                            const E = new Date(datepicker_range_end.value);
                            if(isValidDate(S)){
                                path = `${path}from/${S.getFullYear()}-${S.getMonth() + 1}-${S.getDate()}/`
                            }
                            if(isValidDate(E)){
                                path = `${path}to/${E.getFullYear()}-${E.getMonth() + 1}-${E.getDate()}/`
                            }
                            break;
                        
                        case '3': //Misc manual date
                            const y = parseInt(input_date_year.value);
                            const m = parseInt(input_date_month.value);
                            const d = parseInt(input_date_day.value);
                            if(!isNaN(y)){
                                path = `${path}${y}/`;
                                if(!isNaN(m)){
                                    path = `${path}${m}/`;
                                    if(!isNaN(d)){
                                        path = `${path}${d}/`;
                                    }
                                }
                            }
                            break;

                        default:
                            throw Error(`Unknown isStd "${isStd}"`)
                    }
                }

                path = `${path}${action}/`;

                return path;
            }
            function goto_export(dte){
                window.location = getPath('export-csv',dte);
            }
            function goto_view(dte){
                window.location = getPath('view',dte);
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

            function select_date_fieldset(set){
                dateSelectorFieldSet.dataset.isstd = set
                for (const element of fieldsetSelectorDivs) {
                    element.style.display = (element.dataset.isstd == set)?'initial':'none';
                }
                for (const element of fieldsetSelectorBtns) {
                    element.style.border = (element.dataset.isstd == set)?'1px solid black':'none';
                    fieldSetBtn_setSpanDisplay(element);
                }
            }
            function fieldSetBtn_setSpanDisplay(elm){
                const span = elm.querySelector('span');
                if(elm.isHovered || (elm.dataset.isstd == dateSelectorFieldSet.dataset.isstd)){
                    span.style.display = 'inline';
                }else{
                    span.style.display = 'none';
                }
            }
            function fieldSetBtn_mouseEnter(event, elm){
                elm.isHovered = true;
                if(!!elm.dataset.tm){
                    clearTimeout(elm.dataset.tm);
                    elm.dataset.tm = undefined;
                }
                fieldSetBtn_setSpanDisplay(elm);
            }
            function fieldSetBtn_mouseLeave(event, elm){
                elm.isHovered = false;
                if(elm.dataset.isstd != dateSelectorFieldSet.dataset.isstd){
                    elm.dataset.tm = setTimeout(()=>fieldSetBtn_setSpanDisplay(elm), 150);
                }
            }
            function fieldSetBtn_click(event, elm){
                event.preventDefault();
                select_date_fieldset(elm.dataset.isstd);
            }

            updateClassPicker();
            select_date_fieldset(dateSelectorFieldSet.dataset.isstd);

            btn_export_today.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_export(0);
            });
            btn_export_yesterday.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_export(-1);
            });

            btn_view_today.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_view(0);
            });
            btn_view_yesterday.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_view(-1);
            });

            btn_export_current.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_export();
            });
            btn_view_current.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_view();
            });

            for (const element of fieldsetSelectorBtns) {
                element.addEventListener('mouseenter',(event)=>fieldSetBtn_mouseEnter(event,element));
                element.addEventListener('mouseleave',(event)=>fieldSetBtn_mouseLeave(event,element));
                element.addEventListener('click',(event)=>fieldSetBtn_click(event,element));
            }

            moduleSelect.addEventListener('input', ()=>{classSelect.value = '*'; goto_view();});
            classSelect.addEventListener('input',()=>goto_view());
            datepicker.addEventListener('input',()=>goto_view(new Date(datepicker.value)));
        });
    }

    return {
        register:registerForm
    }
}());