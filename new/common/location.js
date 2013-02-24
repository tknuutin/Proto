
function addNewConnection(targetdiv, locationname, locationid){
    if(targetdiv == "connection"){
        var existing_connections = [];
        $("#connections tr").each(function(){
            existing_connections.push(parseInt($(this).find("td").first().attr("data-id"), 10));
        });
        if(existing_connections.indexOf(locationid) < 0 && locationid != parseInt($("#moduleid").text(), 10)){
            console.log("joo");
            $("#connections tbody").append($("#hiddenelements .connection").clone());
            var newconn = $("#connections .connection").last();
            newconn.find("td").first().attr("data-id", locationid);
            newconn.find(".locationname").text(locationname);
            newconn.find(".locationstatus").text("Unsaved");
            newconn.find(".removebutton").click(function(){
                newconn.remove();
            });
        }
    }
}

$(document).ready(function(){
    $("#connection_create").fancybox({
        'href' : "/proto/editor/select/location",
        'width' : '500',
        'height' : '350',
        'type' : 'iframe',
        'autoHeight' : false,
        'iframe' : {
            scrolling : 'no',
            preload   : true
        }
    });
    $(".moduleinfo .connection .removebutton").click(function(){
        alert("trying to remove the location with id: " + $(this).parents(".connection").attr("data-id"));
    });
});