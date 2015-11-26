'''
Created on 23 Nov 2015

@author: jhc02

URL dispatcher configuration for the cg_webapi app
'''
import os
from django.conf.urls import url
from django.conf import settings

from cg_webapi import views

urlpatterns = [
    url(r'^vmcp/(?P<vmcp_id>.*)$', views.cg_webapi_vmcp),
    url(r'^launch/$', views.cg_webapi_launch),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(settings.WEBAPI_STATIC_ROOT,'js')}),
]
