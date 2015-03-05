from django.template.defaultfilters import register
from django import template

import os

from citizengrid.models import ApplicationFile, ApplicationBasicInfo, ApplicationEC2Images, ApplicationOpenstackImages
from django.template.loader import render_to_string

register = template.Library()

@register.inclusion_tag("cg_myapp_template.html")
def myapp_render(request):
    print "Coming inside this applicaiton"
    # Populate the application list
    apps = ApplicationBasicInfo.objects.filter(owner=request.user)
    print "apps is isn't crayz %s" %(str(apps))
    # Get the list of app ids that we're going to look up application files for.
    app_ids = []
    for app in apps:
        app_ids.append(app.id)
    print 'Looking up file for apps: ' + str(app_ids)
    files = ApplicationFile.objects.filter(owner_id=request.user, file_type='S', application__in=app_ids)

    os_images = ApplicationOpenstackImages.objects.filter(application__in=app_ids)
    ec2_images = ApplicationEC2Images.objects.filter(application__in=app_ids)
    
    # We now have a list of files for all the applications.
    # For each application, prepare a new list. Each item in the list
    # will be a dict containing the details about a file for an application.
    # This list will then be added to the file_info_dict with the key
    # as the app id.
    file_info_dict = {}

    file_formats = { 'NONE': 'Local file (Unknown type)',
                   'RAW' : 'Local image (RAW)',
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
        file_info['formatstring'] = file_formats[appfile.file_format]
        file_info['image_type'] = appfile.image_type
        file_info_dict[appfile.application.id].append(file_info)
        tag = {'apps':apps, 'file_info': file_info_dict, 'os_images':os_images, 'ec2_images': ec2_images}
    return tag
#render_to_string('cg_myapp_template.html',{'apps':apps, 'file_info': file_info_dict, 'os_images':os_images, 'ec2_images': ec2_images})