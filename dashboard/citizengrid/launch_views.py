import citizengrid.settings

import tempfile
import os
import utils
import simplejson

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
from citizengrid.models import UsersApplications
from django.http.response import HttpResponseNotFound


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
def launchapp(request, appid, launchtype):
    print "Request to launch app with ID <" + appid + "> and launch type <" + launchtype + ">"
    print "requesting user is " + str(request.user.id)
    appObject = ApplicationBasicInfo.objects.get(id=appid)

    #if appid == <the id of vams>:
    #   Generate context iso
    #    from subprocess import call
    #    call([], executable=settings.ISO_GENERATOR_EXE)
    
    try:
        rec = UsersApplications.objects.get(user=request.user,application=appObject)   
        rec.run_count = rec.run_count + 1   
        print "Updated record to UsersApplications"   
    except UsersApplications.DoesNotExist:
        rec = UsersApplications(user=request.user,application=appObject)          
        print "Inserted new record to UsersApplications"   
    rec.save()
    # removed owner_id=request.user as any user can launch the application
    #app_files = ApplicationFile.objects.filter(owner_id=request.user, file_type='S', application_id=appid)
    app_files = ApplicationFile.objects.filter( file_type='S', application_id=appid,image_type='C')
    print "Found " + str(len(app_files)) + " files for this application."

    print "Using file locations: "
    for app in app_files:
        print "File: " + app.file.name + " for app <" + app.application.name + ">"

    # Prepare launcher arguments
    # FIXME: For now, just use first to words of the application name for the VM name
    if len(app_files) == 0:
        return HttpResponse("<h1> No image available to launch</h1>")
    else:

       # vm_name = "test"

        vm_name = str(app.application.name)
        #vm_name = split_name[0] + ' ' + split_name[1]
        app_owner = str(ApplicationBasicInfo.objects.filter(id=appid)[0].owner.username)
        #request.user.get_username()

        launcher_args = '    <argument>' + vm_name + '</argument>'
        for app in app_files:
            launcher_args += '\n    <argument>' + os.path.join(request.build_absolute_uri("/"), 'media', app_owner, os.path.basename(app.file.name)) + '</argument>'

        fs = FileSystemStorage()



        filedir = os.path.join(fs.location, 'jnlp', request.user.get_username())

        if not os.path.isdir(filedir):
            os.makedirs(filedir, 0700)
            print "Created user directory for JNLP launch files: " + filedir

        jnlp_file_name = tempfile.mktemp(suffix='.jnlp', dir=filedir)
        jnlp_file_url_path = os.path.join('/media', 'jnlp', request.user.get_username(), os.path.basename(jnlp_file_name))

        # We now generate the jnlp file which will be returned to the client in order
        # to begin the webstart process that will download and run the image.
        jnlp_properties = {'base_url': request.build_absolute_uri("/"),
                           'jnlp_location': jnlp_file_url_path,
                           'app_name': app.application.name,
                           'launcher_args': launcher_args,
                           }
        formatted_jnlp = jnlp_base.format(**jnlp_properties)

        print "Formatted JNLP: "+ formatted_jnlp

        # Write JNLP file to the filesystem
        with open(jnlp_file_name, 'w') as f:
            f.write(formatted_jnlp)

        return HttpResponse(formatted_jnlp, content_type='application/x-java-jnlp-file')


def start_server(appid, cred, endpoint, imageRecord, instance_type, image_info, request):
    if cred:
        print 'Retrieved credentials successfully.'
    else:
        # TODO: Add full error handling
        print 'ERROR: Unable to retrieve credentials'
        return HttpResponseNotFound
    if image_info:
        print 'Retrieved image info for image <' + image_info.image_id + '> successfully.'
    else:
        # TODO: Add full error handling
        print 'ERROR: Unable to retrieve image data'
        return HttpResponseNotFound()
    (access_key, secret_key) = utils.decrypt_cred_pair(cred.access_key, cred.secret_key)
    print 'Access key: ' + access_key
    print 'Secret key: ' + secret_key
    print 'About to connect to region <' + endpoint + '> with access_key <' + str(
        access_key) + '> and secret_key <' + str(secret_key) + '>'
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
        print 'ERROR: Unable to find requested image ID on the selected cloud platform'
        return HttpResponseNotFound()
    else:
        print 'Image is available, about to start image with id <' + image_data.id + '>...'
    response_data = {}
    reservation = conn.run_instances(image_data.id, 1, 1, key_name=None, security_groups=None, user_data=None,
                                     addressing_type=None, instance_type=instance_type, placement=None)
    print 'Instance pending with reservation ID: ' + reservation.id
    instance_ids = []
    for i in reservation.instances:
        instance_ids.append(i.id)
    app = ApplicationBasicInfo.objects.get(id=appid)
    appimg = ApplicationOpenstackImages.objects.get(id=imageRecord)
    creds = UserCloudCredentials.objects.get(id=cred.id)
    for id in instance_ids:
        instanceRecord = CloudInstancesOpenstack(owner=request.user,
                                                 application=app,
                                                 application_image=appimg,
                                                 credentials=creds,
                                                 instance_id=id,
                                                 status='PENDING')
        instanceRecord.save()
    response_data['result'] = 'OK'
    response_data['reservationId'] = reservation.id
    response_data['instanceIds'] = instance_ids
    response_data['instanceRecord'] = instanceRecord.id
    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")


@require_POST
@login_required
def launchserver(request, appid, launchtype):
    print 'Request to launch cloud server for application: ' + appid

    endpoint = request.POST['endpoint']
    instance_type = request.POST['resource_type']
    #instance_type = 'Large'
    alias = request.POST['alias']
    recordId = request.POST['recordId']
    cloud = recordId.split(':')[0]
    imageRecord = recordId.split(':')[1]

    print instance_type

    print 'Launch server on cloud <' + cloud + '> with image record <' + imageRecord + '> using credential alias <' + alias + '> and cloud url <' + endpoint + '>'

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

    return start_server(appid, cred, endpoint, imageRecord,instance_type, image_info, request)

@require_POST
@login_required
def manage_instances(request, task, appid, instancerecord):
    response_data = {}

    print 'Request received by manage instances.'

    if task == 'status':
        print 'Request to undertake management task <' + task + '> for application id <' + appid + '>'

        application = ApplicationBasicInfo.objects.get(id=appid)
        instances = CloudInstancesOpenstack.objects.filter(owner=request.user, application=application)

        if len(instances) == 0:
            return HttpResponse(simplejson.dumps(response_data), content_type="application/json")

        # Prepare Openstack connection
        credentials = instances[0].credentials
        (access_key, secret_key) = utils.decrypt_cred_pair(credentials.access_key, credentials.secret_key)
        parsed_url = urlparse(credentials.endpoint)
        ip = parsed_url.netloc.split(':')[0]
        local_region = boto.ec2.regioninfo.RegionInfo(name="openstack", endpoint=ip)
        conn = boto.connect_ec2(aws_access_key_id=access_key,aws_secret_access_key=secret_key,is_secure=False,region=local_region,port=parsed_url.port,path=parsed_url.path)

        #TODO: Add timeout if instance not accessible

        print 'Set up connection with IP <' + ip + '>, port <' + str(parsed_url.port) + '> and path <' + parsed_url.path + '>.'

        for instance in instances:
            print 'Getting updated data for instance: ' + instance.instance_id
            if instance.credentials.id != credentials.id:
                print "Instance " + instance.instance_id + " uses different credentials, updated openstack connection..."
                credentials = instance.credentials
                (access_key, secret_key) = utils.decrypt_cred_pair(credentials.access_key, credentials.secret_key)
                parsed_url = urlparse(credentials.endpoint)
                ip = parsed_url.netloc.split(':')[0]
                local_region = boto.ec2.regioninfo.RegionInfo(name="openstack", endpoint=ip)
                conn = boto.connect_ec2(aws_access_key_id=access_key,aws_secret_access_key=secret_key,is_secure=False,region=local_region,port=parsed_url.port,path=parsed_url.path)

            instance_data= conn.get_all_instances(instance_ids=[instance.instance_id])
#             r1 = instance_data[0]
#             instance = r1.instances[0]
#             print instance.state
#             print r1
            #instance_data = conn.get_only_instances(instance_ids=[instance.instance_id])
            # If nothing was returned, we assume this instance has shut down so delete it from the DB
            if len(instance_data) == 0:
                CloudInstancesOpenstack.objects.filter(instance_id=instance.instance_id).delete()
                print 'Deleted record for server with instance ID <' + instance.instance_id + '> that no longer exists.'
            else:
                print 'Instance <' + instance_data[0].instances[0].id + '> currently in state <' + instance_data[0].instances[0].state + '> with IP <' + instance_data[0].instances[0].public_dns_name + '>'

                instance_info = {}
                instance_info['id'] = instance_data[0].instances[0].id
                instance_info['state'] = instance_data[0].instances[0].state
                # Update instance state in DB
                if instance_info['state'] != instance.status:
                    instance.status = instance_info['state']
                    instance.save()
                instance_info['ip'] = instance_data[0].instances[0].public_dns_name

                response_data[instance_data[0].instances[0].id] = instance_info




    elif task == 'shutdown':
        print 'Request to shutdown instance ' + instancerecord + ' for application: ' + appid

        application = ApplicationBasicInfo.objects.get(id=appid)
        instance = None
        try:
            instance = CloudInstancesOpenstack.objects.get(owner=request.user, application=application, instance_id=instancerecord)
        except CloudInstancesOpenstack.DoesNotExist:
            print 'A cloud instance could not be found for ID ' + instancerecord + ' for application: ' + appid + " for the current user."

        if instance != None:
            #print '<' + str(instance.length) + '> matching instances found. Shutting down the first matching instance.'
            print 'Matching instance found. Shutting this instance down.'

            inst_for_shutdown = instance
            # Prepare Openstack connection
            credentials = inst_for_shutdown.credentials
            (access_key, secret_key) = utils.decrypt_cred_pair(credentials.access_key, credentials.secret_key)
            parsed_url = urlparse(credentials.endpoint)
            ip = parsed_url.netloc.split(':')[0]
            local_region = boto.ec2.regioninfo.RegionInfo(name="openstack", endpoint=ip)
            conn = boto.connect_ec2(aws_access_key_id=access_key,aws_secret_access_key=secret_key,is_secure=False,region=local_region,port=parsed_url.port,path=parsed_url.path)

            terminated_instances = conn.terminate_instances(str(instancerecord))
            print "Shutting down " + str(len(terminated_instances)) + " instances."

            terminate_instance_result = terminated_instances[0].id

            response_data['result'] = 'OK'
            response_data['terminated'] = terminate_instance_result

        else:
            response_data['result'] = 'ERROR'
            response_data['reason'] = 'Instance not found for application <' + appid + '> and instance ID <' + instancerecord + '>'



    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")
