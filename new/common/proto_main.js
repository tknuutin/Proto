var sessionId = 0; //No game started

function processData(data){
    //set main screen content
    $("line", data).each(function(){
        $("#game_screen p").last().after("<p>" + $(this).text() + "</p>");
    });
    $("#game_input input").val("");
    var mainscreen = $("#game_screen")
    mainscreen.scrollTop(mainscreen[0].scrollHeight - mainscreen.height());
    
    //set sessionId
    sessionId = $("uid", data).text();
}

function sendCommand() {
    var cmd = $("#game_input input").val();
    
        
    //If no game started, set name as Something
    if(sessionId == 0 && cmd == ""){
        cmd="Something";
    }
    else if(cmd == ""){
        cmd="commit suicide";
    }
    $("#game_screen p").last().after("<p>>" + cmd + "</p>");
        
    var query = {
        session : sessionId,
        command : cmd
    };
    
    //make query if command not empty
    $.ajax({
        url: "/proto/play.html",
        data: query,
        success: function(data){
            if ($(data).find("error").length != 0){
                alert($(data).find("error").text());
            }
            else{
                processData(data);
            }
        },
        error : function(jqxhr, status, thrown){
            alert("Ajax error! Type: " + status + ". Thrown: " + thrown);
        },
        dataType: "xml"
    });
}

function onEnter (e) {
    if(e.which == 13){
        e.preventDefault();
        sendCommand();
    }
}

$(document).ready(function(){
    $("#game_input input").keypress(onEnter);
    
    var elems = [{"navelem" : $("#nav_about"), "elem" : $("#about")}, 
                 {"navelem" : $("#nav_game"), "elem" : $("#game")}, 
                 {"navelem" : $("#nav_help"), "elem" : $("#help")}];
                 
    $.each(elems, function(){
        setHandHover(this.navelem);
        var obj = this;
        obj.navelem.click(function(){
            setNonSelected(elems);
            obj.navelem.addClass("selected");
            obj.elem.show();
        });
    });
    
    var ginput = $("#game_input input")
    var cval = ginput.val();
    ginput.focus().val(cval);
    
    var navigation = $("#navigation");
    var navenable = $("#navigationtoggle .enabled");
    var navdisable = $("#navigationtoggle .disabled");
    var navtoggle = $("#navigationtoggle");
    var navigationhover = $("#navigationhover");
    navdisable.show();
    var navdisabled = false;
    setHandHover(navtoggle);
    
    navtoggle.click(function(){
        if(navdisabled){
            navigation.show();
            navigationhover.unbind('mouseenter mouseleave');
            navdisabled = false;
            navenable.hide();
            navdisable.show();
        }
        else{
            navigation.hide();
            navigationhover.hover(
                function(){ 
                    navtoggle.show(); 
                },
                function(){ 
                    navtoggle.hide();
                }
            );
            navenable.show();
            navdisable.hide();
            navdisabled = true;
        }
    });
    
    
    
});