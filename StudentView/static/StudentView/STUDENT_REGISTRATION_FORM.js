var STUDENT_REGISTRATION_FORM = STUDENT_REGISTRATION_FORM || (function(){
    const naieveEmail = /^([a-z]+)\.(([a-z]+\.?)+)(?<!\.)(@student\.cat\.org\.uk$)?/i

    const HINT_EMPTY = ""
    const HINT_NEED_EMAIL = "<i class='fa-solid fa-square-envelope'></i> Please enter your full student email."        
    const HINT_ALREADY_REGISTERED = "<i class='fa-solid fa-ban'></i> Your attendance has already been registered."
    const HINT_REGISTERED = "<i class='fa-solid fa-check'></i> Your attendance has been registered."
    const HINT_VALIDATING = "<i class='fa-solid fa-hourglass-half'></i> Validating..."
    const HINT_SUBMITTING = "<i class='fa-solid fa-hourglass-half'></i> Submitting..."

    const HINT_VALIDATION_ERROR = "<i class='fa-solid fa-exclamation'></i> A data validation error occured.<br>Check your email address."
    const HINT_ERROR = "<i class='fa-solid fa-bomb'></i> Sorry, something went wrong."


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

    function registerForm(formId){
        document.addEventListener('DOMContentLoaded',()=>{
            const FORM = document.getElementById(formId);
            const action = FORM.action + 'ajax/';

            const csrf  = FORM.querySelector('input[name="csrfmiddlewaretoken"]').value;
            const classId  = FORM.querySelector('input[name="classId"]').value;
            const next = FORM.querySelector('input[name="next"]').value;

            const eml   = FORM.querySelector('input[name="student_email"]');
            const fname = FORM.querySelector('input[name="student_fname"]');
            const lname = FORM.querySelector('input[name="student_lname"]');

            const btn   = FORM.querySelector('button[name="submit_student"]');
            const hint = btn.parentElement.querySelector('.registration-hint');

            let lookupTimeout;

            let fnameFocused = false;
            let lnameFocused = false;

            function studentLookupReadyStateChange(event,xhr){
                hint.innerHTML = HINT_SUBMITTING + ` (${xhr.readyState} / 4 | ${xhr.status})`;
                if(xhr.readyState === 4){ 
                    if (xhr.status === 200){
                        studentLookupSuccessfull.call(xhr);
                    }else {
                        hint.innerHTML = HINT_ERROR;
                    }
                }
            }
            function studentLookupSuccessfull(){
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

                if(btn.disabled == true){
                    hint.innerHTML = HINT_ALREADY_REGISTERED;
                }else{
                    hint.innerHTML = HINT_EMPTY
                }
            }
            function lookupStudent(eml){
                clearTimeout(lookupTimeout);

                const xhr = new XMLHttpRequest();
                xhr.addEventListener('readystatechange',(event)=>studentLookupReadyStateChange(event,xhr));
                xhr.open('POST', '/student/lookup/', true);
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                const queryString = serializeForQuery({
                    'classId' : classId,
                    'csrfmiddlewaretoken':csrf,
                    'student_email':eml
                });
                xhr.send(queryString);
            }
            function validateEmailaddr(event){
                const regex = naieveEmail.exec(eml.value);
                let haveEmail = false;

                if(fname.value.length === 0){
                    fnameFocused = false;
                }
                if(lname.value.length === 0){
                    lnameFocused = false
                }
                if(lookupTimeout != undefined){
                    clearTimeout(lookupTimeout);
                }
                if(regex !== null){
                    if(fnameFocused == false){
                        fname.value = FirstToUpper(regex[1]);
                    }
                    if(lnameFocused == false){
                        lname.value = regex[2].split('.').map((s)=>FirstToUpper(s)).join(' ');
                    }

                    haveEmail = regex[4]?.toLowerCase() === '@student.cat.org.uk'
                }else{
                    if(fnameFocused == false){
                        fname.value = eml.value;
                    }
                    if(lnameFocused == false){
                        lname.value = '';
                    }
                }

                if(haveEmail == false){
                    fname.readOnly = false;
                    lname.readOnly = false;
                    btn.disabled = true;
                    hint.innerHTML = HINT_NEED_EMAIL;
                }else{
                    lookupTimeout = setTimeout(()=>lookupStudent(eml.value),500);
                    hint.innerHTML = HINT_VALIDATING;
                }
            }
            

            function registrationSubmittionReadyStateChange(event,xhr){
                hint.innerHTML = HINT_VALIDATING + ` (${xhr.readyState} / 4 | ${xhr.status})`;
                if(xhr.readyState === 4) {
                    if(xhr.status === 200){
                        registrationSubmittelSuccessfull.call(xhr);
                    }else{
                        hint.innerHTML = HINT_ERROR;
                    }
                }
            }
            function registrationSubmittelSuccessfull(){
                const j = this.responseText;
                const response = JSON.parse(j);

                switch(true){
                    case (response.created):
                        hint.innerHTML = HINT_REGISTERED;
                        break;
                    case (response.validationError):
                        hint.innerHTML = HINT_VALIDATION_ERROR;
                        break;
                    case (response.error):
                        hint.innerHTML = HINT_ERROR;
                        break;
                    default:
                        hint.innerHTML = HINT_ALREADY_REGISTERED;
                }

                eml.readOnly = false;
            }
            function submitRegistration(event){
                event.preventDefault();

                btn.disabled = true;
                eml.readOnly = true;
                fname.readOnly = true;
                lname.readOnly = true;

                const xhr = new XMLHttpRequest();
                xhr.addEventListener('load',(event)=>registrationSubmittionReadyStateChange(event,xhr));
                xhr.open('POST', action, true);
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                const queryString = serializeForQuery({
                    'classId': classId,
                    'csrfmiddlewaretoken':csrf,
                    'student_email':eml.value,
                    'student_fname':fname.value,
                    'student_lname':lname.value
                });
                xhr.send(queryString);
            }

            fname.addEventListener('focus',(event)=>{
                if(fname.readOnly != true){
                    fnameFocused = true;
                }
            });
            lname.addEventListener('focus',(event)=>{
                if(fname.readOnly != true){
                    lnameFocused = true;
                }
            });
            eml.addEventListener('input', validateEmailaddr);

            btn.addEventListener('click',submitRegistration);
        });
    }
    return {
        register:registerForm
    }
}())

