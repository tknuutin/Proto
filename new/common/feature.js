
function handleLocationSelect(targetname, locationname, locationid){
    if(targetname == "attachment"){
        $("#attachname").val(locationname);
        $("#attachid").val(locationid);
    }
    else{
        console.log("CRITICAL: No suitable target '" + targetname + "'.");
    }
}

$(document).ready(function(){
    $("#feature_attach").fancybox({
        'href' : "/proto/editor/select/location?target=attachment",
        'width' : '500',
        'height' : '350',
        'type' : 'iframe',
        'autoHeight' : false,
        'iframe' : {
            scrolling : 'no',
            preload   : true
        }
    });
});



