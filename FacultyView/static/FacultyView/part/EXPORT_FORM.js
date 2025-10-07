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
            
            const export_dlg_containter = FORM.querySelector('.export-selection-container');
            const export_dlg = export_dlg_containter.querySelector('.export-selection-dlg');
            const cancel_export_btn = export_dlg.querySelector('button[name="btn-cancel-export"]');

            const file_name = export_dlg.querySelector('input[name="export-filename"]');
            const dlg_header = export_dlg.querySelector('.export-selection-dlg-header h4');

            const export_btns = FORM.querySelectorAll('button[name="btn-export"]');
            const view_btns = FORM.querySelectorAll('button[name="btn-view"]');

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

            function GenerateViewAndExportInfo(dte = undefined){
                let today = (dte === 0);

                const classId = classSelect.value;
                const moduleId = moduleSelect.value;

                let file_name = "Attendance Report";
                let title_prefix = '';
                let title_date = '';

                let path = '/faculty/attendance-history/';

                if(classId != '*'){
                    path = `${path}class/${classId}/`;
                    
                    const C = classSelect.querySelector(`[value="${classId}"]`);
                    const M = moduleSelect.querySelector(`[value="${C.dataset.moduleid}"]`);
                    title_prefix = `${M.textContent}-${C.textContent}`

                    file_name = `${file_name}-${title_prefix}`;
                }else if(moduleId != '*'){
                    path = `${path}module/${moduleId}/`;
                    
                    const M = moduleSelect.querySelector(`[value="${moduleId}"]`);
                    title_prefix = `${M.textContent}-All`;

                    file_name = `${file_name}-${title_prefix}`;
                }else{
                    title_prefix = "All"
                    file_name = `${file_name}-All`;
                }

                if(dte === undefined){ //Use current selection
                    const isStd = dateSelectorFieldSet.dataset.isstd;
                    switch(isStd){
                        case '1': //Single date
                            const N = new Date();
                            const D = new Date(datepicker.value);
                            if(!isValidDate(D)){throw Error('Invalid date selected in date picker');}

                            path = `${path}${D.getFullYear()}/${D.getMonth() + 1}/${D.getDate()}/`;
                            
                            title_date = D.toLocaleDateString();
                            file_name = `${file_name}-${D.getFullYear()}-${D.getMonth() + 1}-${D.getDate()}`;
                            break;
                        
                        case '2': //Date range
                            let S = new Date(datepicker_range_start.value);
                            let E = new Date(datepicker_range_end.value);
                            let ttle_S = ""
                            let tlte_E = ""
                            let fnS = ""
                            let fnE = ""
                            if(isValidDate(S)){
                                path = `${path}from/${S.getFullYear()}-${S.getMonth() + 1}-${S.getDate()}/`
                                ttle_S = S.toLocaleDateString();
                                fnS = `${S.getFullYear()}-${S.getMonth() + 1}-${S.getDate()}`;
                            } else {
                                ttle_S = "####";
                                fnS = "####";
                                S = false;
                            }
                            if(isValidDate(E)){
                                path = `${path}to/${E.getFullYear()}-${E.getMonth() + 1}-${E.getDate()}/`
                                tlte_E = E.toLocaleDateString();
                                fnE = `${E.getFullYear()}-${E.getMonth() + 1}-${E.getDate()}`;
                            } else {
                                tlte_E = "####";
                                fnE = "####";
                                E = false;
                            }
                            if((S === false) && (E === false)){throw Error("No dates selected for range");}

                            file_name = `${file_name}-${fnS}_${fnE}`;
                            title_date = `${ttle_S} <> ${tlte_E}`;
                            break;
                        
                        case '3': //Misc manual date
                            const y = parseInt(input_date_year.value);
                            const m = parseInt(input_date_month.value);
                            const d = parseInt(input_date_day.value);
                            title_date = `${y}-`
                            if(!isNaN(y)){
                                path = `${path}${y}/`;
                                if(!isNaN(m)){
                                    path = `${path}${m}/`;
                                    title_date = `${title_date}${m}-`
                                    if(!isNaN(d)){
                                        path = `${path}${d}/`;
                                        title_date = `${title_date}${d}`
                                    }else{
                                        title_date = `${title_date}##`
                                    }
                                }else{
                                    title_date = `${title_date}##-##`;
                                }
                                file_name = `${file_name}-${title_date}`;
                            }else{
                                throw Error("At least year required.")
                            }
                            break;
                        default:
                            throw Error(`Unknown isStd "${isStd}"`)
                    }

                } else {
                    if(Number.isInteger(dte)){ //days from today
                        const O = dte;
                        dte = new Date();
                        dte.setDate(dte.getDate() + O);
                    }
                    if(!isValidDate(dte)){ // Is a date
                        throw Error("Invalid value provided to GenerateViewAndExportInfo.");
                    }else if(today){
                        path = `${path}today/`;
                    }else{
                        path = `${path}${dte.getFullYear()}/${dte.getMonth() + 1}/${dte.getDate()}/`;
                    }
                    title_date = dte.toLocaleDateString();
                    file_name = `${file_name}-${dte.getFullYear()}-${dte.getMonth()}-${dte.getDate()}`;
                }

                return{
                    'title_prefix' : title_prefix,
                      'title_date' : title_date,
                       'view_path' : `${path}view/`,
                            'path' : path,
                       'file_name' : file_name,
                }
                
            }


            function goto_export(dte, format='csv'){
                window.location = getPath(`export-${format}`, 
                                          dte,{
                                            'file_name':file_name.value
                                          });
            }
            function goto_view(dte){
                const path = GenerateViewAndExportInfo(dte).view_path
                window.location = path;
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


            function update_dlg_heading_and_file_name(){
                const context = export_dlg.export_context;
                dlg_header.textContent = `${context.title_prefix} - [${context.title_date}]`;
                file_name.value = context.file_name
            }
            function displayExportDialog(dte){
                export_dlg.export_context = GenerateViewAndExportInfo(dte);
                update_dlg_heading_and_file_name();
                export_dlg_containter.style.display = 'grid';
            }
            function view_btn_click(event, btn){
                try{
                    event.preventDefault();
                    const V = `${btn.value}`;
                    const I = parseInt(V);

                    if(btn.value == 'C'){
                        goto_view(undefined);
                    }else if(!isNaN(I)){
                        goto_view(I);
                    } else {
                        throw Error(`Invalid button value "${V}".`);
                    }                    
                }catch (error){
                    console.log(error);
                    alert(error);
                }

            }
            function export_btn_click(event, btn){
                event.preventDefault();
                const V = `${btn.value}`;
                const I = parseInt(V);

                if(btn.value == 'C'){
                    displayExportDialog(undefined);
                }else if(!isNaN(I)){
                    displayExportDialog(I);
                } else if(V.length >= 3){
                    const q = GLOBGOR.urls.serializeQuery({
                        'file_name' : file_name.value,
                    })
                    window.location = `${export_dlg.export_context.path}export-${V}/?${q}`
                } else {
                    throw Error(`Invalid button value "${V}".`);
                }
            }
            function export_cancel_click(event){
                event.preventDefault();
                export_dlg_containter.style.display = 'none';
            }


            updateClassPicker();
            select_date_fieldset(dateSelectorFieldSet.dataset.isstd);

            //---- Export and view buttons ----//
            for (const view_btn of view_btns) {
                view_btn.addEventListener('click',(event)=>view_btn_click(event, view_btn));
            }
            for (const export_btn of export_btns) {
                export_btn.addEventListener('click',(event)=>export_btn_click(event,export_btn));                
            }
            cancel_export_btn.addEventListener('click',export_cancel_click);

            //---- Fieldset selector buttons ----//
            for (const element of fieldsetSelectorBtns) {
                element.addEventListener('mouseenter',(event)=>fieldSetBtn_mouseEnter(event,element));
                element.addEventListener('mouseleave',(event)=>fieldSetBtn_mouseLeave(event,element));
                element.addEventListener('click',(event)=>fieldSetBtn_click(event,element));
            }
            datepicker.addEventListener('input',()=>goto_view(new Date(datepicker.value))); //Single date picker

            //---- Class / Module selectors ----//
            moduleSelect.addEventListener('input', ()=>{classSelect.value = '*'; goto_view();});
            classSelect.addEventListener('input',()=>goto_view());
            
        });
    }

    return {
        register:registerForm
    }
}());