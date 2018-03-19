function redirect(){
    var btn = $('.b-btn-close');
    window.location.href = btn.data('url');
}


function refresh_time(){
    var timer = $('#timer');
    time = time - 1;
    timer.html(time);
}

var time = 5;
$(document).ready(function(){
    setInterval(refresh_time, 1000);
    setTimeout(redirect, 5000);
});
