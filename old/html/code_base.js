$(document).ready(function(){
	//set navlink_current for the link that points to current page
	$('#navigation li a').each(function(){
		var $href = $(this).attr('href');
		if ( ($href == $page) || ($href == '') ) {
			$(this).addClass('on');
		} else {
			$(this).removeClass('on');
		}
	});
}