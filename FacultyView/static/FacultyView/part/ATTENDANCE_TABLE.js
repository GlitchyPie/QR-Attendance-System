var ATTENDANCE_TABLE = ATTENDANCE_TABLE || (function(){

    function registerPage(){
        GLOBGOR.registerOnLoad(()=>GLOBGOR.format.all());
    }

    return {
        register: registerPage
    }
}());