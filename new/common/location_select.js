
function sendSelect(){
    var row = $(".select_content tr.selected");
    if(row.length > 0){
        var locationname = row.find("td").first().text();
        var locationid = parseInt(row.find("td").first().attr("data-id"), 10);
        
        if(locationname != "" && locationid != 0){
            parent.jQuery.fancybox.close();
            parent.addNewConnection("connection", locationname, locationid);
        }
    }
}
		
$(document).ready(function(){
    var table = $(".select_content table");
	var rows = $(".select_content tr").not(".select_content tr:first");
    setHandHover(rows);
    rows.click(function(){
        table.find(".selected").removeClass("selected");
        $(this).addClass("selected");
    });
	$("#select_submit").click(function () { sendSelect(); });
	
});