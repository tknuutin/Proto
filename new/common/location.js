
removedConnections = [];

function addNewConnection(targetdiv, locationname, locationid){
    if(targetdiv == "connection"){
        var existing_connections = [];
        $("#connections tr:visible").each(function(){
            existing_connections.push(parseInt($(this).find("td").first().attr("data-id"), 10));
        });
        if(existing_connections.indexOf(locationid) < 0 && locationid != parseInt($("#moduleid").text(), 10)){
            $("#connections").show();
            $("table + .d_element_empty").hide();
            
            var removedLocationIds = [];
            $.each(removedConnections, function(){ removedLocationIds.push(this.locfrom_id); });
            
            var indexOfRemovedLocation = removedLocationIds.indexOf(locationid);
            if(indexOfRemovedLocation > -1){
                $("#connections .connection td[data-id=" + locationid + "]").parents(".connection").show();
                removedConnections.splice(indexOfRemovedLocation, 1);
            }
            else{
                $("#connections tbody").append($("#hiddenelements .connection").clone());
                var newconn = $("#connections .connection").last();
                newconn.attr("data-id", "0");
                newconn.find("td").first().attr("data-id", locationid);
                newconn.find(".locationname").text(locationname);
                newconn.find(".locationstatus").text("Unsaved");
                newconn.find(".removebutton").click(function(){
                    //TODO: ask confirmation
                    newconn.remove();
                    hideConnectionsIfNeeded();
                });
            }
        }
    }
}

function hideConnectionsIfNeeded(){
    if($("#connections tr:visible").length <= 1){
        $("#connections").hide();
        $("table + .d_element_empty").show();
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
        //TODO: ask confirmation
        removedConnections.push({
            "connection_id" : parseInt($(this).parents(".connection").attr("data-id"), 10),
            "locfrom_id" : parseInt($(this).parents(".connection").find("td").first().attr("data-id"), 10)
        });
        $(this).parents(".connection").hide();
        hideConnectionsIfNeeded();
    });
    
    $("#mainform").submit(function(){  
        var form = $(this);
        var counter = 1;
        $("#connections .connection[data-id='0']").each(function(){
            form.append($("<input style='display:none;' name='" + "nc_" + counter + "' value='" + $(this).find("td").first().attr("data-id") + "'></input>"));
            counter++;
        });
        
        counter = 1;
        $.each(removedConnections, function(){
            form.append($("<input name='" + "rc_" + counter + "' value='" + this.connection_id + "'></input>"));
            counter++;
        });
    });
});



