//rewrite url
function rewrite_url(id){
	if(location.href.indexOf("/wps/portal")>-1){
		$(''+id+' a').each(function(){
			var href = $(this).attr('href');
			if(href.indexOf("/wps/myportal")>-1){
				$(this).attr('href', href.replace('/wps/myportal','/wps/portal'));
			}
		});
	} else{
		$(''+id+' a').each(function(){
			var href = $(this).attr('href');
			if(href.indexOf("/wps/portal")>-1){
				$(this).attr('href', href.replace('/wps/portal','/wps/myportal'));				
			}	
		});
	}
}

$(document).ready(function() {			  
	rewrite_url(".linkId");
	rewrite_url("#language");
	rewrite_url("#language_vi");

	var lnk = $('#overlay_link a.link');
	var fwBtn = $('#overlay_link a.fwBtn');
	$('a[rel="#overlay_wap"]').overlay({
		onBeforeLoad: function() {
				var wap_content = jQuery("#wap_content");
				wap_content.load(this.getTrigger().attr("href"));
		}
	});
	$('a[rel="#overlay_link"]').overlay({
		onBeforeLoad: function() {
				lnk.text(this.getTrigger().attr('href'));
				lnk.attr('href', this.getTrigger().attr('href'));
				$("#overlay_link #link_content").show();
				$('#overlay_link #link_blank').hide();
				fwBtn.attr('href', this.getTrigger().attr('href'));
				if(fwBtn.attr('href')==""||fwBtn.attr('href')=="#"){
					$("#overlay_link #link_content").hide();
					$('#overlay_link #link_blank').show();
				}
		}
	});
	
});

function setSelected(elementName, value){
	$("select[name="+elementName+"] option").each(function() { 
		this.selected = (this.value == value); 
	});	
}
function setKeyword(elementName, value){
	$("input[name="+elementName+"]").val(value);
}