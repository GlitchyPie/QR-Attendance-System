var STUDENT_REGISTRATION_FORM = STUDENT_REGISTRATION_FORM || (function(){
    const naieveEmail = /^([a-z]+)\.(([a-z]+\.?)+)(?<!\.)(@student\.cat\.org\.uk$)?/i
    function registerForm(formId){
        document.addEventListener('DOMContentLoaded',()=>{
            const FORM = document.getElementById(formId);
            const csrf  = FORM.querySelector('input[name="csrfmiddlewaretoken"]');
            const eml   = FORM.querySelector('input[name="student_email"]');
            const fname = FORM.querySelector('input[name="student_fname"]');
            const lname = FORM.querySelector('input[name="student_lname"]');
            const btn   = FORM.querySelector('button[name="submit_student"]');
           
            let fnameFocused = false;
            let lnameFocused = false;

            fname.addEventListener('focus',(event)=>{
                fnameFocused = true;
            });
            lname.addEventListener('focus',(event)=>{
                lnameFocused = true;
            });

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

            function getNames(eml){

            }

            function OnEmailChange(event){
                const regex = naieveEmail.exec(eml.value);
                let btnEnable = false;
                if(regex !== null){
                    if(fname.value.length === 0){
                        fnameFocused = false;
                    }
                    if(fnameFocused == false){
                        fname.value = FirstToUpper(regex[1]);
                    }

                    if(lname.value.length === 0){
                        lnameFocused = false
                    }
                    if(lnameFocused == false){
                        lname.value = regex[2].split('.').map((s)=>FirstToUpper(s)).join(' ');
                    }

                    btnEnable = regex[4]?.toLowerCase() === '@student.cat.org.uk'

                    if(btnEnable){
                        getNames(eml.value)
                    }
                };

                btn.disabled = (!btnEnable);
            }
            
            eml.addEventListener('input', OnEmailChange);
        });
    }
    return {
        register:registerForm
    }
}())

