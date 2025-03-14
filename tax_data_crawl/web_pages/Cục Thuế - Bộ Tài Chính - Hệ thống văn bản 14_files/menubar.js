$(document).ready(function(){							
	$('#subMenu').css('display','block');	
	if(selectIndex==0){
		$('#curDate').show();
	}
	$(function() {
		$('#subMenu').find('div').hide();	 		
		$('.lotusTabs li').mouseover(function() {
			$('#subMenu').find('div').hide();
			var index = $('.lotusTabs li').index($(this));	           
			$('#subMenu').find('div:eq(' + index + ')').show();
			$('#subMenu').find('span').hide();
			removeSelectLi();
			$('.lotusTabs li').index($(this).find('a').addClass('link_hover_out'));
			$('.lotusTabs li').index($(this).find('a').find('span').addClass('span_hover_out'));
			removeSelectedLi();
		}).mouseout(function() {
			var index = $('.lotusTabs li').index($(this));							
			/*$('#subMenu').find('div:eq(' + index + ')').show();*/
			removeSelectLi();
			$('.lotusTabs li').index($(this).find('a').addClass('link_hover_out'));
			$('.lotusTabs li').index($(this).find('a').find('span').addClass('span_hover_out'));								
			removeSelectedLi();
		});
	});
	
	$("#navigation").mouseenter(function(){
		
	}).mouseleave(function(){		
		setTimeout(function(){			
			removeSelectedLi();
			removeSelectLi();
			addSelectedLi();
			$('#subMenu').find('div').hide();
			$('#subMenu').find('span').show();
			if(selectIndex==0){
				$('#curDate').show();
			}else{
				$('#curDate').hide();
			}
		}, 5000);
	});

	function removeSelectLi(){
		 $('.lotusTabs li a').each(function(index1) {
			$(this).removeClass('link_hover_out');
		  });
		 $('.lotusTabs li a').each(function(index1) {
			$(this).find('span').removeClass('span_hover_out');
		 });
	}
	
	function removeSelectedLi(){
		 $('.lotusTabs li').each(function(index1) {
			$(this).removeClass('selectedNode');
		 });			        	 
	}
	
	function addSelectedLi(){
		 $('.lotusTabs li').each(function(index1) {
			if(index1==selectIndex){
				$(this).addClass('selectedNode');
			}	
		 });			        	 
	}	
}); 