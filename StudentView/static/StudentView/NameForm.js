document.addEventListener('DOMContentLoaded',()=>{
            const naieveEmail = /^([a-z]+)\.(([a-z]+\.?)+)(?<!\.)(@student\.cat\.org\.uk$)?/i
            const eml   = document.getElementById('student_entry_email');
            const fname = document.getElementById('student_entry_fname');
            const lname = document.getElementById('student_entry_lname');
            const btn   = document.getElementById('submit_student_entry');

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
                };

                btn.disabled = (!btnEnable);
            }
            
            eml.addEventListener('input', OnEmailChange);
        });