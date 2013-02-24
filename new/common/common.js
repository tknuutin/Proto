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