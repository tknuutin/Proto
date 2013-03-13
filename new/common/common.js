function createCookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        var expires = "; expires=" + date.toGMTString();
    } else var expires = "";
    document.cookie = escape(name) + "=" + escape(value) + expires + "; path=/";
}

function readCookie(name) {
    var nameEQ = escape(name) + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return unescape(c.substring(nameEQ.length, c.length));
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name, "", -1);
}

function setHandHover(element){
    element.hover(
        function () {
            $(this).css( 'cursor', 'pointer' );
        },
        function () {
            $(this).css( 'cursor', 'default' );
        }
    );
}

function getQueryContent(key) {
    key = key.replace(/[*+?^$.\[\]{}()|\\\/]/g, "\\$&"); // escape RegEx meta chars
    var match = location.search.match(new RegExp("[?&]"+key+"=([^&]+)(&|$)"));
    return match && decodeURIComponent(match[1].replace(/\+/g, " "));
}

function setNonSelected(elems){
    $.each(elems, function(){
        this.navelem.removeClass("selected");
        this.elem.hide();
    });
}

$(document).ready(function(){
    var loggedIn = $("#navigation .logged_in");
    loggedIn.hide();
    $("#navigation .login").hover(
        function(){ loggedIn.show(); },
        function(){ loggedIn.hide(); }
    );
});