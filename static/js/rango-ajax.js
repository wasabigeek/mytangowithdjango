$(document).ready(function(){
	$('#likes').click(function(){
		var catid;
		catid = $(this).attr("data-catid");
		$.get('/rango/like_category', {category_id:catid}, function(data){
			$('#like_count').html(data);
			$('#likes').hide();
		});
	});
	$('#suggestion').keyup(function(){
		var query;
		query = $(this).val();
		$.get('/rango/suggest_category/', {suggestion:query}, function(data){
			$('#cats').html(data);
		});
	});
	$('#add_page').click(function(){
		var cat_id = $(this).attr("data-catid");
		var page_title = $(this).attr("data-title");
		var page_url = $(this).attr("data-url");
		var page = {category_id:cat_id, title:page_title, url: page_url};
		$.get('/rango/auto_add_page/', page, function(data){
			$('#pages').html(data);
			$('#add_page').hide();
		});
	});
});