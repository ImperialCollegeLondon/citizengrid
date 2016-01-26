from citizengrid.settings.production import *

import tempfile
import os
import utils
import simplejson
import subprocess
import base64
import logging

import boto.ec2

from urlparse import urlparse

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from citizengrid.models import ApplicationBasicInfo
from citizengrid.models import ApplicationFile
from citizengrid.models import UserCloudCredentials
from citizengrid.models import ApplicationOpenstackImages
from citizengrid.models import ApplicationEC2Images
from citizengrid.models import CloudInstancesOpenstack
from citizengrid.models import CloudInstancesAWS
from citizengrid.models import UsersApplications
from django.http.response import HttpResponseNotFound

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
logging.getLogger(__name__).setLevel(logging.DEBUG)

jnlp_base = """
<?xml version="1.0" encoding="utf-8"?>
<!-- JNLP File for VirtualBox local client deployment -->
<jnlp
  spec="6.0+"
  codebase="{base_url}"
  href="{jnlp_location}">
  <information>
    <title>VirtualBox local app deployment</title>
    <vendor>Citizen Cyberlab Project</vendor>
    <homepage href="{base_url}"/>
    <description>VirtualBox local deployment for CitizenGrid application {app_name}</description>
    <description kind="short">Deploy a VirtualBox image for a CitizenGrid application on a client machine</description>
    <icon href="img/logo_trans.png"/>
    <icon kind="splash" href="img/logo_trans.png"/>
    <shortcut online="false" install="false">
      <desktop/>
      <menu submenu="Cyberlab"/>
    </shortcut>
  </information>
  <information os="linux">
    <title>VirtualBox local app deployment for Linux </title>
    <homepage href="{base_url}"/>
  </information>
  <security>
      <all-permissions/>
  </security>
  <resources>
    <j2se version="1.6+" java-vm-args="-esa -Xnoclassgc -Xmx3048m -Xms1056m"/>
    <jar href="static/vbox-launcher/vboxlauncher.jar" download="eager" main="true"/>
    <jar href="static/vbox-launcher/vboxjws.jar" />
    <jar href="static/vbox-launcher/commons-logging-1.1.3.jar" />
    <jar href="static/vbox-launcher/httpcore-4.3.jar" />
    <jar href="static/vbox-launcher/httpclient-4.3.1.jar" />
    <jar href="static/vbox-launcher/zip4j-1.3.2.jar" />
  </resources>
  <application-desc main-class="eu.citizencyberlab.icstm.cg.ClientVboxLauncher">
{launcher_args}
  </application>
</jnlp>
"""

@require_GET
@login_required
def launchapp(request, appid, launchtype, apptag):
    LOG.debug("Request to launch app with ID <%s> and launch type <%s> "
              "with tag name <%s>" % (appid, launchtype, apptag))
    LOG.debug("requesting user is <%s>" % request.user.id)

    appObject = ApplicationBasicInfo.objects.get(id=appid)
    app_files = ApplicationFile.objects.filter( file_type='S', application_id=appid,image_type='C')
    LOG.debug("Found %s files for this application." % len(app_files))

    LOG.debug("Using file locations: ")
    for app in app_files:
        LOG.debug("File: %s for app <%s>." % (app.file.name, app.application.name))

    if len(app_files) == 0:
        return HttpResponse("<h1> No image available to launch</h1>")
    else:
        vm_name = str(app.application.name)
        app_owner = str(ApplicationBasicInfo.objects.filter(id=appid)[0].owner.username)
        #request.user.get_username()
        launcher_args = '    <argument>' + vm_name + '</argument>'
        #launcher_args = ''
        for app in app_files:
            launcher_args += '\n    <argument>' + os.path.join(request.build_absolute_uri("/"), 'media', app_owner, vm_name, os.path.basename(app.file.name)) + '</argument>'

        fs = FileSystemStorage()

        filedir = os.path.join(fs.location, 'jnlp', request.user.get_username())

        if not os.path.isdir(filedir):
            os.makedirs(filedir, 0700)
            LOG.debug("Created user directory for JNLP launch files: <%s>" % filedir)

        jnlp_file_name = tempfile.mktemp(suffix='.jnlp', dir=filedir)
        jnlp_file_url_path = os.path.join('/media', 'jnlp', request.user.get_username(), os.path.basename(jnlp_file_name))
        executable_file_name = os.path.join(fs.location,'isocreator', os.path.basename(ISO_GENERATOR_EXE))
        LOG.debug("Executable file: %s" % executable_file_name)
        if apptag != "NONE":
            LOG.debug("Create an ISO with Group <%s>" % apptag)
            (tagname,tagid) = str(apptag).split("-")

            if tagname.lower() == 'vas':
                LOG.debug("create  VAS contextualized ISO")
                iso_file_name = tempfile.mktemp(suffix='.iso', dir=filedir)
                iso_file_url_path = os.path.join('/media', 'jnlp', request.user.get_username(), os.path.basename(iso_file_name))
                arg = [executable_file_name] + [tagid] + [iso_file_name]
                LOG.debug('About to run process <%s>' % arg)
                subprocess.call(arg)
                launcher_args += '\n    <argument>' + os.path.join(request.build_absolute_uri("/"), 'media', 'jnlp', request.user.get_username(), os.path.basename(iso_file_name)) + '</argument>'
            elif tagname.lower() == 'boinc':
                LOG.debug("create BOINC contextualized ISO")
            else:
                pass
        else:
            pass

        # We now generate the jnlp file which will be returned to the client in order
        # to begin the webstart process that will download and run the image.
        jnlp_properties = {'base_url': request.build_absolute_uri("/"),
                           'jnlp_location': jnlp_file_url_path,
                           'app_name': app.application.name,
                           'launcher_args': launcher_args,
                           }

        formatted_jnlp = jnlp_base.format(**jnlp_properties)

        LOG.debug("Formatted JNLP: %s" % formatted_jnlp)

        # Write JNLP file to the filesystem
        with open(jnlp_file_name, 'w') as f:
            f.write(formatted_jnlp)


        appObject.client_downloads = appObject.client_downloads + 1
        appObject.save()
        LOG.debug("Updated client_download in ApplicationBasicInfo")   
         
        try:
            rec = UsersApplications.objects.get(user=request.user,application=appObject)   
            rec.run_count = rec.run_count + 1             
            LOG.debug("Updated run count in UsersApplications")   
        except UsersApplications.DoesNotExist:
            rec = UsersApplications(user=request.user,application=appObject)          
            LOG.debug("Inserted new record to UsersApplications")   
        rec.save()
    
        return HttpResponse(formatted_jnlp, content_type='application/x-java-jnlp-file')


def start_server(appid, cred, endpoint, cloud, imageRecord, appTag, instance_type, image_info, request):

    contextData = ""
    if appTag != "NONE":
            LOG.debug("Start server with Group ID <%s>" % appTag)
            (tagname,tagid) = str(appTag).split("-")

            if tagname.lower() == 'vas':
                LOG.debug("Create  VAS contextualization")
                contextData ="[amiconfig]\nplugins=cernvm\n\n[cernvm]\ncontextualization_key=cfcbde8ad2d4431d8ecc6dd801015252\nliveq_queue_id="
                contextData += tagid
                LOG.debug("Context Data \n%s" % contextData)
            elif tagname.lower() == 'boinc':
                LOG.debug("Create Boinc contextualization")
            else:
                pass

    if cred:
        LOG.debug('Retrieved credentials successfully.')
    else:
        # TODO: Add full error handling
        LOG.debug('ERROR: Unable to retrieve credentials')
        return HttpResponseNotFound
    if image_info:
        LOG.debug('Retrieved image info for image <%s> successfully.' % image_info.image_id)
    else:
        # TODO: Add full error handling
        LOG.debug('ERROR: Unable to retrieve image data')
        return HttpResponseNotFound()
    (access_key, secret_key) = utils.decrypt_cred_pair(cred.access_key, cred.secret_key)
    LOG.debug('Access key: %s ' % access_key)
    LOG.debug('Secret key: %s' % secret_key)
    LOG.debug('About to connect to region <%s> with access_key <%s> and '
              'secret_key <%s>' % (endpoint, access_key, secret_key))
    parsed_url = urlparse(endpoint)
    ip = parsed_url.netloc.split(':')[0]
    local_region = boto.ec2.regioninfo.RegionInfo(name="openstack", endpoint=ip)
    conn = boto.connect_ec2(aws_access_key_id=access_key, aws_secret_access_key=secret_key, is_secure=False,
                            region=local_region, port=parsed_url.port, path=parsed_url.path)
    images = conn.get_all_images()
    # Check the list of images to see that we have access to the specified image ID.
    image_data = None
    for image in images:
        if image.id == image_info.image_id:
            image_data = image
    if not image_data:
        # TODO: Add full error handling
        LOG.debug('ERROR: Unable to find requested image ID on the selected cloud platform')
        return HttpResponseNotFound()
    else:
        LOG.debug('Image is available, about to start image with id <%s>...' % image_data.id)
    response_data = {}

    reservation = conn.run_instances(image_data.id, 1, 1, key_name=None, security_groups=None, user_data=contextData,
                                     addressing_type=None, instance_type=instance_type, placement=None)
    LOG.debug('Instance pending with reservation ID: %s' % reservation.id)
    instance_ids = []
    for i in reservation.instances:
        instance_ids.append(i.id)
    app = ApplicationBasicInfo.objects.get(id=appid)
    #appimg = ApplicationOpenstackImages.objects.get(id=imageRecord)
    creds = UserCloudCredentials.objects.get(id=cred.id)
    for id in instance_ids:
        if cloud == 'os':
            instanceRecord = CloudInstancesOpenstack(owner=request.user,
                                                 application=app,
                                                 application_image=image_info,
                                                 credentials=creds,
                                                 instance_id=id,
                                                 status='PENDING')
        elif cloud == 'ec2':
            instanceRecord = CloudInstancesAWS(owner=request.user,
                                                 application=app,
                                                 application_image=image_info,
                                                 credentials=creds,
                                                 instance_id=id,
                                                 status='PENDING')
        else:
            pass
        instanceRecord.save()
    response_data['result'] = 'OK'
    response_data['reservationId'] = reservation.id
    response_data['instanceIds'] = instance_ids
    response_data['instanceRecord'] = instanceRecord.id
    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")


@require_POST
@login_required
def launchserver(request, appid, launchtype):
    LOG.debug("Request to launch cloud server for application: %s" % appid)
    LOG.debug("Requesting user is %s" % request.user.id)

    appTag = "NONE"
    endpoint = request.POST['endpoint']
    instance_type = request.POST['resource_type']
    #instance_type = 'Large'
    alias = request.POST['alias']
    recordId = request.POST['recordId']

    appTag = request.POST.get('appTag', '')
    cloud = recordId.split(':')[0]
    imageRecord = recordId.split(':')[1]

    if appTag =="":
        appTag = "NONE"

    LOG.debug('Instance type <%s>' % instance_type)
    LOG.debug('appTag received: <%s>' % appTag)
    LOG.debug('Launch server on cloud <%s> with image record <%s> using '
              'credential alias <%s> and cloud url <%s>' 
              % (cloud, imageRecord, alias, endpoint))
    
    # Lookup credentials for this user and the specified endpoint
    if cloud == 'os':
        cred = UserCloudCredentials.objects.get(user=request.user, endpoint=endpoint, key_alias=alias)
        image_info = ApplicationOpenstackImages.objects.get(id=imageRecord)
    elif cloud == 'ec2':
        # TODO: Add EC2 support
        cred = UserCloudCredentials.objects.get(user=request.user, endpoint=endpoint, key_alias=alias)
        image_info = ApplicationEC2Images.objects.get(id=imageRecord)
    else:
        #TODO: Add error checking
        # Error, an invalid cloud was specified
        pass

    app = ApplicationBasicInfo.objects.get(id=appid)
    try:
        rec = UsersApplications.objects.get(user=request.user,application=app)   
        rec.run_count = rec.run_count + 1             
        LOG.debug("Updated run count in UsersApplications")   
    except UsersApplications.DoesNotExist:
        rec = UsersApplications(user=request.user,application=app)          
        LOG.debug("Inserted new record to UsersApplications")
    rec.save()

        
    return start_server(appid, cred, endpoint, cloud, imageRecord, appTag, instance_type, image_info, request)

@require_POST
@login_required
def manage_instances(request, task, appid, instancerecord):
    response_data = {}

    LOG.debug('Request received by manage instances.')

    if task == 'status':
        LOG.debug('Request to undertake management task <%s> for application '
                  'id <%s>' % (task, appid))

        application = ApplicationBasicInfo.objects.get(id=appid)
        instances_openstack = CloudInstancesOpenstack.objects.filter(owner=request.user, application=application)
        instances_ec2 = CloudInstancesAWS.objects.filter(owner=request.user, application=application)

        if len(instances_openstack) + len(instances_ec2) == 0:
            return HttpResponse(simplejson.dumps(response_data), content_type="application/json")

        # Prepare Openstack connection
        if len(instances_openstack) != 0:
            for instance in instances_openstack:
                LOG.debug('Getting updated data for EC2 instance: %s' % instance.instance_id)
                credentials = instance.credentials
                (access_key, secret_key) = utils.decrypt_cred_pair(credentials.access_key, credentials.secret_key)
                parsed_url = urlparse(credentials.endpoint)
                ip = parsed_url.netloc.split(':')[0]
                local_region = boto.ec2.regioninfo.RegionInfo(name="openstack", endpoint=ip)
                conn = boto.connect_ec2(aws_access_key_id=access_key,aws_secret_access_key=secret_key,is_secure=False,region=local_region,port=parsed_url.port,path=parsed_url.path)
                reservations = conn.get_all_instances(instance_ids=[instance.instance_id])
                if len(reservations) == 0:
                    CloudInstancesOpenstack.objects.filter(instance_id=instance.instance_id).delete()
                else:
                    for reservation in reservations:
                        LOG.debug('Reservation ID: %s' % reservation.id)
                        for instanceOS in reservation.instances:
                            LOG.debug('Instance ID: %s' % instanceOS.id)
                            instance_info = {}
                            instance_info['id'] = instanceOS.id
                            instance_info['state'] = instanceOS.state
                            if instance_info['state'] == 'running':
                                instance_info['ip'] = instanceOS.public_dns_name
                            # Update instance state in DB
                            if instance_info['state'] != instance.status:
                                instance.status = instance_info['state']
                                instance.save()
                                instance_info['ip'] = instanceOS.public_dns_name
                            response_data[instanceOS.id] = instance_info


        if len(instances_ec2) != 0:
            for instance in instances_ec2:
                LOG.debug('Getting updated data for EC2 instance: %s' % instance.instance_id)
                credentials = instance.credentials
                (access_key, secret_key) = utils.decrypt_cred_pair(credentials.access_key, credentials.secret_key)
                parsed_url = urlparse(credentials.endpoint)
                ip = parsed_url.netloc.split(':')[0]
                local_region = boto.ec2.regioninfo.RegionInfo(name="openstack", endpoint=ip)
                conn = boto.connect_ec2(aws_access_key_id=access_key,aws_secret_access_key=secret_key,is_secure=False,region=local_region,port=parsed_url.port,path=parsed_url.path)
                reservations = conn.get_all_instances(instance_ids=[instance.instance_id])
                if len(reservations) == 0:
                    CloudInstancesAWS.objects.filter(instance_id=instance.instance_id).delete()
                else:
                    for reservation in reservations:
                        LOG.debug('Reservation ID: %s' % reservation.id)
                        for instanceEC2 in reservation.instances:
                            LOG.debug('Instance ID: %s' % instanceEC2.id)
                            instance_info = {}
                            instance_info['id'] = instanceEC2.id
                            instance_info['state'] = instanceEC2.state
                            instance_info['ip'] = instanceEC2.public_dns_name
                            # Update instance state in DB
                            if instance_info['state'] != instance.status:
                                instance.status = instance_info['state']
                                instance.save()
                                instance_info['ip'] = instanceEC2.public_dns_name
                            response_data[instanceEC2.id] = instance_info

    elif task == 'shutdown':
        LOG.debug('Request to shutdown instance: <%s> for application: <%s>' 
                  % (instancerecord, appid))

        application = ApplicationBasicInfo.objects.get(id=appid)
        instance = None
        try:
            instance = CloudInstancesOpenstack.objects.get(owner=request.user, application=application, instance_id=instancerecord)
        except CloudInstancesOpenstack.DoesNotExist:
            LOG.debug('The OpenStack cloud instance could not be found for ID: '
                      '<%s> for application: <%s> for the current user.' 
                      % (instancerecord, appid))

        if instance == None:
            try:
                instance = CloudInstancesAWS.objects.get(owner=request.user, application=application, instance_id=instancerecord)
            except CloudInstancesOpenstack.DoesNotExist:
                LOG.debug('The AWS cloud instance could not be found for ID: '
                          '<%s>.  For application: <%s> for the current user.' 
                          % (instancerecord, appid))

        if instance != None:
            #print '<' + str(instance.length) + '> matching instances found. Shutting down the first matching instance.'
            LOG.debug('Matching instance found. Shutting this instance down.')

            inst_for_shutdown = instance
            # Prepare Openstack/EC2 connection
            credentials = inst_for_shutdown.credentials
            (access_key, secret_key) = utils.decrypt_cred_pair(credentials.access_key, credentials.secret_key)
            parsed_url = urlparse(credentials.endpoint)
            ip = parsed_url.netloc.split(':')[0]
            local_region = boto.ec2.regioninfo.RegionInfo(name="openstack", endpoint=ip)
            conn = boto.connect_ec2(aws_access_key_id=access_key,aws_secret_access_key=secret_key,is_secure=False,region=local_region,port=parsed_url.port,path=parsed_url.path)

            terminated_instances = conn.terminate_instances(str(instancerecord))
            LOG.debug('Shutting down <%s> instances.' % len(terminated_instances))

            terminate_instance_result = terminated_instances[0].id

            response_data['result'] = 'OK'
            response_data['terminated'] = terminate_instance_result

        else:
            response_data['result'] = 'ERROR'
            response_data['reason'] = 'Instance not found for application <' + appid + '> and instance ID <' + instancerecord + '>'



    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")
