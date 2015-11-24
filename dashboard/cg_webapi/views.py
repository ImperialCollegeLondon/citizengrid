import json
import logging

from django.conf import settings
from django.shortcuts import render_to_response
from django.http.response import HttpResponse, HttpResponseBadRequest,\
    HttpResponseServerError
from django.template.context import RequestContext
from cg_webapi.models import VmcpRequest
from citizengrid.cvm_webapi import VMCPSigner

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
logging.getLogger(__name__).setLevel(logging.DEBUG)

def cg_webapi_main(request):
    return HttpResponse("Hello world!", content_type='text/plain')

# This controller receives a request with a vmcp_id, this VCMP config is 
# retrieved from the database, signed and returned to the caller to start the 
# VM.
def cg_webapi_vmcp(request, vmcp_id):
    # Lookup the VMCP id in the database
    LOG.debug('Looking up VMCP request data for id: <%s>' % vmcp_id)
    try:
        vmcp_obj = None
        vmcp_obj = VmcpRequest.objects.get(vmcp_key=vmcp_id)
        MACHINE_CONFIG = json.loads(vmcp_obj.content)
        LOG.debug('Obtained machine config: <%s>' % MACHINE_CONFIG)
    except VmcpRequest.DoesNotExist:
        LOG.error('The specified VMCP request ID <%s> doesn\'t exist'
                  % vmcp_id)
        return HttpResponseBadRequest('{"status":"error", "errorText":"Invalid VMCP_ID specified."}')
    finally:
        if vmcp_obj != None:
            vmcp_obj.delete()
    # Check that the cvm_salt value is in the request    
    if 'cvm_salt' not in request.GET:
        LOG.error('Required cvm_salt parameter not found in vmcp request.')
        return HttpResponseServerError('{"status":"error", "errorText":"Required cvm_salt parameter not found in vmcp request."}')
    else:
        cvm_salt = request.GET['cvm_salt']
    
    signer = VMCPSigner(settings.VMCP_KEY_PATH)
    LOG.debug('VMCP signer: <%s>' % signer)
    
    signed_request = signer.sign(MACHINE_CONFIG, cvm_salt)
        
    return HttpResponse(json.dumps(signed_request), content_type="application/json")

# This controller will return an insecure view that loads the webapi javascript
# library and makes a call to the cg_webapi_vmcp controller above to start the 
# VM. The above view will be called with the VMCP unique ID which will extract
# the VMCP data from the database, sign it and return the signed response.
def cg_webapi_launch(request):
    if 'id' not in request.GET:
        return HttpResponseBadRequest('A required query string parameter is missing.')
    
    vmcp_id = request.GET['id']
    vmcp_url = ('cg-webapi/vmcp/%s' % vmcp_id)
    
    LOG.debug('Returning VMCP launch view for ID <%s> and url <%s>' % (vmcp_id, vmcp_url))
    
    return render_to_response('cg_webapi_insecure_popup.html', 
                              {'vmcp_url':vmcp_url}, 
                              context_instance=RequestContext(request))