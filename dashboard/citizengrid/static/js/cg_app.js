function launchBtnClicked(event) {
	// If the VM is already running...
	if($('#launch-app-client-btn').html() == 'Terminate Local Virtual Machine') {
		stopSession();
		return;
	}
	// If not, display the modal to set up the session. 
	var appName = $(event.target).data("appname");
	var appId = $(event.target).data("appid");
    var appIcon = $(event.target).data("appicon");
          $.ajax({
            url: 'cg/manage/applicationgrouptag/' + appId,
            type: "GET",
            success: function (data) {
                $("#selectTagslaunch").html(data)
               $("#launchAppModal").modal('show')
            }
        });

	$(".modal-body #appimg").attr("src", appIcon);
	$(".modal-body #appname").html("Application: <b>" + appName + "</b>");
	$(".modal-footer #launchappbtn").data("id", appId);
	$('.launchapp-btn').data("id", appId);

}

function modalLaunchBtnClicked(event) {

	var appId = $(event.target).data("id");
    var appTag = $(".modal-body #tagid" ).val()
	var launchType = $('#launchtype').data("launchtype");
	//$(event.target).attr("href", "/cg/launchapp/" + appId + "/" + launchType + "/" + appTag);
	if(console && console.log) {
		console.log('About to launch application with ID: ' + appId + " and tag: " + appTag);
	}
	startSession({'app_tag':appTag});
	event.preventDefault();
	$('#launchAppModal').modal("hide");
}

 $(document).off('click', ".open-StartCloudServerModal").on("click", ".open-StartCloudServerModal", function(e) {

        var cloudUrl = $(this).data("cloudurl");
        var appId = $(this).data("appid");
        var recordId = $(this).data("record-id");
        $('#selectCloud').html(cloudUrl);
        $('#startCloudServerForm input[name=appid]').val(appId);
        $('#startCloudServerForm input[name=recordid]').val(recordId);

        var csrftoken = getCookie('csrftoken');

        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        });

        $('#cloud-credentials-loading').show();

        // Make AJAX request for credentials for this URL and the current user
        // and populate the credential list.
        $.ajax({
            url: '/cg/info/cloudcredentials',
            data: cloudUrl,
            type: 'POST',
            success: function(data) {

                var cred_list_items = [];
                var i = 0;
                $.each(data.credentials, function(key, value) {
                    cred_list_items.push('<option value="' + i + '">' + value + '</option>');
                    i++;
                });
                $('#selectCredentials').html(cred_list_items.join(''));

                $('#cloud-credentials-loading').toggle();
            },
            complete: function() {
                // Schedule the next request when the current one's complete
                //setTimeout(funcname????, 5000);
            }
        });

        e.preventDefault();
    });

 var startServerModalData = null;

    $(document).off("click","#cloudServerLaunch").on("click", "#cloudServerLaunch", function() {
        // variables
        var url = $('#selectCloud').text();
        var credAlias = $('#selectCredentials').text().split(" - ")[0];
        var appTag = $(".modal-body #tagid" ).val()
        var appId = $('#startCloudServerForm input[name=appid]').val();
        var recordId = $('#startCloudServerForm input[name=recordid]').val();
        var resource_type = $("#resourceType" ).val()

        if (console && console.log) {
            console.log('Run cloud server');
            console.log('Selected cloud: ' + url);
            console.log('Credential alias: ' + credAlias);
            console.log('App ID: ' + appId);
            console.log('Record ID: ' + recordId);
            console.log('Resource Type: ' + resource_type);
            console.log('Tag name: ' + appTag);
        }
       // alert("appTag " + appTag);
        $('#start-cloud-loading').show();
        $.ajax({
            url: '/cg/launchserver/' + appId + "/",
            data: {
                endpoint: url,
                alias: credAlias,
                recordId: recordId,
                resource_type:resource_type,
                appTag: appTag
            },
            type: 'POST',
            success: function(data) {
                if (console && console.log) {
                    console.log('Start server completed successfully.');
                    console.log('Result: ' + data.result)
                    console.log('Instances started with reservation ID: ' + data.reservationId)
                    console.log('Instance IDs: ' + data.instanceIds)
                }

                $('#start-cloud-loading').hide();

                $('#cloudServerCancel').hide();
                $('#cloudServerLaunch').hide();
                $('#cloudServerOk').show();

                var newhtml = "";
                if (data.result == 'OK') {
                    newhtml = "<div style=\"color: green\">Cloud server(s) requested. Reservation ID is " + data.reservationId + "</div>";
                    //newhtml = "test";
                    console.log("Updated HTML 1: " + newhtml);
                } else {
                    newhtml = "<div style=\"color: red\">An error has occurred when trying to start the cloud server(s).</div>";
                    console.log('Updated HTML (error): ' + newhtml);
                }

                if (console && console.log) {
                    console.log('Updated HTML 2: ' + newhtml);
                }

                startServerModalData = $('#startCloudServerModal .modal-body').html();
                $('#startCloudServerModal .modal-body').html(newhtml);
            },
            complete: function() {
                // Schedule the next request when the current one's complete
                //setTimeout(funcname????, 5000);
            }
        });


    });

    var shuttingDown = new Array();

    function updateRunningServers(appid) {
        if (console && console.log) {
            console.log("Update running servers has been called...");
        }

        var csrftoken = getCookie('csrftoken');

        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        });

        $.ajax({
            url: '/cg/manage/instances/status/' + appid + '/',
            data: {
                'appid': appid
            },
            type: 'POST',
            success: function(data) {
                if (console && console.log) {
                    console.log('Got back data for ' + Object.keys(data).length + ' instances');
                    console.log('Application ID: ' + appid);
                }

                if (Object.keys(data).length > 0 ) {
                    if (console && console.log) {
                        console.log('Still have running instances, updating in 10 seconds...');
                    }

                    var i;
                    var allRunning = true;
                    var keys = Object.keys(data);
                    for (i = 0; i < keys.length; i++) {
                        console.log('ID: ' + keys[i]);
                        console.log('Length: ' + $('#' + keys[i]).length);

                        if ($('#' + keys[i]).length) {
                            console.log("Instance state on gui  " + $('#' + keys[i] + ' .state').text())
                            console.log(document.getElementsByClassName("state")[0].innerHTML)
                            // element exists - check if an update is required
                            // if status terminated, delete the instance from the table
                            if (!$('#' + keys[i] + ' .state').text() == 'terminated') {
                                $('#' + keys[i]).remove();
                                delete shuttingDown[keys[i]];
                            } else{
                                if (!$('#' + keys[i] + ' .state').text() != data[keys[i]].state) {
                                    console.log("Instance state on backend  " + data[keys[i]].state)
                                    $('#' + keys[i] + ' .state').text(data[keys[i]].state); }
                                if ((data[keys[i]].state != 'running') || (Object.keys(shuttingDown).length > 0)) {
                                        allRunning = false;
                                    }

                                // element exists - check if an update is required
                                if (!$('#' + keys[i] + ' .ip').text() != data[keys[i]].ip) {
                                    $('#' + keys[i] + ' .ip').text(data[keys[i]].ip);
                                    if(data[keys[i]].ip =='undefined' ){
                                        allRunning = false;
                                    }

                                }
                                if (Object.keys(shuttingDown).length > 0) {
                                    for (i = 0; i < Object.keys(shuttingDown).length; i++) {
                                        if ($('#' + keys[i]).length) {
                                            $('#' + keys[i]).remove();
                                            delete shuttingDown[keys[i]];
                                        } //end of if
                                    }//end of for
                                }
                            }
                        } else {
                            // Add new row to table
                            var newRow = '<tr id="' + keys[i] + '"><td class="instance_id">' + keys[i] + '</td><td class="state">' + keys[i].state + '</td><td class="ip">' + keys[i].ip + '</td><td><a href="#"><i class="glyphicon glyphicon-refresh"></i></a></td><td><a id ="shutdown-' + keys[i] + '" class="shutdown-server glyphicon glyphicon-remove" data-original-title="Shutdown server" data-instance=' + keys[i] + ' data-appid=' + appid + '></a></td></tr>';
                            $('#server_instance_info_' + appid + ' > tbody:last').append(newRow);
                            $('.shutdown-server').tooltip();
                            allRunning = false;
                        }
                    }
                    console.log("shutting down " + Object.keys(shuttingDown).length)
                    console.log("Running status " + allRunning)
                    if ((!allRunning) || (Object.keys(shuttingDown).length > 0)) {
                        setTimeout(function() {
                            updateRunningServers(appid);
                        }, 10000);
                    }
                } else {
                    if (console && console.log) {
                        console.log('No more running instances for application <' + appid + '>, cancelling updates');
                    } //end of if
                } //end of if-else
                if (console && console.log) {
                    console.log('Completed updatedRunningServers success function');
                }//end of if
            }, //end of success
            complete: function() {
                // Schedule the next request when the current one's complete
                //setTimeout(funcname????, 5000);
            } //complete function end
        }); //ajax function end
    }//end of updated serverfunction


    $(document).off("click",".shutdown-server").on("click", ".shutdown-server", function(e) {
        var instanceId = $(this).data("instance");
        var appid = $(this).data("appid");

        if (console && console.log) {
            console.log('Requested to shutdown instance: ' + instanceId);
        }

        shuttingDown[instanceId] = 'shutting-down';
        console.log("called shutting down " + Object.keys(shuttingDown).length )

        setTimeout(function() {
            shutdownRunningServer(appid, instanceId);
        }, 0);
    });


    function shutdownRunningServer(appid, instanceid) {
        if (console && console.log) {
            console.log("Request to shutdown running server with ID <" + instanceid + ">...");
        }

        var csrftoken = getCookie('csrftoken');

        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        });

        $.ajax({
            url: '/cg/manage/instances/shutdown/' + appid + '/' + instanceid,
            data: {
                'instanceid': instanceid
            },
            type: 'POST',
            success: function(data) {
                if (console && console.log) {
                    console.log('Request sent to shutdown server. Result: ' + data.result);
                }
            },
            complete: function() {
                // Schedule the next request when the current one's complete
                setTimeout(updateRunningServers(appid), 10000);
            }
        });
    }

    $('#cloudServerOk').off("click").on("click", function() {
        if ($('#cloudServerOk').is(":visible")) {
            // If OK button is visible, we accept the click event
            // Close the modal, replace the HTML content and re-activate
            // the buttons.

            $('#startCloudServerModal').modal("hide");

            //TODO: Wait until modal has been hidden before updating content
            if (startServerModalData != null) {
                $('#startCloudServerModal .modal-body').html(startServerModalData);
            }
            $('#cloudServerOk').hide();
            $('#cloudServerCancel').show();
            $('#cloudServerLaunch').show();

            var appid = $('#startCloudServerForm input[name=appid]').val();
            alert("appid is "+ appid);

            setTimeout(function() {
                updateRunningServers(appid);
            }, 0);
        }
    });
$(document.body).off("click"," a.run-image").on('click'," a.run-image",function(e) {
   // get all the tags
    var appid = $(this).attr("data-appid")
    console.log(appid)
          $.ajax({
            url: 'cg/manage/applicationgrouptag/' + appid,
            type: "GET",
            success: function (data) {
                $("#selectTagsCloudServer").html(data)
                $("#startCloudServerModal").modal('show')
            }
        });
 });