
$(document).ready(function(){ 
    $("#navigation li").each(function(){ 
        setHandHover($(this));
    });
    
    var helpbox = $(".helpbox");
    $(".helpsubject").hover(function(){
        helpbox.text($(this).find(".element_helptext").html());
    });
    
    var hidden = false;
    var cookiename = "modme_editor_help_show";
    
    if(parseInt(readCookie(cookiename), 10) == 0){
        hidden = true;
        helpbox.hide();
    }
    
    $(".hidehelpbutton").click(function(e){
        e.preventDefault();
        if(!hidden){
            helpbox.hide();
            eraseCookie(cookiename);
            createCookie(cookiename, "0", 1);
            hidden = true;
        }
        else{
            helpbox.show();
            eraseCookie(cookiename);
            createCookie(cookiename, "1", 1);
            hidden = false;
        }
    });
});