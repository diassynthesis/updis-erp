$(document).ready(function() {
	jQuery.jqtab = function(tabtit,tab_conbox,shijian) {
		$(tab_conbox).find("li").hide();
		$(tabtit).find("li:first").addClass("thistab").show(); 
		$(tab_conbox).find("li:first").show();
	
		$(tabtit).find("li").bind(shijian,function(){
		  $(this).addClass("thistab").siblings("li").removeClass("thistab"); 
			var activeindex = $(tabtit).find("li").index(this);
			$(tab_conbox).children().eq(activeindex).show().siblings().hide();
			return false;
		});
	
	};
	/*调用方法如下：*/
    $.jqtab("#tabs","#tab_conbox","click");
    $.jqtab("#tabs2","#tab_conbox2","click");
    $.jqtab("#tabs3","#tab_conbox3","click");

    $(".tabs-container .arrow").click(function(e){
        e.preventDefault();
        var content = $(".tabs-container .tabs");
        var pos = content.position().left + 500;
        if (pos>0) {
            pos=0;
        }
        content.animate({ left: pos }, 1000);
    });
    $(".tabs-container .arrow_r").click(function(ev){
        ev.preventDefault();
        var width = 0;
        $(".tabs-container ul.tabs > li").each(function(idx,itm){width += $(itm).width();});
        var tab_window_width = $(".tabs-container").width();
        var content = $(".tabs-container ul.tabs");
        var pos = content.position().left - 500;

        if (width + pos < tab_window_width) {
            pos = -width + tab_window_width;
        }
        content.animate({ left: pos }, 1000);
    });
});
