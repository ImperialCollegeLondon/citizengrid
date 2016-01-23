function log(msg) {
	if(console && console.log) {
		console.log(msg)
	}
}

var STATES = ['No hypervisor available','','Powered Off','Saved','Paused','Running'];

function prepareCVMWebAPI() {
	log('****** PREPARE prepareCVMWebAPI CALLED ******');
	CVM.startCVMWebAPI(function(plugin) {

		log('Got access to plugin...');
		
		plugin.addEventListener('started', function(message) {
			log('Plugin received a started event: ' + message);
		});
		
		plugin.addEventListener('completed', function(message) {
			log('Plugin received a completed event: ' + message);
		});

		plugin.addEventListener('progress', function(message, progress) {
			log('Plugin received a progress message: ' + message);
			log('Progress: ' + progress);
		});

		plugin.addEventListener('error', function(message) {
			log('Plugin received an error event: ' + message);
		});
		
		log('***** SETTING WINDOW.PLUGIN ******')
		window.plugin = plugin;
	});
}

function initCVMWebAPISession(app_id) {
		log('****** INIT initCVMWebAPISession CALLED ******');
		window.plugin.requestSession('http://cyberlab.doc.ic.ac.uk:55080/vmcp?appid=' + app_id, function(session) {
                //window.plugin.requestSession('http://test.local:8080/vmcp?appid=' + app_id, function(session) {
			log('**** Initialising CVMWebAPI Session...')
			
			window.session = session;
			
			session.addEventListener('started', function(message) {
				log('Plugin received a started event: ' + message);
			});
			
			session.addEventListener('completed', function(message) {
				log('Plugin received a completed event: ' + message);
			});

			session.addEventListener('progress', function(message, progress) {
				log('Plugin received a progress message: ' + message);
				log('Progress: ' + progress);
				var percentage = Math.floor(progress * 100);
				//$('#vmprogress .progress-bar').css('width',percentage + '%');
				//$('#vmprogress .progress-bar').html(percentage + '%');
				//$('#status-info').html(message);
			});

			session.addEventListener('error', function(message) {
				log('Plugin received an error event: ' + message);
			});
			
			session.addEventListener('stateChanged', function(code) {
				log('State changed event - new state code: ' + code);
				$('#client-status span').html(STATES[code]);
				// If machine running, change wording on launch button to terminate VM
				if(code == 5) {
					$('#client-launch').html('Terminate Local Virtual Machine');
				}
				else if(code < 5) {
					$('#client-launch').html('Launch Application Client Locally');
				}
			});
			
			session.addEventListener('resolutionChanged', function(width, height, depth) {
				log('Resolution changed. New resolution: [' + width + ', ' + height + ']. Depth: ' + depth);
			});

			session.addEventListener('apiStateChanged', function(available, url) {
				log('Is API available?: ' + available);
				log('API URL: ' + url);
			});
						
			// Set initial state
			var state = session.state;
			$('#client-status span').html(STATES[state]);
			// If machine running, change wording on launch button to terminate VM
			if(state == 5) {
				$('#client-launch').html('Terminate Local Virtual Machine');
			}
			else if(state < 5) {
				$('#client-launch').html('Launch Application Client Locally');
			}
			
			// Enable launch button and remove initialising text if no VM is
			// running, otherwise change the button to show VM running
			if($('.launchapp-btn').hasClass('disabled')) {
				log('Updating launch button on modal...');
				if(STATES[window.session.status] == 'Running') {
					$('#api-loading').html('The application virtual machine is already running.');
				}
				else {
					$('.launchapp-btn').removeClass('disabled');
					$('#api-loading').hide();
				}
			}

	});
}

function startSession(params) {
	log('Starting session...');
	window.session.start(params);
}

function stopSession() {
	log('Stop session...');
	window.session.stop();
}

function getVMSession(appID) {
	// Get the CernVM Web API session for this application
	//var appTag = $(".modal-body #tagid" ).val();
	log('********** Initialising CernVM WebAPI plugin for application ID <' + appID + '>');
	initCVMWebAPISession(appID);
};


$(document).ready(function() {
	log('Setting up CERNVM Web API...');
	prepareCVMWebAPI();
	log('Set up of CERNVM Web API plugin done...');
});
