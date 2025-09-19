document.addEventListener("DOMContentLoaded",()=>{
            const btn1 = document.getElementById("btn-export-today");
            const btn2 = document.getElementById("btn-export-yesterday");
            const btn3 = document.getElementById("btn-view-today");
            const btn4 = document.getElementById("btn-view-yesterday");
            const btn5 = document.getElementById("btn-export-date");
            const btn6 = document.getElementById("btn-view-date");

            const moduleSelect = document.getElementById("select-export-module");
            const classSelect = document.getElementById("select-export-class");
            const picker = document.getElementById("export-date-picker");


            function getPath(action, dte){
                function isValidDate(ob){
                    if(Object.prototype.toString.call(ob) === "[object Date]"){
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
                if(classId != "*"){
                    path = `${path}class/${classId}/`;
                }else if(moduleId != "*"){
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
                classSelect.value = "*";
                goto_view(new Date(picker.value))
                
            }
            function updatClassPicker(event){
                const v = moduleSelect.value;
                if(v == "*"){
                    for (const element of classSelect.children) {
                        element.style.display = "initial";
                    }
                }else{
                    for (const element of classSelect.children) {
                        if(element.value != "*"){
                            if(element.dataset.moduleid != v){
                                element.style.display = "none";
                            }else{
                                element.style.display = "initial";
                            }
                        }
                    }
                }
            }

            updatClassPicker();
            moduleSelect.addEventListener('input', gotoModule);
            classSelect.addEventListener('input',()=>goto_view(new Date(picker.value)));

            btn1.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_export();
            });
            btn2.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_export(-1);
            });

            btn3.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_view();
            });
            btn4.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_view(-1);
            });

            btn5.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_export(-1);
            });
            btn6.addEventListener('click',(event)=>{
                event.preventDefault();
                goto_view(new Date(picker.value));
            });

        });