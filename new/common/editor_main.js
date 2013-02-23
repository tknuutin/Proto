
$(document).ready(function(){ 
    $("#navigation li").each(function(){ 
        setHandHover($(this));
    });
    
    $(".helpbox").hide();
    $(".module").focus(function(){
        $(".helpbox").show();
        $(".helpbox").text($(this).next().html());
    });
});