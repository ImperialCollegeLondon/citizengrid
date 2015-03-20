$(function()
		  {
    $.ajaxSetup({
        cache: false,
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });
		$(document.body).on('click',".local >a ,.cloud >a,.appli_delete >a, .delcreds >a",function(e) {
			var a = confirm("Click to confirm deletion");
            console.log("Hi")
			if(a){
		    e.preventDefault();
		    if(console.log){
		    console.log($(this).attr("id")+ "and type is" + $(this).attr("type"));  
		    }
            var type =$(this).attr("type")
            var id = $(this).attr("id")
            var fd = new FormData();
            fd.append('type',type)
            var global_id = null
            if(type=='file'){
            	global_id ='#localimage'
            }else if(type=='os' || type=='ec2'){
            	global_id ='#cloudimage'	
            }else if (type =='oscred') {
            	global_id="#oscred-info"
            }
            else if (type =='app') {
            	global_id="#app_list"
            }
            else{
            	global_id="#app_list"
            }
            
            $.ajax({
                url: '/cg/delete/'+id,
                data: fd,
                type: "POST",
                success: function(data) {
                    //document.getElementById("app_list").innerHTML = data
                	$(global_id).html(data)
                	//alert(data)
                },
                processData: false,
                contentType: false
            });	
			}else{
				return false;  
			}
		    
		    return false;  
		});
		  });
