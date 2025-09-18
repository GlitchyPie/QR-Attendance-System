document.addEventListener("DOMContentLoaded",()=>{
            const btn1 = document.getElementById("btn-export-today");
            const btn2 = document.getElementById("btn-export-yesterday");
            const btn3 = document.getElementById("btn-view-today");
            const btn4 = document.getElementById("btn-view-yesterday");
            const btn5 = document.getElementById("btn-export-date");
            const btn6 = document.getElementById("btn-view-date");

            const classSelect = document.getElementById("select-export-class");
            const picker = document.getElementById("export-date-picker");

            function getPathPrefix(action){
                const classId = classSelect.value;
                let path = "";
                if(classId !== '*'){
                    path = `/class/${classId}/attendance/`
                }else{
                    path = "/class/attendance/";
                }
                path = `${path}${action}/`;
                return path;
            }
            function goto_export(dte){
                let path = getPathPrefix('export');
                path = `${path}${dte.getFullYear()}/${dte.getMonth() + 1}/${dte.getDate()}/`;
                window.location = path;
            }
            function goto_view(dte){
                let path = getPathPrefix('view');
                path = `${path}${dte.getFullYear()}/${dte.getMonth() + 1}/${dte.getDate()}/`;
                window.location = path;
            }

            btn1.addEventListener('click',(event)=>{
                event.preventDefault();
                const D = new Date();
                goto_export(D);
            });
            btn2.addEventListener('click',(event)=>{
                event.preventDefault();
                const D = new Date();
                D.setDate(D.getDate() - 1);
                goto_export(D);
            });

            btn3.addEventListener('click',(event)=>{
                event.preventDefault();
                const D = new Date();
                goto_view(D);
            });
            btn4.addEventListener('click',(event)=>{
                event.preventDefault();
                const D = new Date();
                D.setDate(D.getDate() - 1);
                goto_view(D);
            });

            btn5.addEventListener('click',(event)=>{
                event.preventDefault();
                const D = new Date(picker.value)
                goto_export(D);
            });
            btn6.addEventListener('click',(event)=>{
                event.preventDefault();
                const D = new Date(picker.value)
                goto_view(D);
            });

        });