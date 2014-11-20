"""
This file contains un-secured views functions which are publically accessible and doesn't require user login.
"""

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.core import serializers
from django.template.defaulttags import csrf_token
from django.db.models import Q
import json

from citizengrid.forms import ExtendedUserCreationForm
from citizengrid.models import UserInfo,Branch,Category,SubCategory,ApplicationBasicInfo

import citizengrid.view_utils as view_utils


def home(request):
    # View code here...
    print "CitizenGrid Home requested..."
    if str(request.user) != 'AnonymousUser':
        user_info_list = UserInfo.objects.filter(user=request.user)
        print "user is %s" %(str(request.user))
        print "role is :" + user_info_list[0].user_primary_role_desc
        role = user_info_list[0].user_primary_role_desc
    else:
        role = "None"
    return render_to_response('index.html', {'next':'/','role':role}, context_instance=RequestContext(request))


def about(request):
    # Code for contact us...
    print "Contact us requested here..."
    role = view_utils.return_role(request)
    if role is not None:
        return render_to_response('aboutus.html', {'next':'/','role':role}, context_instance=RequestContext(request))
    else:
        return render_to_response('aboutus.html', {'next':'/'}, context_instance=RequestContext(request))


def contact(request):
    # Code for contact us...
    print "Contact us requested here..."
    role = view_utils.return_role(request)
    if role is not None:
        return render_to_response('contactus.html', {'next':'/','role':role}, context_instance=RequestContext(request))
    else:
        return render_to_response('contactus.html', {'next':'/'}, context_instance=RequestContext(request))


def userdoc(request):
    # User Documentation
    print "userdoc requested here..."
    return render_to_response('userdoc.html', {'next':'/'}, context_instance=RequestContext(request))


def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        action = "registration"
        if form.is_valid():
            new_user = form.create()
            return render_to_response('registration/confirm.html', {'action': action}, context_instance=RequestContext(request))
    else:
        form = ExtendedUserCreationForm()

    return render_to_response('registration/register.html', {'form': form}, context_instance=RequestContext(request))

def register_confirmation(request):
    print "CitizenGrid Home requested..."
    return render_to_response('registration/confirm.html', {'next':'/'}, context_instance=RequestContext(request))


def all_json_category(request,branch):
    current_branch = Branch.objects.get(id=branch)
    category = Category.objects.all().filter(branch_id=current_branch)
    json_category = serializers.serialize("json", category)
    return HttpResponse(json_category, content_type="application/javascript")

def all_json_subcategory(request,category):
    current_subcategory = Category.objects.get(id=category)
    subcategory = SubCategory.objects.all().filter(category_id=current_subcategory)
    json_subcategory = serializers.serialize("json", subcategory)
    return HttpResponse(json_subcategory, content_type="application/javascript")

