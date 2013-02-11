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

function setNonSelected(elems){
    $.each(elems, function(){
        this.navelem.removeClass("selected");
        this.elem.hide();
    });
}