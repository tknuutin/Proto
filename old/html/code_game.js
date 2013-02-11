
	var sessionId = 0; //No game started
	var tabents = new Array();
	var tabcmds = new Array();
	var tabwords = new Array("examine", "take", "equip", "unequip", "attack", "eat", "consume", "throw", "grab")
	
	function examinableClicked(name){
		document.getElementById('command').value = "examine " + name;
	}
	
	function setSideElementClickable(elementId, commandName){
		$(elementId).click(function () {
			document.getElementById('command').value = commandName.toLowerCase();
		});
		$(elementId).hover(
			function () {
				$(this).css( 'cursor', 'pointer' );
				$(this).removeClass("sideNormal").addClass("sideHover");
			},
			function () {
				$(this).css( 'cursor', 'default' );
				$(this).removeClass("sideHover").addClass("sideNormal");
			}
		);
	}
	
	function setStatScreenContent(data) {
		var statScreen = $("#stats");
		var elementNumber = 0;
		statScreen.empty();
		$(data).find("command").each(function(){
			var commandName = $(this).find("command_name").text();
			statScreen.append("<a class=\"sideNormal\" id=\"sideCmd" + elementNumber + "\"> COMMAND: "+ commandName + " [" + $(this).find("command_type").text() + "]</a><br/>");
			
			setSideElementClickable("#sideCmd" + elementNumber, commandName);
			tabcmds.push(commandName);
			elementNumber = elementNumber + 1;
		});
		elementNumber = 0;
		
		statScreen.append("<br/>");
		
		$(data).find("trait_name").each(function(){
			var traitName = $(this).text();
			statScreen.append("<a class=\"sideNormal\" id=\"sideTrait" + elementNumber + "\"> TRAIT: "+ traitName + "</a><br/>");
			
			setSideElementClickable("#sideTrait" + elementNumber, "examine trait " + traitName);
			tabents.push(traitName);
			elementNumber = elementNumber + 1;
		});
		elementNumber = 0;
		
		$(data).find("stat").each(function(){
			var statName = $(this).find("stat_name").text();
			statScreen.append("<a class=\"sideNormal\" id=\"sideStat" + elementNumber + "\"> STAT: "+ statName + " (" + $(this).find("stat_value").text() + ")</a><br/>");
			
			setSideElementClickable("#sideStat" + elementNumber, "examine stat " + statName);
			tabents.push(statName);
			elementNumber = elementNumber + 1;
		});
		elementNumber = 0;
		
		$(data).find("skill").each(function(){
			var skillName = $(this).find("skill_name").text();
			statScreen.append("<a class=\"sideNormal\" id=\"sideSkill" + elementNumber + "\"> SKILL: "+ skillName + " (" + $(this).find("skill_value").text() + ")</a><br/>");
			
			setSideElementClickable("#sideSkill" + elementNumber, "examine skill " + skillName);
			tabents.push(skillName);
			elementNumber = elementNumber + 1;
		});
		elementNumber = 0;
		
		$(data).find("item_name").each(function(){
			var itemName = $(this).text();
			statScreen.append("<a class=\"sideNormal\" id=\"sideItem" + elementNumber + "\"> ITEM: "+ itemName + "</a><br/>");
			
			setSideElementClickable("#sideItem" + elementNumber, "examine " + itemName);
			tabents.push(itemName);
			elementNumber = elementNumber + 1;
		});
		
	}
	
	function setInfoScreenContent(data) {
		var infoScreen = $("#info");
		infoScreen.empty();
		infoScreen.append("<a class=\"sideNormal\" id=\"sideName\">Name: " + $(data).find("name").text() + "</a><br/>");
		infoScreen.append("<a class=\"sideNormal\" id=\"sideHealth\">Health: " + $(data).find("health").text() + "</a><br/>");
		infoScreen.append("<a class=\"sideNormal\" id=\"sideExp\">Experience: " + $(data).find("experience").text() + "</a><br/>");
		infoScreen.append("<a class=\"sideNormal\" id=\"sideWeapon\">Weapon: " + $(data).find("weapon").text() + "</a><br/>");
		infoScreen.append("<a class=\"sideNormal\" id=\"sideQuest\">Quest: " + $(data).find("quest").text() + "</a><br/>");
		infoScreen.append("<a class=\"sideNormal\" id=\"sideLocation\">Location: " + $(data).find("location").text() + "</a><br/>");
		infoScreen.append("<a class=\"sideNormal\" id=\"sideTime\">Time: " + $(data).find("time").text() + "</a><br/>");
		setSideElementClickable("#sideName", "examine name");
		setSideElementClickable("#sideHealth", "examine health");
		setSideElementClickable("#sideExp", "examine experience");
		setSideElementClickable("#sideWeapon", "examine " + $(data).find("weapon").text());
		setSideElementClickable("#sideQuest", "examine quest");
		setSideElementClickable("#sideLocation", "examine location");
		setSideElementClickable("#sideTime", "examine time");
	}
	
	function sendCommand() {
		var cmd = document.getElementById('command').value;
			
		//If no game started, set name as Something
		if(sessionId == 0 && cmd == ""){
			cmd="Something";
		}
		else if(cmd == ""){
			cmd="commit suicide";
		}
			
		var query = {
			session : sessionId,
			command : cmd
		};
		
		//make query if command not empty
		$.ajax({
			url: "play.html",
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

	function processData(data){
		//empty tabcomplete entity arrays
		tabent = new Array();
		tabcmd = new Array();
	
		//set info screen content
		setInfoScreenContent(data);
		//set stats screen content
		setStatScreenContent(data);
		
		//set other entities to tab complete arrays
		$(data).find("entity").each(function(){
			tabents.push($(this).text());
		});
		
		//set main screen content
		var mainScreen = $("#main");
		mainScreen.val(mainScreen.val() + "\n" + $("main", data).text());
		mainScreen.scrollTop(mainScreen[0].scrollHeight - mainScreen.height());
		
		//set sessionId
		sessionId = $("id", data).text();
		
		//empty commandline
		$("#command").val("");
	}
	
	function onEnter (e) {
		if(e.which == 13){
			e.preventDefault();
			sendCommand();
		}
	}
	
	function onTab (e) {
		if(e.which == 9){
			e.preventDefault();
			var value = $("#command").val().toLowerCase();
			
			if(value != ""){
				var foundMatch = false;
				
				tabcmds.forEach(function(cmd){
					if(foundMatch == false){
						//alert("value: -" + value + "-. in: " + cmd + ". indexof:" + cmd.indexOf(value));
						//alert("indexof:" + cmd.indexOf(value));
						if(cmd.toLowerCase().indexOf(value) == 0){
							$("#command").val(cmd.toLowerCase());
							//alert(cmd);
							foundMatch = true;
						}
					}
				});
				if(foundMatch == false){
					tabwords.forEach(function(word){
						if(foundMatch == false){
							if(word.toLowerCase().indexOf(value) == 0){
								$("#command").val(word.toLowerCase());
								foundMatch = true;
							}
						}
					});
				}
				if(foundMatch == false){
					words = value.split(" ");
					lastWord = words[words.length - 1].toLowerCase();
					tabents.forEach(function(entity){
						if(foundMatch == false){
							//alert(entity + ", " + entity.indexOf(lastWord));
							if(entity.toLowerCase().indexOf(lastWord) == 0){
								newWord = "";
								for(i=0; i<words.length - 1; i++){
									newWord += words[i] + " ";
								}
								newWord += entity.toLowerCase();
								$("#command").val(newWord);
								foundMatch = true;
							}
						}
					});
				}
			}
		}
	}
	
	var popupWindow;
	
	function popup(mylink, windowname)
	{
		if (! window.focus)return true;
		var href;
		if (typeof(mylink) == 'string')
		   href=mylink;
		else
		   href=mylink.href;
		popupWindow = window.open(href, windowname, 'width=700,height=600,scrollbars=yes');
		return false;
	}
	
	$(document).ready(function(){
		//assign click handler for Enter button
		var enterBtn = document.getElementById('submit');
		enterBtn.onclick = function() { sendCommand(); };
		
		$("#save").fancybox({
				'href' : "savedgames.html?sessionID=" + sessionId,
				'width' : '700',
				'height' : 'auto',
				'autoScale' : false,
				'transitionIn' : 'none',
				'transitionOut' : 'none',
				'type' : 'ajax',
				'hideOnContentClick' : false
		});
		$("#load").fancybox({
				'href' : "loadgame.html?sessionID=" + sessionId,
				'width' : '700',
				'height' : 'auto',
				'autoScale' : false,
				'transitionIn' : 'none',
				'transitionOut' : 'none',
				'type' : 'ajax',
				'hideOnContentClick' : false
		});
		
		
		//assign handler for Enter key on commandline
		$(document).keypress(onEnter);
		$("#command").keydown(onTab);
		$("#command").keyup(function(e){if(e.which == 9){e.preventDefault;}});
		$("#command").keypress(function(e){if(e.which == 9){e.preventDefault;}});
    });