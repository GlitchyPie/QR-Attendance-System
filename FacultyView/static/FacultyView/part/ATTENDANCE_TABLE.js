var ATTENDANCE_TABLE = ATTENDANCE_TABLE || (function(){
    const localOpts_time = {
        hour:'2-digit',
        minute: '2-digit'
    }
    let lang;
    GLOBGOR.registerOnLoad(()=>{lang = document.documentElement.lang??'en';});

    function registerPage(){
        GLOBGOR.registerOnLoad(GLOBGOR.format.all);
    }

    return {
        register: registerPage
    }
}());