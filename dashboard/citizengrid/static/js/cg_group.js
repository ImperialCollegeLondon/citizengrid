$(function()
		  {
    $.ajaxSetup({
        cache: false,
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });
        $("#groupModal").modal({ show: false})
		$(document.body).on('click',".leavegrp >a, .editgrp >a, .delgrp >a, .attachapp > a, .groupname > a,.detach_gat >a",function(e) {
            console.log($(this).attr('type'))
            var type =$(this).attr("type")
            var id = $(this).attr("id")
            var isAdmin = $(this).attr("id")
            if(type == 'editgrp'){
                console.log("Retreiving detail data for group with id" + id)
                e.preventDefault()
                var rowData
                 $.ajax({
                url: '/cg/manage/group/detail/'+id,
                type: "GET",
                success: function(data) {
                    rowData = data
                    console.log(rowData)
                    console.log(rowData['grpname'])
                    // Populate bootstrap modal window and display it
                    $(".modal-body #grpname").val(rowData['grpname'])

                    $(".modal-body #grpdesc").val(rowData['grpdesc'])
                    $(".modal-body #grpid").val(id)

                    $("#applist").val(rowData.apps)
                    var html ="\<select name = \"apps[]\" id=\"appsgroup\" class=\"form-control\"  placeholder=\"Application\" multiple>"
                    for (i = 0; i < rowData.apps.length; i++) {
                       html = html  + "\<option value=\"" + rowData.apps[i].id + "\">" + rowData.apps[i].name + "\</option>"
                    }
                    html = html + "\</select\>"
                    console.log(html)
                    $("#applist").html(html)
                    $("#appsgroup").multiselect();
                    $("#groupEditModal").modal('show')
                }
            });
            }
            else if (type == 'leavegrp') {
                var a = confirm("Are you sure you want  to leave the group");
                if (a) {
                    e.preventDefault();
                    if (console.log) {
                        console.log($(this).attr("id") + "and type is" + $(this).attr("type"));
                    }
                    var type = $(this).attr("type")
                    var id = $(this).attr("id")

                    $.ajax({
                        url: '/cg/manage/group/leave/' + id,
                        data: {
                            id: id
                        },
                        type: "POST",
                        success: function (data) {
                            $("#groups").html(data)
                        }
                    });
                }
            }
            else if (type == 'attachapp') {
                console.log("Inside attach app")
                console.log($(this).attr("id") + "and type is" + $(this).attr("type"));
                e.preventDefault();

                    var type = $(this).attr("type")
                    var id = $(this).attr("id")
                    $(".modal-body #attach_grpid").val(id)
                    $.ajax({
                        url: '/cg/manage/group/applist',
                        data: {
                            id: id
                        },
                        type: "GET",
                        success: function (data) {
                            $("#attach_app").html(data)
                            $("#attach_app_list").multiselect()
                        }
                    });
                $("#attachAppToGrpModal").modal('show')
            }
            else if (type == 'detach_gat') {
                console.log("Inside detach tag/application form group")
                console.log($(this).attr("id") + "and type is" + $(this).attr("type"));
                e.preventDefault();

                    var type = $(this).attr("type")
                    var id = $(this).attr("id")
                    console.log("id send" +id)
                    $.ajax({
                        url: '/cg/manage/group/detachfromgroup/'+id,
                        data: {
                            id: id
                        },
                        type: "POST",
                        success: function (data) {
                            $("#apptaglist").html(data)
                        }
                    });
                $("#apptagModal").modal('show')

            }
            else if (type == 'grouptagdetail'){
                var grpid = $(this).attr("id")
                console.log("Inside groupdetail ")
                console.log("Calling application Detail tag function with group id" +grpid );
                    $.ajax({
                        url: '/cg/manage/group/applicationgrouptagdetail',
                        data: {
                            id: grpid
                        },
                        type: "GET",
                        success: function (data) {
                            $("#apptaglist").html(data)
                            $("#apptagModal").modal('show')
                        }
                    });

            }
            else if (type == 'delgrp')
            {
             var a = confirm("Are you sure you want  to delete");
             if(a){
		    e.preventDefault();
		    if(console.log){
		    console.log($(this).attr("id")+ "and type is" + $(this).attr("type"));
		    }
            var type =$(this).attr("type")
            var id = $(this).attr("id")

            $.ajax({
                url: '/cg/manage/group/delete/'+id,
                data: {
                    id:id
                },
                type: "POST",
                success: function(data) {
                    //document.getElementById("app_list").innerHTML = data
                    //console.log(data)
                	$("#groups").html(data)
                	//alert(data)
                }
            });
			}else{
				return false;
			}
            }
            else {return false}
		    return false;
		});


		  });
