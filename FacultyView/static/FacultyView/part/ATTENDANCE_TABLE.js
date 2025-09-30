var ATTENDANCE_TABLE = ATTENDANCE_TABLE || (function(){
    const localOpts_time = {
        hour:'2-digit',
        minute: '2-digit'
    }
    let lang;
    document.addEventListener('DOMContentLoaded',()=>{lang = document.documentElement.lang??'en';});

    function registerPage(){
        document.addEventListener('DOMContentLoaded',()=>{
            GLOBGOR.format.all();
        });
    }

    return {
        register: registerPage
    }
}());