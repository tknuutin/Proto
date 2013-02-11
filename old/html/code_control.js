
//if boolean enabled is true, site feature will be thought of enabled, and thus "Enable" button will be disabled and the "Disable" button disabled
function siteFeatureStatus(name, enabled){
	$('#site_' + name + '_enable').attr("disabled", enabled);
	$('#site_' + name + '_disable').attr("disabled", !enabled);
}

function checkSiteFeatureFromXml(data, feature){
	if($(data).find(feature).text() == "1"){ 
		siteFeatureStatus(feature, true);
	}
	else{ 
		siteFeatureStatus(feature, false);
	}
}

function updateSiteStatus(featureName){
	$.ajax({
		url: "control_info.html",
		data : { toggleFeature : featureName },
		success: function(data){
			if ($(data).find("error").length != 0){
				alert($(data).find("error").text());
			}
			else{
				checkSiteFeatureFromXml(data, "play");
				checkSiteFeatureFromXml(data, "unver");
				checkSiteFeatureFromXml(data, "designer");
				checkSiteFeatureFromXml(data, "publish");
				checkSiteFeatureFromXml(data, "register");
			}
		},
		error : function(jqxhr, status, thrown){
			alert("Ajax error! Type: " + status + ". Thrown: " + thrown);
		},
		dataType: "xml"
	});
}

$(document).ready(function(){
	updateSiteStatus("");
	
	$('#site_play_enable').click(function(){updateSiteStatus("play")});
	$('#site_unver_enable').click(function(){updateSiteStatus("unver")});
	$('#site_designer_enable').click(function(){updateSiteStatus("designer")});
	$('#site_publish_enable').click(function(){updateSiteStatus("publish")});
	$('#site_register_enable').click(function(){updateSiteStatus("register")});
	$('#site_play_disable').click(function(){updateSiteStatus("play")});
	$('#site_unver_disable').click(function(){updateSiteStatus("unver")});
	$('#site_designer_disable').click(function(){updateSiteStatus("designer")});
	$('#site_publish_disable').click(function(){updateSiteStatus("publish")});
	$('#site_register_disable').click(function(){updateSiteStatus("register")});
});