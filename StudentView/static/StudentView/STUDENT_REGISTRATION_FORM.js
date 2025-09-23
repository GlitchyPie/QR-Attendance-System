var STUDENT_REGISTRATION_FORM = STUDENT_REGISTRATION_FORM || (function(){
    const naieveEmail = /^([a-z]+)\.(([a-z]+\.?)+)(?<!\.)(@student\.cat\.org\.uk$)?/i
    function registerForm(formId){

        function FirstToUpper(s){
            let t = s;
            if(s === undefined){
                return s;
            }else if(s.length === 1){
                t = s.toUpperCase();
            } else {
                const u = s.substring(0,1);
                const v = s.substring(1);
                t = u.toUpperCase() + v.toLowerCase();
            }
            return t;
        }
        function serializeForQuery(obj) {
            var str = [];
            for(var p in obj)
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
            return str.join("&");
        }

        document.addEventListener('DOMContentLoaded',()=>{
            const FORM = document.getElementById(formId);
            const csrf  = FORM.querySelector('input[name="csrfmiddlewaretoken"]');
            const clasId  = FORM.querySelector('input[name="classId"]');
            const eml   = FORM.querySelector('input[name="student_email"]');
            const fname = FORM.querySelector('input[name="student_fname"]');
            const lname = FORM.querySelector('input[name="student_lname"]');
            const btn   = FORM.querySelector('button[name="submit_student"]');
           
            let lookupTimeout;

            let fnameFocused = false;
            let lnameFocused = false;

            function studentLookedUp(){
                const j = this.responseText;
                const response = JSON.parse(j);
                const student = response.student;
                if(!!student.found){
                    fname.value = student.fname;
                    lname.value = student.lname;

                    fname.readOnly = true;
                    lname.readOnly = true;

                    btn.disabled = student.isPresent;
                }else{
                    fname.readOnly = false;
                    lname.readOnly = false;

                    btn.disabled = false;
                }
            }

            function lookupStudent(eml){
                clearTimeout(lookupTimeout);

                const xhr = new XMLHttpRequest();
                xhr.addEventListener('load',studentLookedUp);
                xhr.open('POST', '/student/lookup/', true);
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                const queryString = serializeForQuery({
                    'student_email':eml,
                    'csrfmiddlewaretoken':csrf.value,
                    'classId' : clasId.value
                });
                xhr.send(queryString);
            }

            function OnEmailChange(event){
                const regex = naieveEmail.exec(eml.value);
                let btnEnable = false;

                if(fname.value.length === 0){
                    fnameFocused = false;
                }
                if(lname.value.length === 0){
                    lnameFocused = false
                }
                if(lookupTimeout != undefined){
                    clearTimeout(lookupTimeout);
                }
                if(eml.value == ''){
                    if(fnameFocused == false){
                        fname.value = '';
                    }
                    if(lnameFocused == false){
                        lname.value = '';
                    }
                }else if(regex !== null){
                    
                    if(fnameFocused == false){
                        fname.value = FirstToUpper(regex[1]);
                    }
                    if(lnameFocused == false){
                        lname.value = regex[2].split('.').map((s)=>FirstToUpper(s)).join(' ');
                    }

                    btnEnable = regex[4]?.toLowerCase() === '@student.cat.org.uk'

                    if(btnEnable){
                        lookupTimeout = setTimeout(()=>lookupStudent(eml.value),500);
                    }
                }else{
                    if(fnameFocused == false){
                        fname.value = eml.value;
                    }
                    if(lnameFocused == false){
                        lname.value = '';
                    }
                };

                if(btnEnable == false){
                    fname.readOnly = false;
                    lname.readOnly = false;
                    btn.disabled = true;
                }
            }
            

            fname.addEventListener('focus',(event)=>{
                if(this.readOnly == false){
                    fnameFocused = true;
                }
            });
            lname.addEventListener('focus',(event)=>{
                if(this.readOnly == false){
                    lnameFocused = true;
                }
            });
            eml.addEventListener('input', OnEmailChange);
        });
    }
    return {
        register:registerForm
    }
}())

