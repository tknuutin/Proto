

function addElementToTable(table_name, add_str, update_func){
	$("div#" + table_name + " > span > table tr:last").after(add_str);
	
	$("div#" + table_name + " > span > table tr:last > td > input.sub_element_remove").click(function(){
		$(this).parent().parent().next().remove();
		$(this).parent().parent().remove();
		update_func(table_name);
	})
	$("div#" + table_name + " > span > table tr:last").after("<tr><td><hr/></td></tr>");
	update_func(table_name);
}

function updateParNums(table_name){
	$("#" + table_name + " > span > table > tbody > tr > td > textarea.sub_paragraph").each(function(index){
		num = index + 1;
		$(this).attr("id", table_name + "_par_" + num);
		$(this).attr("placeholder", "Paragraph " + num);
	});
}
function updateDmgNums(table_name){
	$("#" + table_name + " > span > table > tbody > tr.dmg_event").each(function(index){
		num = index + 1;
		$(this).attr("id", table_name + "_dmg_" + num);
	});
}
function updateAttrNums(table_name){
	$("#" + table_name + " > span > table > tbody > tr.attr_event").each(function(index){
		num = index + 1;
		$(this).attr("id", table_name + "_attr_" + num);
	});
}

function showDescriptionChoice(){
	var choice = $("input[@name=desc_type]:checked").val()
	if(choice == "sim"){
		$("#choice_ft_simple").show();
		$("#choice_ft_complex").hide();
	}
	else if(choice == "com"){
		$("#choice_ft_simple").hide();
		$("#choice_ft_complex").show();
	}
	else if(choice == "non"){
		$("#choice_ft_simple").hide();
		$("#choice_ft_complex").hide();
	}
}

$(document).ready(function(){
	$('input[name="desc_type"][value="sim"]').attr("checked", "checked");
	showDescriptionChoice();
	$('input[name="desc_type"]').each(function(){$(this).change(function(){showDescriptionChoice();});});

	$("#first_time_add_par").click(function(){
		add_str = "<tr><td>" + $("span.paragraph_event").html() + "</td><td>" + $("span.remove_button_template").html() +"</td></tr>"
		addElementToTable("first_time", add_str, updateParNums)
	});
	
	$("#first_time_add_dmg").click(function(){
		add_str = "<tr class=\"dmg_event\"><td>" + $("span.damage_event").html() + "</td><td>" + $("span.remove_button_template").html() +"</td></tr>"
		addElementToTable("first_time", add_str, updateDmgNums)
	});
	
	$("#first_time_add_attr").click(function(){
		add_str = "<tr class=\"attr_event\"><td>" + $("span.attribute_event").html() + "</td><td>" + $("span.remove_button_template").html() +"</td></tr>"
		addElementToTable("first_time", add_str, updateAttrNums)
	});
});