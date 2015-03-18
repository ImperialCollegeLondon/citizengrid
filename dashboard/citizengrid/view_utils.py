    #===============================================================================
    # View utils provide utility a.k.a helper methods for views - to ensure that we are
    # not cluttering view with helper functions.
    # Ensure to add all helper methods here. Views should be reserved for business specific
    # view functions
    #===============================================================================
import os
from visicon import gen_icon
from django.core.files.storage import FileSystemStorage
from citizengrid.forms import ApplicationBasicInfoForm
from citizengrid.models import ApplicationBasicInfo,ApplicationEC2Images,ApplicationOpenstackImages, UserInfo, UserCloudCredentials,\
    ApplicationFile,Branch, SubCategory, Category
from citizengrid.templatetags import cg_template_filters
from django.db.models import Q
from django.template.loader import render_to_string
from citizengrid.templatetags import cg_myapp_template

from citizengrid import DATA_K
import bz2
import base64
import binascii
from Crypto.Cipher import AES
from django.db import transaction
#===============================================================================
# Stores server and client Cloud image in the db
# AWS - Server image
# OpenStack Server image
# CitizenGrid Server image - TODO - pending discussion
# Params:
#    type - Refers Client or Server type
#    app - Application which has cloud server image
#    apphost - EC2/Openstack
#    id - Image ID -
#    location - Endpoint url
#===============================================================================
def store_cloud_details(app,type,apphost,id,location):
    print "Details %s %s " %(apphost,type)
    if apphost =='Public':
        new_image = ApplicationEC2Images(application = app,
                                         image_id = id,
                                         zone_name = '',
                                         zone_url = location,
                                         image_type=type)
        print "Going to save EC2 %s image %s" %(type,str(new_image))
        new_image.save()
    elif apphost =='Private':
        #Store Openstack details
        new_image = ApplicationOpenstackImages(application=app,
                                           image_id=id,
                                           zone_name='',
                                           zone_url=location,
                                           image_type=type)
        print "Going to save Openstack %s image %s" %(type,str(new_image))
        new_image.save()
    else:
        pass

#===============================================================================
# Stores local image (file) for Server and Client applications
#===============================================================================
def store_local_image(requestmap):
    pass

#===============================================================================
#     Deletes from citizenapplicationfile
#     TODO - abstract html snippet into a template
#===============================================================================
def delete_file(request,id):
    print "Going to delete Application file with id %d" %(id)
    file = ApplicationFile.objects.filter(id=id,owner=request.user)
    application_id = file.values()[0]['application_id']
    file.delete()
    print "Deleted  Application file: %s" %(str(file))
    
    appfile = ApplicationFile.objects.filter(owner=request.user,application_id=application_id).values()
    data = ''
    if len(appfile) != 0:
        file_format = cg_template_filters.getfileformat(str(appfile[0]['file_format']))
        fileurl = cg_template_filters.getfileurl(str(appfile[0]['file']),request.user.username)
        filebasename = cg_template_filters.getfilebasename(str(appfile[0]['file']))
        data = """ <div class="row">
            <div class="local col-md-4 pull-left">""" + file_format + ": <a href='" + fileurl +"'>" + filebasename + """</a></div>
             <div class="local col-md-1 pull-right"> <a title="delete image" class="" type="file" id='""" + str(appfile[0]['id'])+ """' href="#"><i class="icon-trash icon-white"></i></a> </div>
        </div>"""
    else:
        pass
    return data
    
#===============================================================================
#     Deletes from citizengrid applicationfile
#===============================================================================
def delete_cloud(request,type,id):
    print "Going to delete with type %s" %(type)
    if type == 'ec2':
        ecimage = ApplicationEC2Images.objects.filter(image_id=str(id))
        application_id = ecimage.values()[0]['application_id']
        ecimage.delete()
        # select rest OS and EC2 images
        ec_images = ApplicationEC2Images.objects.filter(id=str(application_id))
        os_images = ApplicationOpenstackImages.objects.filter(application_id=str(application_id))
        return render_to_string('cg_cloud_div_template.html', { 'ec2_images': ec_images,'openstack_images':os_images })
    elif type =='os':
        osimage = ApplicationOpenstackImages.objects.filter(image_id=str(id))
        application_id = osimage.values()[0]['application_id']
        # Delete images
        osimage.delete()
        # select rest OS and EC2 images
        os_images = ApplicationOpenstackImages.objects.filter(application_id=str(application_id))
        ec_images = ApplicationEC2Images.objects.filter(application_id=str(application_id))
        return render_to_string('cg_cloud_div_template.html', { 'ec2_images': ec_images,'openstack_images':os_images })
    elif type=='app':
        #delete the app with id
        delete_application(request,id)
        #render the data
        #tag= cg_myapp_template.myapp_render(request)
        #data =
        (branches,category,subcategory,form,apps,formErrorVal, file_info_dict, os_images, ec2_images,role) = application_provider_view_data(request)
        return render_to_string('cg_myapp_template.html',{'branches':branches,'category':category,'subcategory':subcategory,'form':form,'apps':apps,
                               'hasFormError': formErrorVal, 'file_info': file_info_dict, 'os_images':os_images,
                               'ec2_images': ec2_images,'role':role})
        #cg_myapp_template.myapp_render(request)
        #return render_to_string('cg_myapp_template.html')
    else:
        pass  
    
        #===============================================================================
        # Delete credentials routine
        # param :
        #    type - AWS|Openstack|Cloud
        #    id - Access Key
        #    request - request map data
        #===============================================================================
def delete_cred(request,type,id):
    print "Inside delete_creds data routine"
    os_creds = []
    PADDING = '{'
    #cg_manage_cred_openstack.html
    if type =='oscred':
        #dlete openstack credentials
        db_creds = UserCloudCredentials.objects.filter(user=request.user,id=int(id))
        db_creds.delete()
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
            os_creds.append(new_cred) 
        return render_to_string('ajaxdivtemplate/cg_manage_cred_openstack.html', {'cloud_creds':os_creds,})
            #return render_to_response('cg_manage_credentials.html', {'next':'/', 'cloud_creds':cloud_creds,'role':role}, context_instance=RequestContext(request))
    else:
        pass


def delete_application(request,id):
    print "Deleting application by id %d" %(id)
    with transaction.atomic():
        ApplicationFile.objects.filter( application=id).delete()
        ApplicationEC2Images.objects.filter( application=id).delete()
        ApplicationOpenstackImages.objects.filter(application=id).delete()
        ApplicationBasicInfo.objects.filter(id=id).delete()
    return "Object Deleted"




def return_role(request):
        if str(request.user) != 'AnonymousUser':
                user_info_list = UserInfo.objects.filter(user=request.user)
                print "role is :" + user_info_list[0].user_primary_role_desc
                role = user_info_list[0].user_primary_role_desc
        else:
                role = "None"

        return role

def application_user_view_data(request):
        print "Inside application provider view data"
        apps = ApplicationBasicInfo.objects.filter(public=True)
        
        myapps = ApplicationBasicInfo.objects.filter(usersapplications__user=request.user)
 
        # Get the list of app ids that we're going to look up application files for.
        app_ids = []
        for app in apps:
            app_ids.append(app.id)
        print 'Looking up file for apps: ' + str(app_ids)
        files = ApplicationFile.objects.filter(file_type='S',image_type='C', application__in=app_ids)


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
    ## Current role appended  in session
        user_info_list = UserInfo.objects.filter(user=request.user)
        role = user_info_list[0].user_primary_role_desc
        request.session['role'] = role
        return (apps,file_info_dict,role,myapps)


def application_provider_view_data(request):
    formErrorVal = False

    if request.method == 'POST':
        # If we've not come from the welcome page then we can
        # look for a valid form to parse, otherwise there's no point.
        if 'cancelWelcome' not in request.POST:
            # We've received a standard post from the CG page and there
            # may be an application form and request to register an app
            form = ApplicationBasicInfoForm(request.POST, request=request)

            if form.is_valid():
                name = form.cleaned_data['name']
                desc = form.cleaned_data['description']
                image_id = form.cleaned_data['image_id']
                image_location = form.cleaned_data['image_location']
                public = form.cleaned_data['public']
                additional_information = form.cleaned_data['additional_Information']

                print "APP REGISTRATION FORM VALID:"
                print "\tName: " + name
                print "\tDescription: " + desc
                print "\tImage ID: " + image_id
                print "\tImage location: " + str(image_location)
                print "\tPublic: " + str(public)
                print "\tAdditionalInformation: " + str(additional_information)

                # Now create the application model and store it
                app = ApplicationBasicInfo(owner=request.user, name=name,
                                  description=desc, client_downloads=0,
                                  image_id=image_id, image_location=str(image_location), public=public)
                app.save()

                print 'Created new application with new ID: ' + str(app.id)

                # Now that the model is stored, we switch the associated
                # files to stored status and set the owning application to
                # the one that's just been created.
                tempfiles = ApplicationFile.objects.filter(file_type='T', owner_id=request.user)
                for tempfile in tempfiles:
                    tempfile.file_type='S'
                    tempfile.application = app
                    tempfile.save()

                # Generate the identicon for the application
                fs = FileSystemStorage()
                icon_location = os.path.join(fs.location, '..', 'static', 'img', 'ident', str(app.id)+'.png')
                print "Debug: IconLocation is %s" %(icon_location)
                gen_icon.create_icon(icon_location)

                app.iconfile = os.path.join('img', 'ident', str(app.id)+'.png')
                app.save()

            else:
                print "APP REGISTRATION FORM IS NOT VALID..."
                active_tab = 'NA'
                form = ApplicationBasicInfoForm()
                formErrorVal = True

        else:
            form = ApplicationBasicInfoForm()

    else:
        form = ApplicationBasicInfoForm()


    # Populate the application list
    apps = ApplicationBasicInfo.objects.filter(owner=request.user)
    # Get the list of app ids that we're going to look up application files for.
    app_ids = []
    for app in apps:
        app_ids.append(app.id) #Appending the all app id in the app_id list
    print 'Looking up file for apps: ' + str(app_ids)
    files = ApplicationFile.objects.filter(owner_id=request.user, file_type='S', application__in=app_ids) #__in django filter list

    os_images = ApplicationOpenstackImages.objects.filter(application__in=app_ids)
    ec2_images = ApplicationEC2Images.objects.filter(application__in=app_ids)

    # We now have a list of files for all the applications of the request.user.
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
        # FIXME: Need a more foolproof way to get the file path for the link
        file_info['path'] = os.path.join('media', request.user.username, appfile.filename())
        print appfile.file_format
        file_info['formatstring'] = file_formats[appfile.file_format]
        file_info['image_type'] = appfile.image_type
        file_info_dict[appfile.application.id].append(file_info)
## Current role appended  in session
    user_info_list = UserInfo.objects.filter(user=request.user)
    role = user_info_list[0].user_primary_role_desc
    branches = Branch.objects.all()
    category = Category.objects.all()
    subcategory = SubCategory.objects.all()

    return  (branches,category,subcategory,form,apps,formErrorVal, file_info_dict, os_images, ec2_images,role)
