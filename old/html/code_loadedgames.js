var currentRow=-1;

function SelectRow(newRow){
	if(currentRow!=-1){
		$("td").each(function(){
			$(this).css("background", "#FFF");
		});
	}
	
	$("#row_" + newRow).find("td").each(function (){
		$(this).css("background", "#DBDBDB");
	});
		
	var save_name = $('#savedgames tr').eq(newRow).find("td").eq(2).html();
	$("#load_name_input").val(save_name);
	
	currentRow=newRow;
}

function IsSelected()
{
   return currentRow==-1?false:true;
}

function GetSelectedRow()
{
   return currentRow;
}

function sendLoad(){
	var savename = document.getElementById('load_name_input').value;
			
	if(savename != ""){
		var query = {
			session : parent.sessionId,
			savename : savename
		};
		
		$.ajax({
			url: "game/load.html",
			data: query,
			success: function(data){
				message = $(data).find("message").text();
				alert(message);
				parent.jQuery.fancybox.close();
				parent.jQuery("#main").val("");
				parent.processData(data);
			},
			error : function(jqxhr, status, thrown){
				alert("Ajax error! Type: " + status + ". Thrown: " + thrown);
			},
			dataType: "xml"
		});
	}
}
		
$(document).ready(function(){
	
	$("#load_submit").click(function () { sendLoad(); });
	
	$("tr").each(function(){
		$(this).hover(
			function () {
				$(this).css( 'cursor', 'pointer' );
				$(this).removeClass("sideNormal").addClass("sideHover");
			},
			function () {
				$(this).css( 'cursor', 'default' );
				$(this).removeClass("sideHover").addClass("sideNormal");
			}
		);
	});
});