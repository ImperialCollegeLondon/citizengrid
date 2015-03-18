import os
import bz2
import base64
import json

import boto.ec2
from urlparse import urlparse

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.core.files.storage import FileSystemStorage
from django.contrib.formtools.wizard.views import SessionWizardView
from django.http import HttpResponse
from Crypto.Cipher import AES
from django.shortcuts import redirect
import simplejson
from rest_framework import status
from django.http.response import HttpResponseNotAllowed, HttpResponseNotFound,\
    HttpResponseForbidden, HttpResponseRedirect
from django.forms.util import ErrorList
from django.template.loader import render_to_string
from citizengrid.models import UserInfo, ApplicationBasicInfo, ApplicationServerInfo, ApplicationClientInfo, Branch, Category, SubCategory, \
    UserCloudCredentials,UsersApplications, CloudInstancesOpenstack
from citizengrid.models import ApplicationEC2Images, ApplicationOpenstackImages
from citizengrid.forms import ApplicationBasicInfoForm, ApplicationServerInfoForm, ApplicationClientInfoForm, CloudCredentialsForm, CloudImageForm, \
    UpdateUserCreationForm,LocalImageForm
from citizengrid.models import ApplicationFile,MyGroup,GroupApplicationTag
from citizengrid import DATA_K
from citizengrid.forms import ExtendedUserCreationForm
from django.contrib.auth.models import User
import citizengrid.view_utils as view_utils
from citizengrid.view_utils import application_provider_view_data
from django.template import loader, Context
import utils
import view_utils
import views
from django.db import IntegrityError, transaction
from visicon import gen_icon



@login_required
def update_user_account(request):
    userdata = User.objects.filter(username = request.user)
    username= userdata[0].username
    email=userdata[0].email
    first_name=userdata[0].first_name
    last_name=userdata[0].last_name
    formdata = {'email': email, 'first_name': first_name, 'last_name': last_name}

    if request.method == 'POST' and 'btn-save' in request.POST:
        form = UpdateUserCreationForm(request.POST)
        action = "update"
        print str(form)
        if form.is_valid():
            userdata = form.update(userdata[0])
            return render_to_response('registration/confirm.html', {'action': action}, context_instance=RequestContext(request))
        else:
            print "The form is invalid"
            form = UpdateUserCreationForm(formdata)
    elif request.method == 'POST' and 'btn-cancel' in request.POST:
         action = "cancel"
         return render_to_response('registration/confirm.html', {'action': action}, context_instance=RequestContext(request) )
    else:
        form = UpdateUserCreationForm(formdata)


    return render_to_response('registration/update.html', {'form': form}, context_instance=RequestContext(request))



@login_required
def cg(request):
    # View code here...
    print "CitizenGrid main page requested..."

    # Get the user info for the current user
    user_info_list = UserInfo.objects.filter(user=request.user)
    if len(user_info_list) != 1:
        print "ERROR: Looking up info for user " + request.user.username + " and it can't be found!"
        return

    user_info = user_info_list[0]

    print user_info

    # First we need to find out what the user's role is
    # and transfer control to the relevant function to display
    # the right view.
    # We know who the user is so we can look up this information
    # What do to do is defined by citizengrid_userinfo.user_status
    # and citizengrid_userinfo.user_primary_role. Status may be 'N' (New) or
    # 'A' (Active). Primary role may be 'U' (User) or 'P' (Provider).
    user_status = user_info.user_status
    user_role = user_info.user_primary_role

    # Before transferring control to next stage,
    # check if a role change was requested or if
    # we've just come from the welcome page
    if request.method == 'GET':
        if request.GET.get("change-role") != None:
            print "CHANGE ROLE REQUESTED..."
            user_info.user_status='N'
            user_info.save()
            user_status = user_info.user_status
        else:
            print "NO ROLE CHANGE REQUESTED, standard cg request..."
    if request.method == 'POST':
        # If a value for the welcome_values checkbox is not present
        # then we've not come from the welcome page
        if 'cancelWelcome' not in request.POST:
            print 'WE HAVEN\'T COME FROM THE WELCOME PAGE, NOT ATTEMPTING TO PROCESSING WELCOME DATA'
        else:
            welcome_values = request.POST.get("cancelWelcome", "")
            print "Welcome values: " + welcome_values

            # Find which submit button was pressed...
            app_user = request.POST.get("app_user", None)
            app_provider = request.POST.get("app_provider", None)
            cancel = request.POST.get("cancel",None)
            print "APP_USER: " + str(app_user)
            print "APP_PROVIDER: " + str(app_provider)
            print "Cancel " + str(cancel)
            # If the box is checked, set the user to be active,
            # otherwise leave them as a new user
            if welcome_values == 'true':
                user_info.user_status='A'
            elif welcome_values == 'false':
                user_info.user_status='N'
            user_info.save()

            print "User info obtained for user before updating primary role" + request.user.username + " User status: " + user_info.user_status + " User primary role: " + user_info.user_primary_role

            if app_user != None:
                print "APP_USER BUTTON PRESSED"
                user_info.user_primary_role = 'U'
                user_info.user_primary_role_desc='Application User'
                user_info.save()
                return cg_user(request)
            elif app_provider != None:
                print "APP_PROVIDER BUTTON PRESSED"
                user_info.user_primary_role = 'P'
                user_info.user_primary_role_desc='Application Provider'
                user_info.save()
                return cg_provider(request)
            else:
                print "Cancel pressed"
                print user_info.user_primary_role_desc
            if user_info.user_primary_role == 'U':
                return cg_user(request)
            else:
                return cg_provider(request)


    # Now transfer processing to relevant function
    if user_status == 'N':
        return render_to_response('cg_new.html', {'next':'/'}, context_instance=RequestContext(request))
    elif user_role == 'U':
        return cg_user(request)
    elif user_role == 'P':
        return cg_provider(request)

@login_required
def cg_user(request):
    # Get all public applications to be displayed in the application list

    (apps,file_info_dict,role,myapps) = view_utils.application_user_view_data(request)

    return render_to_response('cg_main_user.html', {'apps':apps, 'myapps':myapps, 'file_info': file_info_dict,'role':role}, context_instance=RequestContext(request))


@login_required
def cg_provider(request):
    #return ApplicationNewAppWizard_view(request)
    apps = []
    active_tab = 'MA' # Can be MA for "My Apps" or NA for "New Application"
    (branches,category,subcategory,form,apps,formErrorVal, file_info_dict, os_images, ec2_images,role) = application_provider_view_data(request)
    return render_to_response('cg_provider_newapp_basic.html',
                              {'next':'/', 'branches':branches,'category':category,'subcategory':subcategory,'form':form,'apps':apps,
                               'hasFormError': formErrorVal,'active_tab':active_tab, 'file_info': file_info_dict, 'os_images':os_images,
                               'ec2_images': ec2_images,'role':role}, context_instance=RequestContext(request))



# The upload URL will handle uploaded files sent via a POST
# or, if a GET request is sent, it will return any pending
# upload files.
@login_required
def upload(request):
    result_list = []

    # If we've recieved a POST request, look for included file data
    if request.method == 'POST':
        file_list = request.FILES['files[]']

        if not isinstance(file_list, list):
            file_list = [file_list]

        print "File upload: Received info for " + str(len(file_list)) + " files."

        fs = FileSystemStorage()

        if not os.path.isdir(os.path.join(fs.location, request.user.get_username())):
            os.makedirs(os.path.join(fs.location, request.user.get_username()), 0700)
            print "Created user directory for file uploads: " + str(os.path.join(fs.location, request.user.get_username()))

        for upload_file in file_list:
            print "File name: " + upload_file.name
            print "File size: " + str(upload_file.size) + "bytes"

            file_extn = os.path.splitext(upload_file.name)[1]

            file_fmt_extns = {'.ovf':'OVF','.ova':'OVA','.iso':'ISO','.vmdk':'VMDK','.vdi':'VDI','.hd':'RAW','.img':'RAW'}

            file_fmt = file_fmt_extns.get(file_extn,'NONE');

            app_file = ApplicationFile(file=upload_file, owner=request.user, file_format=file_fmt)
            app_file.save()

            # with fs.open(os.path.join(request.user.get_username(), file.name), 'wb+') as destination:
            #     for chunk in file.chunks():
            #         destination.write(chunk)
            #     destination.close()

            result_item = {}
            result_item["name"] = upload_file.name
            result_item["url"] = os.path.join("media", request.user.get_username(), upload_file.name)
            result_item["thumbnail_url"] = ""
            result_item["deleteUrl"] = os.path.join('cg', 'delupload', str(app_file.id))
            result_item["deleteType"] = "GET"
            result_item["size"] = upload_file.size
            result_list.append(result_item)

    # If we've received a get request, look for any pending temp uploads
    # for this user and return file info.
    elif request.method == 'GET':
        tempfiles = ApplicationFile.objects.filter(file_type='T', owner=request.user)
        for app_file in tempfiles:
            result_item = {}
            result_item["name"] = app_file.filename()
            result_item["url"] = os.path.join("media", request.user.get_username(), app_file.filename())
            result_item["thumbnail_url"] = ""
            result_item["deleteUrl"] = os.path.join('cg', 'delupload', str(app_file.id))
            result_item["deleteType"] = "GET"
            result_item["size"] = app_file.file.size
            result_list.append(result_item)
    else:
        return HttpResponseNotAllowed()

    return HttpResponse(simplejson.dumps({'files': result_list}), 'application/json')

@login_required
@require_GET
def delupload(request, uploadid):
    print 'Received a request to delete uploaded temporary file with id: ' + uploadid
    # Begin by looking up the file and checking that its still in temp
    # state and owned by the requesting user
    app_file = ApplicationFile.objects.get(id=uploadid)
    if not app_file:
        return HttpResponseNotFound('ERROR: File with upload id ' + uploadid + ' could not be found...')
    if app_file.owner != request.user:
        return HttpResponseForbidden('ERROR: File with upload id ' + uploadid + ' can only be deleted by its owner...')
    if app_file.file_type != 'T':
        return HttpResponseForbidden('ERROR: File with upload id ' + uploadid + ' is registered to an application and cannot be deleted.')

    # If we've passed these checks we can now delete the file and then its DB record.
    app_file.file.delete()
    app_file.delete()

    return HttpResponse('OK')

@login_required
def manage_credentials(request):
    cloud_creds = []
    PADDING = '{'

    # Prepare list of openstack credentials to return to view
    #openstack_db_creds = UserOpenstackCredentials.objects.filter(user=request.user)
    cloud_db_creds = UserCloudCredentials.objects.filter(user=request.user)
    key = base64.decodestring(bz2.decompress(base64.decodestring(DATA_K)))

    for cred in cloud_db_creds:
        cipher = AES.new(key, AES.MODE_CBC, "enw4d2e3w66dugh2")
        decoded_key = base64.decodestring(cred.access_key)
        access_key = cipher.decrypt(decoded_key)
        access_key = access_key.rstrip(PADDING)

        new_cred = {}
        new_cred['host_cloud'] = cred.host_cloud
        new_cred['alias'] = cred.key_alias
        new_cred['access_key'] = access_key
        new_cred['endpoint'] = cred.endpoint
        new_cred['id'] = cred.id
        cloud_creds.append(new_cred)

        print 'New cred access key: [' + new_cred['access_key'] + ']'

    role = view_utils.return_role(request)

    return render_to_response('cg_manage_credentials.html', {'next':'/', 'cloud_creds':cloud_creds,'role':role}, context_instance=RequestContext(request))

@login_required
def manage_groups(request):
    print " Inside manage groups."
    groups = MyGroup.objects.select_related().all().filter(user=request.user)

    print 'in manage groups with groups retrieved ' + str(len(groups))

    role = view_utils.return_role(request)
    return render_to_response('cg_manage_groups.html', {'next':'/', 'groups':groups,'role':role}, context_instance=RequestContext(request))

@login_required
def application_list(request):
    print " All groups "
    apps = ApplicationBasicInfo.objects.all()
    select_data = """ <select name=attach_app_list id="attach_app_list" class="form-control"  placeholder="Applications">
    <option value="0">Nothing Selected</option>
    """
    for mg in apps :
        select_data = select_data + "<option value=\"" + str(mg.id) + "\">" + mg.name + "</option>"
    select_data = select_data + """</select> """
    print select_data
    return HttpResponse(select_data,content_type="application/html")

@login_required
def groups(request):
    print " Entering all applications method "
    apps = MyGroup.objects.select_related().exclude(user=request.user)
    select_data = """ <select name =groups[] id="joingroup" class="form-control"  placeholder="Groups" name="group" multiple> """
    for mg in groups :
        select_data = select_data + "<option value=\"" + str(mg.id) + "\">" + mg.name + "</option>"
    select_data = select_data + """</select> """
    print select_data
    return HttpResponse(select_data,content_type="application/html")



@login_required
def detail_group(request,id):
    group = MyGroup.objects.select_related().get(id=id)
    all_apps = []
    all_applications = ApplicationBasicInfo.objects.all()
    for a in all_applications:
        app = {}
        app['id'] = a.id
        app['desc'] = a.description
        app['name'] = a.name
        all_apps.append(app)
    return HttpResponse(
            json.dumps({'id': group.id, 'grpname': group.name, 'grpdesc': group.description,'apps':all_apps}),
            content_type="application/json")

@login_required
def edit_group(request,id):
    print "Inside backend Edit group routine"
    print  'grpname' in request.POST
    if 'grpname' in request.POST:
        try:

            #with transaction.atomic:
            mg = MyGroup.objects.get(id=id)
            print str(request.POST['grpname'])
            print str(request.POST['grpdesc'])
            mg.name = str(request.POST['grpname'])
            mg.description = str(request.POST['grpdesc'])
            mg.save()
        except IntegrityError as e:
            print e.message

        success_data = """
        <span>Your group creation request is successful. Here is what you submitted:</span><br><br>
        <strong>Name:</strong>""" + str(request.POST['grpname']) + "<br>"
        #return HttpResponse( success_data,content_type="application/html")
        return HttpResponseRedirect('/cg/manage/group')
    else:
        print "Sufficient information not present in the request to create a group"
        return HttpResponse( "<p> Invalida Data </p>",content_type="application/html")
        #return "<p> Invalida Data </p>"


@login_required
def leave_group(request,id):
    print "Inside leave group routine"
    groups = MyGroup.objects.select_related().filter(user=request.user).get(id=id)
    groups.user.remove(request.user)
    groups.save()
    groups = MyGroup.objects.select_related().all().filter(user=request.user)
    role = view_utils.return_role(request)
    html =  render_to_string('ajaxgrouptemplate/group_delete_template.html', { 'groups':groups,'role':role}, context_instance=RequestContext(request))
    return HttpResponse(html)

@login_required
def delete_group(request,id):
    print "Inside delete group"
    MyGroup.objects.filter(id=id).delete()
    groups = MyGroup.objects.select_related().all().filter(user=request.user)
    role = view_utils.return_role(request)
    html =  render_to_string('ajaxgrouptemplate/group_delete_template.html', { 'groups':groups,'role':role}, context_instance=RequestContext(request))
    return HttpResponse(html)

@login_required
def join_group(request):
    print "Inside Join group"
    print 'ids[]' in request.POST
    ids = request.POST.getlist('ids[]')
    int_ids = [int(str(i)) for i in ids]
    try:
        with transaction.atomic():
            for i in int_ids:
                group = MyGroup.objects.select_related().get(id=i)
                group.user.add(request.user)
                group.save()
    except IntegrityError as e:
        print e.message
    return manage_groups(request)

@login_required
def add_group(request):
    print  'grpname' in request.POST
    print request.POST
    if 'grpname' in request.POST:
        try:

            #with transaction.atomic:
                mg = MyGroup(name=str(request.POST['grpname']),description=str(request.POST['grpdesc']),group_role='O')
                mg.save()
                mg.user.add(request.user)
        except IntegrityError as e:
            print e.message

        success_data = """
        <span>Your group creation request is successful. Here is what you submitted:</span><br><br>
        <strong>Name:</strong>""" + str(request.POST['grpname']) + "<br>"
        #return HttpResponse( success_data,content_type="application/html")
        return HttpResponseRedirect('/cg/manage/group')
    else:
        print "Sufficient information not present in the request to create a group"
        return HttpResponse( "<p> Invalid Data </p>",content_type="application/html")
        #return "<p> Invalida Data </p>"

@login_required
def attach_app_to_group(request,id):
    if 'tagname' in request.POST:
        tagname = str(request.POST['tagname'])
        tagdesc = request.POST['tagdesc']
        tagid = request.POST['tagid']
        appid = request.POST['appid']
        print appid
        application =  ApplicationBasicInfo.objects.get(id=appid)
        mg = MyGroup.objects.get(id=id)
        print "Application %s to be attached to the group %s with tagid %s and tagname %s " %(application.name,mg.name,tagid,tagname)
        try:
            gat = GroupApplicationTag(tagname=tagname,description=tagdesc,tagid=tagid,application=application,group=mg)
            gat.save()
        except IntegrityError as e:
            print e.message
            return HttpResponse( "<p> Invalid Data </p>",content_type="application/html")
        success_data = """
        Your group application tag creation request is successful."""
        return HttpResponse(success_data,content_type="application/html")
    else:
        return HttpResponse( "<p> Invalid Data </p>",content_type="application/html")



@login_required
def application_grp_tag_detail(request):
    print "Inside Group Application Tag details method"
    if 'id' in request.GET:
        grpid = request.GET['id']
        gats = GroupApplicationTag.objects.filter(group=grpid)
        print gats
        html = render_to_string('ajaxgrouptemplate/group_application_tag_grid.html', { 'gats':gats}, context_instance=RequestContext(request))
        return HttpResponse(html)
    else:
        return HttpResponse( "<p> Invalid Data </p>",content_type="application/html")


@login_required
def detach_app_from_group(request,id):
    gat = GroupApplicationTag.objects.get(id=request.POST['id'])
    grpid = gat.group.id
    # deleting relevant tag
    GroupApplicationTag.objects.get(id=id).delete()
    #preparing the view
    gats = GroupApplicationTag.objects.filter(group=grpid)
    html = render_to_string('ajaxgrouptemplate/group_application_tag_grid.html', { 'gats':gats}, context_instance=RequestContext(request))
    return HttpResponse(html)



# Called via an AJAX call from a modal on the credential management page
# This view returns only the HTML content for the modal itself. The main
# view is rendered from the cg_manage_credentials template.
@login_required
def add_update_credentials(request):
   # print 'Received add/update request for platform [' +platform + '] and alias [' + str(alias) + '].'

    # The alias that will be passed to the pop-up modal box
    # if the user has requested creation of a new credential set
    global access_key_enc, secret_key_enc
    alias = ''
    PADDING = '{'
    BLOCK_SIZE = 16

    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING


    # If data was posted then this is a request to add/update credentials

    # Prepare the main properties to return for the modal form
    modal_data = {}
    #modal_data['id'] = request.id
    modal_data['target'] = "#cloudModal"
    modal_data['action'] = "/cg/manage/cred/cloud"
    modal_data['method'] = 'POST'

    # Before adding credentials we encrypt them with a secret key
    key = base64.decodestring(bz2.decompress(base64.decodestring(DATA_K)))
    print 'The key is: ' + key
    id = ''
    if request.method == 'POST':
        credentials = None

        form = CloudCredentialsForm(request.POST)

        if form.is_valid():
            cloud = form.cleaned_data['cloud']
            alias = form.cleaned_data['alias']
            access_key = form.cleaned_data['access_key']
            secret_key = form.cleaned_data['secret_key']
            endpoint = form.cleaned_data['endpoint']

            print "Cloud credential form valid:"
            print "\tCloud:" + cloud
            print "\tAlias: " + alias
            print "\tAccess key: " + access_key
            print "\tSecret key: " + secret_key
            print "\tEndpoint: " + endpoint

                # Check if this alias already exists
            existing_records = UserCloudCredentials.objects.filter(user=request.user, key_alias=alias)
            if existing_records:
                print 'ERROR: This alias already exists.'
                if not 'alias' in form.errors.keys():
                    form.errors['alias'] = ErrorList([])
                    form.errors['alias'].append('A credential set with this alias already exists.')

            else:
                keys_ok = False

                cipher = AES.new(key, AES.MODE_CBC, "enw4d2e3w66dugh2")
                try:
                    if len(access_key) % BLOCK_SIZE == 0:
                        access_key_enc = cipher.encrypt(access_key)
                    else :
                        if len(access_key) % BLOCK_SIZE != 0:
                            access_key = pad(access_key)
                            access_key_enc = cipher.encrypt(access_key)
                    keys_ok = True
                except ValueError as e:
                    print 'ERROR: ' + e.message
                    if not 'access_key' in form.errors.keys():
                        form.errors['access_key'] = ErrorList([])
                        form.errors['access_key'].append(e.message)
                    keys_ok = False
                try:
                    if len(secret_key) % BLOCK_SIZE == 0:
                        secret_key_enc = cipher.encrypt(secret_key)
                    else :
                        if len(secret_key) % BLOCK_SIZE != 0:
                            secret_key = pad(secret_key)
                            secret_key_enc = cipher.encrypt(secret_key)
                    keys_ok = True
                except ValueError as e:
                    print 'ERROR: ' + e.message
                    if not 'secret_key' in form.errors.keys():
                        form.errors['secret_key'] = ErrorList([])
                        form.errors['secret_key'].append(e.message)
                    keys_ok = False
                if keys_ok:
                    credentials = UserCloudCredentials(user=request.user,host_cloud=cloud,key_alias=alias,
                                                           access_key=base64.encodestring(access_key_enc)[:-1],
                                                           secret_key=base64.encodestring(secret_key_enc)[:-1],
                                                           endpoint=endpoint)
                    credentials.save()
                    print 'Created new credential set with ID: ' + str(credentials.id)
                else:
                    print 'New credential set not created, there was a key error'
        else:
            print 'The Credentials form that was submitted is invalid.'
            print form.errors

    credentials_registered = False
    if credentials is not None:
        credentials_registered = True
        form = CloudCredentialsForm()
        id= credentials.id

    return render_to_response('cg_cred_modal.html', {'form':form, 'id':id,'modal_data':modal_data, 'credentials_registered':credentials_registered, 'alias': alias}, context_instance=RequestContext(request))

@login_required
def manage_images(request, app):
    app_id=int(app)
    # Get app from the DB
    application = ApplicationBasicInfo.objects.filter(id=app_id)[0]

    fs = FileSystemStorage()

    if request.user != application.owner:
        return HttpResponseForbidden('ACCESS DENIED: You cannot manage the images for this application, you are not the owner.')

    if request.method == 'POST':
        if 'cif' in request.POST:
            cif = CloudImageForm(request.POST)
            if cif.is_valid():
                print "CIF cleaned data is " + str(cif.cleaned_data)
                cloud = cif.cleaned_data['cloud']
                endpoint = cif.cleaned_data['endpoint']
                image_id = cif.cleaned_data['image_id']
                server_client = cif.cleaned_data['server_client']

                print 'New image form contents: '
                print 'Cloud: ' + cloud
                print 'Endpoint: ' + endpoint
                print 'Image ID: ' + image_id
                print 'Server or Client image: ' + server_client
                #===================================================================
                # TODO - refactor image create function to use single version rather
                # than using different versions
                #===================================================================

                #appserver = ApplicationServerInfo(appref=application,apphost=cloud,server_image_id=image_id,server_image_location=endpoint)
                #appserver.save()
                if cloud == 'Private':
                    new_image = ApplicationOpenstackImages(application=application,
                                                           image_id=image_id,
                                                           zone_name='',
                                                           zone_url=endpoint,
                                                           image_type=server_client)
                    new_image.save()
                    print 'Registered new Openstack image with ID: ' + str(new_image.id)
                elif cloud == 'Public':
                    new_image = ApplicationEC2Images(application=application,
                                                     image_id=image_id,
                                                     zone_name='',
                                                     zone_url=endpoint,
                                                     image_type=server_client)
                    new_image.save()
                    print 'Registered new AWS image with ID: ' + str(new_image.id)
        else:
            print "In else block"
            lif = LocalImageForm(request.POST,request.FILES)
            if lif.is_valid():
                lif_cleaned= str(lif.cleaned_data)
                local_image = request.FILES['local_image']
                local = lif.cleaned_data["local"]

                handle_uploaded_file(application.name,request,fs,local_image)
                new_image = ApplicationFile(owner = request.user,
                                            application = application,file=local_image.name,
                                            file_format = str(local).upper(),file_type='S'
                                            )
                new_image.save()
            else:
                print "LIF not clean" +str(lif.cleaned_data)

    else:
        cif = CloudImageForm()
    cif = CloudImageForm()

    # Now get all image files, EC2 and Openstack configs for the app
    local_images = ApplicationFile.objects.filter(application=app_id, owner=request.user)
    ec2_images = ApplicationEC2Images.objects.filter(application=app_id)
    openstack_images = ApplicationOpenstackImages.objects.filter(application=app_id)
    #append current role in the session :
    #TODO To be added in the session rather than passing as request param
    role = view_utils.return_role(request)
    print 'Local Image : '

    return render_to_response('cg_manage_images.html', {'app': application, 'role':role,'username': request.user.get_username(), 'local_images': local_images, 'ec2_images':ec2_images, 'openstack_images': openstack_images, 'cloud_image_form': cif}, context_instance=RequestContext(request))

@login_required
def get_running_servers(request):
    return HttpResponse()

@login_required
def get_cloud_credentials(request):
    if request.method != 'POST':
        return HttpResponseForbidden('ERROR: Invalid request...')
    """
    List cloud credentials
    """

    url = request.body
    #url = url.lstrip()
    
    print 'Received a request to get credentials:' + url

    creds = UserCloudCredentials.objects.filter(user_id=request.user, endpoint=url)

    cred_list = []
    for cred in creds:
        cred_list.append(cred.key_alias + ' - ' + utils.decrypt_cred(cred.access_key))

    response_data = {}
    response_data['credentials'] = cred_list

    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")



FORMS = [("step1", ApplicationBasicInfoForm),
         ("step2", ApplicationServerInfoForm),
         ("step3", ApplicationClientInfoForm)]

TEMPLATES = {"step1": "cg_provider_wizard_step1.html",
              "step2": "cg_provider_wizard_step2.html",
              "step3": "cg_provider_wizard_step3.html"}


"""
    Subclasses SessionWizard to control wizard layout in UI
"""
class ApplicationNewAppWizard(SessionWizardView):

        file_storage = FileSystemStorage(location=os.path.join('citizengrid','media'))
        def get_template_names(self):
            return [TEMPLATES[self.steps.current]]

        #
        #    Context updated to populate category view
        #
        def get_context_data(self, form, **kwargs):
            context = super(ApplicationNewAppWizard, self).get_context_data(form=form, **kwargs)
            initial_dict = self.get_form_initial('1')
            if self.steps.current == '2':
                step1_data = self.get_cleaned_data_for_step('1')
                context.update({'step1_data':step1_data,'category': Category.objects.all(),'branches':Branch.objects.all(),'subcategory':SubCategory.objects.all(),})
            else:
                step1_data = self.get_cleaned_data_for_step('1')
                step2_data = self.get_cleaned_data_for_step('2')
                context.update({'step1_data':step1_data,'step2_data':step2_data,'category': Category.objects.all(),'branches':Branch.objects.all(),'subcategory':SubCategory.objects.all(),})
            return context

        #=======================================================================
        # Processes file upload of server and client images.
        # TODO - Processing file at this stage is incorrect, we
        # need to do file upload and db update  in the last stage, if there is any error
        # delete the files
        #=======================================================================
        def process_step(self,form,**kwargs):
            print str("In the step" + self.steps.current)
            if self.steps.current== 'step1':
                self.extra_context = {'cat_1': 1,'subcat_1':1}
                print str(form.cleaned_data)

                if 'iconfile' in form.cleaned_data and 'name' in form.cleaned_data:
                    fs = FileSystemStorage()
                    file = form.cleaned_data['iconfile']
                    name = str(form.cleaned_data['name'])
                    handle_uploaded_file_icon(name, self.request,fs,file)
            return self.get_form_step_data(form)

        """
        Overrides get_form_initial from SessionWizard to populate form values with
        initial values.
        """
        def get_form_initial(self, step):
            print self.get_form_list()
            print "Entering Now" + str(self.storage.get_step_data('step2'))
            initial ={}
            if self.storage.get_step_data('step1') is not None:
                val = self.storage.get_step_data('step1')
                initial.update({'step1': {'name':val['step1-name'],
                                          'step1-select_category' :val['step1-select_category'],
                                          'description':val['step1-description'],'additional_Information':val['step1-additional_Information'],
                                          'keywords':val['step1-keywords']}})
            if self.storage.get_step_data('step2') is not None:
                val = self.storage.get_step_data('step2')

            self.initial_dict = initial
            return self.initial_dict.get(step, initial)

        """
        Overrides done method in SessionWizard , which submits the wizard form.
        """
        def done(self, form_list, **kwargs):
            request = self.request
            print self.storage.get_step_data('step1')
            t=self.storage.get_step_data('step1')
            print "step 2 is %s" %(str(self.storage.get_step_data('step2')))
            print "step 3 is %s" %(str(self.storage.get_step_data('step3')))
            print "Inside ApplicationNewappWizard"

            step2 = self.storage.get_step_data('step2')
            step3 = self.storage.get_step_data('step3')
            name = self.get_cleaned_data_for_step('step1')['name']
            desc = self.get_cleaned_data_for_step('step1')['description']
            keywords = self.get_cleaned_data_for_step('step1')['keywords']
            # sets public field to boolean value for storing in database
            public = 0
            if t['public'] == 'TRUE':
                public =1
            else:
                public = 0

            apphost = step2['step2-server_hosting_platform']
            client_platform = step3['step3-client_platform']

            #self.get_cleaned_data_for_step('step2')['step2-server_hosting_platform']
            server_image_id = self.get_cleaned_data_for_step('step2')['server_image_id']
            server_image_location = self.get_cleaned_data_for_step('step2')['server_image_location']
            client_image_id = self.get_cleaned_data_for_step('step3')['client_image_id']
            client_image_location = self.get_cleaned_data_for_step('step3')['client_image_location']

            category = t.getlist('cat')
            subcategory = t.getlist('subcat')
            try:

                with transaction.atomic():

                    app = ApplicationBasicInfo(owner=request.user, name=name,description=desc,client_downloads=0,public=public,keywords=keywords)
                    app.save()
                    app.branch = t.getlist('step1-select_category')
                    app.category = t.getlist('cat')
                    app.subcategory = t.getlist('subcat')

                    # Generate the identicon for the application
                    fs = FileSystemStorage()

                    icon_location = os.path.join('media',request.user.get_username())
                    #icon_location = os.path.join(fs.location, '..', 'static', 'img', 'ident')
                    #gen_icon.create_icon(icon_location)
                    #icon_location = os.path.join(fs.location, request.user.username, name)
                    iconfile_name = self.get_cleaned_data_for_step('step1')['iconfile'].name
                    print "inconfile is %s" %(self.get_cleaned_data_for_step('step1')['iconfile'].name)
                   # app.iconfile = os.path.join('img', 'ident', str(app.id)+'.png')
                    app.iconfile = os.path.join(icon_location, iconfile_name)
                    app.save()



                    appserver = ApplicationServerInfo(appref=app,apphost=apphost,server_image_id=server_image_id,server_image_location=server_image_location)
                    appclient = ApplicationClientInfo(appref=app,clienthost=client_platform,client_image_id=client_image_id,client_image_location=client_image_location)
                   # appserver.save()
                    appclient.save()

            except Exception as e:
                print " Cannot persist in DB , error %s occurred" %(e.message)
                raise HttpResponse(status=500)
            else:
                    # Uploading files here
                    file1 = self.get_form_step_files(form_list[1])
                    file2 = self.get_form_step_files(form_list[2])


                    uploadnew(name,request,file1['files[]'],"S") if 'files[]' in file1 and file1['files[]'] is not None else ""
                    #uploading client

                    uploadnew(name,request,file2['files[]'],"C") if 'files[]' in file2 and file2['files[]'] is not None else ""
                    #Saving Server Cloud details (EC2 and Openstack if given)
                    view_utils.store_cloud_details(app,'S',str(apphost),server_image_id,server_image_location)

                    #Store Client Cloud details
                    view_utils.store_cloud_details(app,'C',client_platform,client_image_id,client_image_location)

                    # Now that the model is stored, we switch the associated
                    # files to stored status and set the owning application to
                    # the one that's just been created.
                    tempfiles = ApplicationFile.objects.filter(file_type='T', owner_id=request.user)
                    for tempfile in tempfiles:
                        tempfile.file_type='S'
                        tempfile.application = app
                        tempfile.save()

                    print 'Created new application with ID: ' + str(app.id)

            return render_to_response('cg_app_creation_done.html', {'form_data': [form.cleaned_data for form in form_list], })



ApplicationNewAppWizard_view = ApplicationNewAppWizard.as_view(FORMS)

@login_required
def wrapped_wizard_view(request):
    return ApplicationNewAppWizard_view(request)

#===============================================================================
#     getTableData : Upload Server or client images
#    steptype - client or server stage file image
#===============================================================================
@login_required
def getTableData(request):
    data = ApplicationBasicInfo.objects.all().prefetch_related("branch","category","subcategory").filter(public=1).order_by('id')
    app_list =[]
    for d in data:
        ls ={}
        ls['name']="<span class='demo hover' value='" + str(d.id) + "'>"+ d.name +"</span>"
        ls['description']= d.description
        ls['branch'] = [b.name for b in d.branch.all().order_by('id')]
        ls['category'] = [c.name for c in d.category.all().order_by('id')]
        ls['subcategory'] = [s.name for s in d.subcategory.all().order_by('id')]
        #ls['apphost'] = dict(ApplicationServerInfo.SERVER_APP_HOST_CHOICES).get(str(serverinfo[0]['apphost']))
        ls['keywords'] = d.keywords
        ls['owner'] = d.owner.username
        app_list.append(ls)

    jsonData ='{"aaData":'+ json.dumps(app_list) + ', "iTotalRecords": 10, "sEcho": 3, "iTotalDisplayRecords": 10}'
    return HttpResponse(jsonData, content_type="application/javascript")


@login_required
def getUserApps(request):
    print "In getUserApps"
    # Get all users applications to be displayed in the application list
    
    data = ApplicationBasicInfo.objects.filter(usersapplications__user=request.user).prefetch_related("branch","category","subcategory")
    app_list =[]
    for d in data:
        ls={}
        
        ls['name']="<span  data-target='#myModal' data-toggle='modal' class='hover' id='myapplink' value='" + str(d.id) + "'>"+ d.name +"</span>"
        ls['description']= d.description
        ls['branch'] = [b.name for b in d.branch.all().order_by('id')]
        ls['category'] = [c.name for c in d.category.all().order_by('id')]
        ls['subcategory'] = [s.name for s in d.subcategory.all().order_by('id')]
        #ls['apphost'] = dict(ApplicationServerInfo.SERVER_APP_HOST_CHOICES).get(str(serverinfo[0]['apphost']))
        ls['keywords'] = d.keywords
        ls['owner'] = d.owner.username
        app_list.append(ls)

    jsonData ='{"aaData":'+ json.dumps(app_list) + ', "iTotalRecords": 10, "sEcho": 3, "iTotalDisplayRecords": 10}'
    return HttpResponse(jsonData, content_type="application/javascript")




#===============================================================================
#     uploadnew : Upload Server or client images
#    file - Input file to be stored
#    steptype - client or server stage file image
#===============================================================================


def uploadnew(appname,request,file,steptype):
    print "Debug: Entering uploadnew"
    result_list = []

    # If we've recieved a POST request, look for included file data
    file_list = file

    if not isinstance(file_list, list):
        file_list = [file_list]

    print "File upload: Received info for " + str(len(file_list)) + " files."

    fs = FileSystemStorage()

    if not os.path.isdir(os.path.join(fs.location, request.user.get_username())):
        os.makedirs(os.path.join(fs.location, request.user.get_username()), 0700)
        print "Created user directory for file uploads: " + str(os.path.join(fs.location, request.user.get_username()))

    for upload_file in file_list:
        print "File name: " + upload_file.name
        print "File size: " + str(upload_file.size) + "bytes"

        file_extn = os.path.splitext(upload_file.name)[1]

        file_fmt_extns = {'.ovf':'OVF','.ova':'OVA','.iso':'ISO','.vmdk':'VMDK','.vdi':'VDI','.hd':'RAW','.img':'RAW'}

        file_fmt = file_fmt_extns.get(file_extn,'NONE')

        print "file_extn and file_fmt are %s %s"  %(file_extn,file_fmt)
        try:

            with transaction.atomic():

                app_file = ApplicationFile(file=upload_file.name, owner=request.user, file_format=file_fmt,image_type=steptype)
                app_file.save()

        except Exception,e:
            print "Reason is" + e.message
            print "File not uploaded !!!"
        else:


            # with fs.open(os.path.join(request.user.get_username(), file.name), 'wb+') as destination:
            #     for chunk in file.chunks():
            #         destination.write(chunk)
            #     destination.close()

            result_item = {}
            result_item["name"] = upload_file.name
            result_item["url"] = os.path.join("media", request.user.get_username(), upload_file.name)
            result_item["thumbnail_url"] = ""
            result_item["deleteUrl"] = os.path.join('cg', 'delupload', str(app_file.id))
            result_item["deleteType"] = "GET"
            result_item["size"] = upload_file.size
            result_list.append(result_item)

            print "File uploaded successfully"

    #===============================================================================
    #  Shows application detail
    #===============================================================================

@login_required
def application_detail(request,appid):
    # Get all public applications to be displayed in the application list
    app = ApplicationBasicInfo.objects.filter(public=True,id=appid)
    # Get the list of app ids that we're going to look up application files for.
    app_ids = [appid]
    print 'Looking up file for apps: ' + str(app_ids)

    files = ApplicationFile.objects.filter(file_type='S', image_type= 'C', application=int(appid))
    os_client_images = ApplicationOpenstackImages.objects.filter(application=int(appid), image_type= 'C')
    ec2_client_images = ApplicationEC2Images.objects.filter(application=int(appid), image_type= 'C')

    # We now have a list of files for all the applications.
    # For each application, prepare a new list. Each item in the list
    # will be a dict containing the details about a file for an application.
    # This list will then be added to the file_info_dict with the key
    # as the app id.
    file_info_dict = {}

    file_formats = { 'NONE': 'Local file (Unknown type)',
                   'HD' : 'Local image (RAW_ID)',
                   'IMG' : 'Local image (RAW_Image)',
                   'VDI' : 'Local image (Virtualbox)',
                   'VMDK': 'Local image (VMware VMDK)',
                   'ISO' : 'CD/DVD ROM Image',
                   'OVF' : 'OVF Appliance',
                   'OVA' : 'Local Appliance Archive (OVA)'}

    for appfile in files:
        if appfile.application.id not in file_info_dict:
            file_info_dict[appfile.application.id] = []
        file_info = {}
        file_info['appfile'] = appfile
        file_info['name'] = appfile.filename()
        file_info['path'] = os.path.join('media', request.user.username, appfile.filename())
        file_info['formatstring'] = file_formats[appfile.file_format]
        file_info_dict[appfile.application.id].append(file_info)
    return render_to_response('cg_application_detail.html', {'apps':app, 'file_info': file_info_dict,'os_images':os_client_images, 'ec2_images':ec2_client_images, })

    #===============================================================================
    #  Shows MY application detail
    #===============================================================================

@login_required
def my_application(request, appid):
    # Get some stuff to show
    app = ApplicationBasicInfo.objects.get(pk=appid);
    
    my_stats = UsersApplications.objects.get(user=request.user,application=appid)
    
    instances = CloudInstancesOpenstack.objects.filter(owner=request.user, application=app)

    files = ApplicationFile.objects.filter(application=appid)
    
    os_client_images = ApplicationOpenstackImages.objects.filter(application=appid)
    
    ec2_client_images = ApplicationEC2Images.objects.filter(application=appid)

    file_info_dict = {}
    instance_list = []
    
    for appfile in files:
        if appfile.application.id not in file_info_dict:
            file_info_dict[appfile.application.id] = []
        file_info = {}
        print "Got file " + str(appfile)
        file_info['appfile'] = appfile
        file_info['name'] = appfile.filename()
        file_info['path'] = os.path.join('media', request.user.username, appfile.filename())
        file_info['formatstring'] = appfile.file_format
        file_info_dict[appfile.application.id].append(file_info)
        
   
    if len(instances) > 0:
        print "Found " + str(len(instances)) + " openstack cloud instances"
        credentials = instances[0].credentials
        (access_key, secret_key) = utils.decrypt_cred_pair(credentials.access_key, credentials.secret_key)
        parsed_url = urlparse(credentials.endpoint)
        ip = parsed_url.netloc.split(':')[0]
        local_region = boto.ec2.regioninfo.RegionInfo(name="openstack", endpoint=ip)
        conn = boto.connect_ec2(aws_access_key_id=access_key,aws_secret_access_key=secret_key,is_secure=False,region=local_region,port=parsed_url.port,path=parsed_url.path)

        print 'Set up connection with IP ' + ip + ', port ' + str(parsed_url.port) + ', path ' + parsed_url.path

        for instance in instances:
            print 'For each instance: ' + instance.instance_id
            if instance.credentials.id != credentials.id:
                print "Instance " + instance.instance_id + " uses different credentials, updated openstack connection..."
                credentials = instance.credentials
                (access_key, secret_key) = utils.decrypt_cred_pair(credentials.access_key, credentials.secret_key)
                parsed_url = urlparse(credentials.endpoint)
                ip = parsed_url.netloc.split(':')[0]
                local_region = boto.ec2.regioninfo.RegionInfo(name="openstack", endpoint=ip)
                conn = boto.connect_ec2(aws_access_key_id=access_key,aws_secret_access_key=secret_key,is_secure=False,region=local_region,port=parsed_url.port,path=parsed_url.path)

            instance_data = conn.get_all_instances(instance_ids=[instance.instance_id])
            if len(instance_data) > 0:
                count = 1
                print 'Instance ID ' + instance_data[0].instances[0].id + ' in state ' + instance_data[0].instances[0].state + ' with IP ' + instance_data[0].instances[0].public_dns_name
                instance_info = {}
                instance_info['id'] = instance_data[0].instances[0].id
                instance_info['state'] = instance_data[0].instances[0].state
                instance_info['ip'] = instance_data[0].instances[0].public_dns_name
                instance_list.append( instance_info )


    return render_to_response('cg_myapp_template.html', {'my_stats':my_stats, 'app':app,'instance_list':instance_list, 'file_info': file_info_dict,'os_images':os_client_images, 'ec2_images':ec2_client_images })


    #===================================================================================================================================
    #    Handler for all delete requests from CG App
    #    params:
    #    request - Request dictionary containing form data
    #    id    - ID of delete app|file|image request
    #    Handles
    #        1). Delete Local images - Hitting citizengrid_applicationfile
    #        2). Delete Cloud images - Hitting both citizengrid_applicationec2images and citizengrid_osimage
    #        3). Delete applications - hitting Application(Basic,Sever,Client,File,, Storage) - should be part of db transaction
    #===================================================================================================================================
@login_required
def cg_delete(request,id):
    print "Inside CG_Delete"
    data =''
    if 'type' in request.POST:
        type = request.POST['type']
        if type == 'file':
            data = view_utils.delete_file(request,int(id))
        elif type == 'ec2' or type == 'os':
            data = view_utils.delete_cloud(request,type,str(id))
        elif type == 'app':
            data = view_utils.delete_cloud(request,type,int(id))
            #print 'data  is %s' %(data)
        elif type == 'oscred':
            data = view_utils.delete_cred(request,type,id)
            #print "returned data is %s" %(data)
        else:
            # No condition met for delete type
            data = "No match found!!.Cannot delete none type"
    else:
        print  "No type found" +  str(request.POST.get('type'))
    return HttpResponse(data)


def handle_uploaded_file(appname,request,fs,file):
    location = ""
    if appname is None:
        location  = os.path.join(fs.location,request.user.get_username())
    else:
        location = os.path.join(fs.location,request.user.get_username(), appname)
    if not os.path.isdir(location):
        os.makedirs(location,0700)
        print "Created user directory for  uploads: " + str(os.path.join(location))

    with fs.open(os.path.join(location,file.name), 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()

def handle_uploaded_file_icon(appname,request,fs,file):
        location = ""
        location = os.path.join(fs.location, request.user.get_username())
        if not os.path.exists(location):
            os.makedirs(location,0700)
            print "Created user directory for  uploads: " + str(os.path.join(location))

        with fs.open(os.path.join(location,file.name), 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()
