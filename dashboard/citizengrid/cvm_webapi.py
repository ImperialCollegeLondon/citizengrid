import os
import json
import logging
import hashlib
import base64
import urllib
import uuid
from django.http.response import HttpResponseNotAllowed, HttpResponse,\
    HttpResponseServerError, HttpResponseRedirect, HttpResponseBadRequest
from citizengrid.models import ApplicationBasicInfo, ApplicationFile
from cg_webapi.models import VmcpRequest
from django.conf import settings
import urlparse

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')

class _crypto_M2Crypto:
    """
    [Cryptographic Routines Implementation]
    Using M2Crypto Libraries (Tricky to build, but fast)

    Installable using: `pip install m2crypto`
    """
    def __init__( self, pkey ):
        # Try to load M2Crypto
        import M2Crypto
        self.rsa = M2Crypto.RSA.load_key( pkey )

    def sign( self, payload ):
        # Calculate the digest of the payload
        digest = hashlib.new('sha512', payload).digest()
        # Sign and return
        return base64.b64encode( self.rsa.sign(digest, "sha512") )

class _crypto_PyCrypto:
    """
    [Cryptographic Routines Implementation]
    Using PyCrypto Libraries (Relatevely easy to build and fast)

    Installable using: `pip install pycrypto`
    """
    def __init__( self, pkey ):
        # Try to load PyCrypto libraries
        import Crypto.Hash.SHA512 as SHA512
        import Crypto.PublicKey.RSA as RSA
        import Crypto.Signature.PKCS1_v1_5 as PKCS1_v1_5
        self.SHA512 = SHA512
        # Open and read key file
        with open(pkey, 'r') as f:
            # Create an RSA key
            rsa = RSA.importKey(f.read())
            # Create a PKCS1 signer
            signer = PKCS1_v1_5.new(rsa)
            # Return the signer instance
            self.signer = signer

    def sign( self, payload ):
            # Calculate the digest of the payload
            digest = self.SHA512.new(payload)
            # Sign and return
            return base64.b64encode( self.signer.sign(digest) )

class _crypto_rsa:
    """
    [Cryptographic Routines Implementation]
    Using RSA Python Library (Pure python code, but slower)

    Installable using: `pip install rsa`
    """
    def __init__( self, pkey ):
        # Try to load rsa library
        import rsa
        print "Using rsa"
        self.rsa = rsa
        # Open and read key file
        with open(pkey, 'r') as f:
            # Create an RSA key
            self.key = rsa.PrivateKey.load_pkcs1(f.read())

    def sign( self, payload ):
        # Sign and return
        return base64.b64encode( self.rsa.sign(payload, self.key, "SHA-512") )

class VMCPSigner:
    """
    VMCP Signer Class

    This class provides the cryptographic helper routine 'sign' which is used
    to sign a set of key/value parameters with a predefined private key.

    This class automaticaly tries to find various RSA implementations already
    installed in your system, including M2Crypto, PyCrypto and RSA libraries.

    Usage:

    ```python
    from vmcp import VMCPSigner
    
    # Create an instance to the VMCP signer
    signer = VMCPSigner('path/to/private_key.pem')
    
    # Sign a set of key/value parameters using a
    # salt provided by CernVM WebAPI
    parameters = signer.sign({ "disk": "1024" }, request.get('cvm_salt'))

    ```
    """

    def __init__(self, private_key="test-local.pem"):
        """
        Create a VMCP signer that uses the specified private key
        """
        # Try various cryptographic providers until we find something
        self.crypto = None
        for p in (_crypto_M2Crypto, _crypto_PyCrypto, _crypto_rsa):
            try:
                self.crypto = p(private_key)
                break
            except ImportError:
                continue
            except IOError as e:
                raise IOError("Could not load private key from '%s' (%s)" % (private_key, str(e)))

        # Check if it was not possible to instantiate a provider
        if not self.crypto:
            raise IOError("Could not find an RSA library in your installation!")

    def sign(self, parameters, salt):
        """
        Calculate the signature for the given dictionary of parameters
        and unique salt.

        This function use the reference for calculating the VMCP signature
        from https://github.com/wavesoft/cernvm-webapi/wiki/Calculating-VMCP-Signature .

        It returns a new dictionary, having the 'signature' key populated with
        the appropriate signature.
        """

        # Validate parameters
        if type(parameters) != dict:
            raise IOError("Expecting dictionary as parameters!")

        # Create the buffer to be signed, 
        # following the specifications
        # ------------------------------------
        # 1) Sort keys
        strBuffer = ""
        for k in sorted(parameters.iterkeys()):

            # 2) Handle the BOOL special case
            v = parameters[k]
            if type(v) == bool:
                if v:
                    v=1
                else:
                    v=0
                parameters[k] = v

            # 3) URL-Encode values
            # 4) Represent in key=value\n format
            strBuffer += "%s=%s\n" % ( str(k).lower(), urllib.quote(str(v),'~') )

        # 5) Append Salt
        strBuffer += salt
        # ------------------------------------

        # Create a copy so we don't touch the original dict
        parameters = parameters.copy()

        # Store the resulting signature to the parameter
        parameters['signature'] = self.crypto.sign( strBuffer )
        return parameters

def sha256_checksum(file_path):
    with open(os.path.join(settings.PROJECT_ROOT, file_path)) as f:
        hash_alg = hashlib.sha256()
        hash_alg.update(f.read())
        base64_hash = base64.b64encode(hash_alg.digest())
    return base64_hash

def vmcp(request):
    MACHINE_CONFIG = _generate_vmcp_config(request)
    
    if 'cvm_salt' not in request.GET:
        LOG.error('Required cvm_salt parameter not found in vmcp request.')
        return HttpResponseServerError('{"status":"error", "errorText":"Required cvm_salt parameter not found in vmcp request."}')
    else:
        cvm_salt = request.GET['cvm_salt']
    
    signer = VMCPSigner(settings.VMCP_KEY_PATH)
    LOG.debug('VMCP signer: <%s>' % signer)
    
    signed_request = signer.sign(MACHINE_CONFIG, cvm_salt)
        
    return HttpResponse(json.dumps(signed_request), content_type="application/json")
    
# This endpoint is for use when running behind HTTPS and redirecting to an HTTP
# URL for starting a VM. Get the signed VCMP request (via HTTPS request) and 
# then save this against a unique key. Then send an HTTP redirect to access this    
def webapi_start(request):
    # We need an appid and apptag for the request to succeed.
    if 'appid' not in request.GET:
        return HttpResponseBadRequest('Required parameter appid not provided.')
    if 'apptag' not in request.GET:
        return HttpResponseBadRequest('Required parameter apptag not provided.')
    
    MACHINE_CONFIG = _generate_vmcp_config(request)
    
    # Now save the signed request
    unique_id = uuid.uuid4()
    vr = VmcpRequest(vmcp_key=unique_id, content=json.dumps(MACHINE_CONFIG))
    vr.save()
    
    # Now send a redirect to an HTTP page passing the unique_id
    # Get the current URI
    uri = request.build_absolute_uri()
    parsed_url = urlparse.urlparse(uri)
    # See if we have a host/port
    host_port = parsed_url.netloc.split(':')
    redirect_url = ('http://%s:%s/cg-webapi/launch/?id=%s' % 
                    (host_port[0], settings.HTTP_PORT, unique_id))
    LOG.debug('Redirecting secure VMCP request to <%s>' % redirect_url)    
    return HttpResponseRedirect(redirect_url)    

def _generate_vmcp_config(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    
    app_id = request.GET['appid']
    app_tag = request.GET['apptag']
    
    # Get the group id from the app tag
    group_id = app_tag[app_tag.find('-')+1:]
    
    LOG.debug('Getting VMCP config for application with ID [%s]' % app_id)
    
    file_formats = { 'NONE': 'Local file (Unknown type)',
                   'HD' : 'Local image (RAW_ID)',
                   'IMG' : 'Local image (RAW_Image)',
                   'VDI' : 'Local image (Virtualbox)',
                   'VMDK': 'Local image (VMware VMDK)',
                   'ISO' : 'CD/DVD ROM Image',
                   'OVF' : 'OVF Appliance',
                   'OVA' : 'Local Appliance Archive (OVA)'}
    
    # Get the application from the database and build the required
    # machine configuration for the application
    LOG.debug('About to request app object for app_id <%s>' % app_id)
    app = ApplicationBasicInfo.objects.get(id=app_id)
    files = ApplicationFile.objects.filter(file_type='S', image_type= 'C', application=int(app_id))
    file_info_dict = {}
    for appfile in files:
        if appfile.image_type == 'C':
            has_client = True

        if appfile.application.id not in file_info_dict:
            file_info_dict[appfile.application.id] = []
        file_info = {}
        file_info['appfile'] = appfile
        file_info['name'] = appfile.filename()
        file_info['path'] = os.path.join('media', app.owner.username, app.name, appfile.filename())
        #file_info['path'] = os.path.join('media', request.user.username, appfile.filename())
        file_info['formatstring'] = file_formats[appfile.file_format]
        file_info_dict[appfile.application.id].append(file_info)
    
    disk_checksum = sha256_checksum(file_info['path'])
    
    MACHINE_CONFIG = {
        'name' : app.name,
        'secret' : 'pr0t3ct_this',
        #'userData' : "[amiconfig]\nplugins=cernvm\n[cernvm]\ncontextualization_key=0c41ec2627604bc09457de39e190c24c\n",
        'ram' : 1024,
        'cpus' : 1,
        'disk' : 2048,
        'flags': 0x31,
        'diskURL':'http://test.local:8000/' + file_info['path'],
        'diskChecksum': disk_checksum
    }
    
    LOG.debug('Using diskURL <%s>' % MACHINE_CONFIG['diskURL'])
    
    if app.name.lower() == 'vas':
        MACHINE_CONFIG['userData'] = ("[amiconfig]\nplugins=cernvm\n\n"
            "[cernvm]\ncontextualization_key=cfcbde8ad2d4431d8ecc6dd801015252\n"
            "liveq_queue_id=%s\n" % group_id)
    
        LOG.debug('VMCP MACHINE_CONFIG requested and configured. User data: %s'
                  % MACHINE_CONFIG['userData'])
        
    return MACHINE_CONFIG
    