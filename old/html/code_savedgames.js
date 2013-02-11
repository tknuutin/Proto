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
	$("#save_name_input").val(save_name);
	
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

function sendSave(){
	if (parent.sessionId != 0){
		var savename = document.getElementById('save_name_input').value;
			
		//If no savename specified, set it as "something"
		if(savename == ""){
			savename="Something";
		}
		
		
		var query = {
			session : parent.sessionId,
			savename : savename
		};
		
		$.ajax({
			url: "game/save.html",
			data: query,
			success: function(data){
				message = $(data).find("save_response").text();
				alert(message);
				parent.jQuery.fancybox.close();
			},
			error : function(jqxhr, status, thrown){
				alert("Ajax error! Type: " + status + ". Thrown: " + thrown);
			},
			dataType: "xml"
		});
	}
	else{
		alert("No game started!");
	}
	
}
		
$(document).ready(function(){
	
	$("#save_submit").click(function () { sendSave(); });
	
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