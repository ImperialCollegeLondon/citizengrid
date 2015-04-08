from django.conf.urls import patterns, include, url
from citizengrid import cg_api_views
import os
from . import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
router = cg_api_views.HybridRouter()
# Only admin can see this view
router.register(r'users', cg_api_views.UserViewSet)
router.register(r'groups', cg_api_views.GroupViewSet)  # All registered users
router.add_api_view("apps",
                    url(r'^apps/$',
                        cg_api_views.ApplicationListPublicView.as_view(),
                        name='ApplicationListPublicView'))
router.add_api_view("myapps",
                    url(r'^myapps/$',
                        cg_api_views.MyApplicationListView.as_view(),
                        name='MyApplicationListView'))
router.add_api_view("branches",
                    url(r'^branches/$',
                        cg_api_views.BranchListView.as_view(),
                        name='BranchListView'))
router.add_api_view("categories",
                    url(r'^categories/$',
                        cg_api_views.CategoryListView.as_view(),
                        name='CategoryListView'))
router.add_api_view("subcategories",
                    url(r'^subcategories/$',
                        cg_api_views.SubCategoryListView.as_view(),
                        name='SubCategoryListView'))
router.add_api_view("usercredentials",
                    url(r'^usercredentials/$',
                        cg_api_views.UserCloudCredentialsListView.as_view(),
                        name='UserCloudCredentialsListView'))

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', 'citizengrid.views.home', name='home'),
                       url(r'^about', 'citizengrid.views.about', name='about'),
                       url(r'^contact',
                           'citizengrid.views.contact',
                           name='contact'),
                       url(r'^doc',
                           'citizengrid.views.userdoc',
                           name='userdoc'),
                       url(r'^media/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT}),
                       url(r'^static/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': settings.STATIC_ROOT}),
                       url(r'^cg$',
                           'citizengrid.secure_views.cg',
                           name='cg_home'),
                       url(r'^js/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': os.path.join(settings.STATIC_ROOT,
                                                          'js')}),
                       url(r'^css/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': os.path.join(settings.STATIC_ROOT,
                                                          'css')}),
                       url(r'^img/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': os.path.join(settings.STATIC_ROOT,
                                                          'img')}),
                       url(r'^media/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT}),
                       url(r'^font/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': os.path.join(settings.STATIC_ROOT,
                                                          'fonts')}),
                       url(r'^fonts/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': os.path.join(settings.STATIC_ROOT,
                                                          'fonts')}),
                       url(r'^cg/upload$',
                           'citizengrid.secure_views.upload',
                           name='jfu_upload'),
                       url(r'^cg/delupload/(?P<uploadid>\d+)$',
                           'citizengrid.secure_views.delupload',
                           name='del_file'),
                       url(r'^cg/launchapp/(?P<appid>\d+)/(?P<launchtype>\w+)/(?P<apptag>.*)$',
                           'citizengrid.launch_views.launchapp',
                           name='launch_app'),
                       url(r'^cg/launchserver/(?P<appid>\d+)/(?P<launchtype>\w*)$',
                           'citizengrid.launch_views.launchserver',
                           name='launch_server'),
                       url(
                           r'^cg/manage/instances/(?P<task>\w+)/(?P<appid>\w*)/(?P<instancerecord>[-\w]*)$',
                           'citizengrid.launch_views.manage_instances',
                           name='manage_instances'),
                       url(r'^cg/manage/cred$',
                           'citizengrid.secure_views.manage_credentials',
                           name='manage_credentials'),
                       url(r'^cg/manage/group/applist$',
                           'citizengrid.secure_views.application_list',
                           name='application_list'),
                       url(r'^cg/manage/group$',
                           'citizengrid.secure_views.manage_groups',
                           name='manage_groups'),
                       url(r'^cg/manage/group/edit/(?P<id>\d+)$',
                           'citizengrid.secure_views.edit_group',
                           name='edit_group'),
                       url(r'^cg/manage/group/create/$',
                           'citizengrid.secure_views.add_group',
                           name='add_group'),
                       url(r'^cg/manage/groups/$',
                           'citizengrid.secure_views.groups',
                           name='add_group'),
                       url(r'^cg/manage/group/delete/(?P<id>\d+)$',
                           'citizengrid.secure_views.delete_group',
                           name='delete_group'),
                       url(r'^cg/manage/group/detail/(?P<id>\d+)$',
                           'citizengrid.secure_views.detail_group',
                           name='delete_group'),
                       url(r'^cg/manage/group/leave/(?P<id>\d+)$',
                           'citizengrid.secure_views.leave_group',
                           name='leave_group'),
                       url(r'^cg/manage/group/join/$',
                           'citizengrid.secure_views.join_group',
                           name='join_group'),
                       url(r'^cg/manage/group/attachapptogrp/(?P<id>\d+)$',
                           'citizengrid.secure_views.attach_app_to_group',
                           name='attach_app_to_group'),
                       url(r'^cg/manage/group/detachfromgroup/(?P<id>\d+)$',
                           'citizengrid.secure_views.detach_app_from_group',
                           name='detach_app_from_group'),
                       url(r'^cg/manage/group/applicationgrouptagdetail/$',
                           'citizengrid.secure_views.application_grp_tag_detail',
                           name='application_grp_tag_detail'),
                       url(r'^cg/manage/applicationgrouptag/(?P<id>\d+)$',
                           'citizengrid.secure_views.application_grp_tag',
                           name='application_grp_tag'),
                       url(r'^cg/manage/updateaccount$',
                           'citizengrid.secure_views.update_user_account',
                           name='update_user_account'),
                       url(r'^cg/manage/cred/cloud$',
                           'citizengrid.secure_views.add_update_credentials',
                           name='add_update_credentials'),
                       url(r'^cg/manage/images/(?P<app>\w+)$',
                           'citizengrid.secure_views.manage_images',
                           name='manage_images'),
                       url(r'^cg/info/servers$',
                           'citizengrid.secure_views.get_running_servers',
                           name='get_running_servers'),
                       url(r'^cg/info/cloudcredentials$',
                           'citizengrid.secure_views.get_cloud_credentials',
                           name='get_cloud_credentials'),
                       url(r'^accounts/login/$',
                           'django.contrib.auth.views.login'),
                       url(r'^accounts/logout/$',
                           'django.contrib.auth.views.logout'),
                       url(r'^accounts/register/$',
                           'citizengrid.views.register'),
                       url(r'^accounts/confirmation/$',
                           'citizengrid.views.register_confirmation'),
                       url(r'^accounts/', include('password_reset.urls')),
                       url(r'^gettabledata/$',
                           'citizengrid.secure_views.getTableData'),
                       url(r'^getuserapps/$',
                           'citizengrid.secure_views.getUserApps'),
                       url(r'^cg/appdetail/(?P<appid>\w+)$',
                           'citizengrid.secure_views.application_detail'),
                       url(r'^cg/myappdetail/(?P<appid>\w+)$',
                           'citizengrid.secure_views.my_application'),
                       url(r'^cg/delete/(?P<id>[\w-]+)$',
                           'citizengrid.secure_views.cg_delete'),
                       (r'^branch/(?P<branch>\d+)/all_json_category/$',
                        'citizengrid.views.all_json_category'),
                       (r'^category/(?P<category>\d+)/all_json_subcategory/$',
                        'citizengrid.views.all_json_subcategory'),
                       url(r'^cg/app/wizard$',
                           'citizengrid.secure_views.wrapped_wizard_view',
                           name='wrapped_wizard_view'),
                       # url(r'^api/citizengrid/apps/(?P<appid>\d+)/$',
                       #     cg_api_views.ApplicationDetailListView.as_view(),
                       #     name='ApplicationDetailListView'),
                       url(r'^api/citizengrid/myapps/(?P<appid>\d+)/$',
                           cg_api_views.MyApplicationDetailListView.as_view(),
                           name='MyApplicationDetailListView'),

                       # start the application locally
                       url(r'^api/citizengrid/apps/(?P<appid>\d+)/startapp/$',
                           'citizengrid.cg_api_views.startapp_locally',
                           name='start'),

                       url(r'^api/citizengrid/apps/(?P<appid>\d+)/files/$',
                           cg_api_views.ApplicationFileList.as_view(),
                           name='ApplicationFileList'),

                       url(
                           r'^api/citizengrid/apps/(?P<appid>\d+)/files/(?P<fileid>\d+)/$',
                           cg_api_views.ApplicationFileDetail.as_view(),
                           name='ApplicationFileDetail'),
                       # OSImagesList
                       url(r'^api/citizengrid/apps/(?P<appid>\d+)/osimages/$',
                           cg_api_views.ApplicationOpenstackImagesList.as_view(),
                           name='ApplicationOpenstackImagesList'),

                       # OsImage Detail url
                       url(
                           r'^api/citizengrid/apps/(?P<appid>\d+)/osimages/(?P<fileid>\d+)/$',
                           cg_api_views.ApplicationOpenstackImageDetail.as_view(),
                           name='ApplicationOpenstackImageDetail'),

                       # EC2ImagesList
                       url(r'^api/citizengrid/apps/(?P<appid>\d+)/ec2images/$',
                           cg_api_views.ApplicationEc2ImagesList.as_view(),
                           name='ApplicationEc2ImagesList'),

                       # EC2Image Detail url
                       url(
                           r'^api/citizengrid/apps/(?P<appid>\d+)/ec2images/(?P<fileid>\d+)/$',
                           cg_api_views.ApplicationEc2ImageDetail.as_view(),
                           name='ApplicationEc2ImageDetail'),

                       # start EC2 app on cloud
                       url(
                           r'^api/citizengrid/apps/(?P<appid>\d+)/ec2images/(?P<fileid>\d+)/startserver/$',
                           cg_api_views.start_Ec2server,
                           name='start_Ec2server'),

                       # start OpenStack app on cloud
                       url(
                           r'^api/citizengrid/apps/(?P<appid>\d+)/osimages/(?P<fileid>\d+)/startserver/$',
                           cg_api_views.start_OpenstackServer,
                           name='start_OpenstackServer'),

                       # Credentials list
                       url(r'^api/citizengrid/usercredentials/(?P<credid>\d+)/$',
                           cg_api_views.UserCloudCredentialsDetailView.as_view(),
                           name='UserCloudCredentialsDetailView'),

                       # Openstack Instances
                       url(r'^api/citizengrid/apps/(?P<appid>\d+)/osinstances/$',
                           cg_api_views.CloudInstancesList.as_view(),
                           name='CloudInstancesList'),

                       url(
                           r'^api/citizengrid/apps/(?P<appid>\d+)/osinstances/(?P<instanceid>([a-zA-Z])-([0-9a-zA-Z])+)/$',
                           cg_api_views.CloudInstancesDetail.as_view(),
                           name='CloudInstancesDetail'),

                       # AWS Instances
                       url(r'^api/citizengrid/apps/(?P<appid>\d+)/awsinstances/$',
                           cg_api_views.AWSCloudInstancesList.as_view(),
                           name='AWSCloudInstancesList'),

                       url(
                           r'^api/citizengrid/apps/(?P<appid>\d+)/awsinstances/(?P<instanceid>([a-zA-Z])-([0-9a-zA-Z])+)/$',
                           cg_api_views.AWSCloudInstancesDetail.as_view(),
                           name='AWSCloudInstancesDetail'),

                       # stop instance
                       url(
                           r'^api/citizengrid/apps/(?P<appid>\d+)/instances/(?P<instanceid>([a-zA-Z])-([0-9a-zA-Z])+)/stop$',
                           cg_api_views.stopinstance,
                           name='stopinstance'),

                       # Group web api urls

                       # List all groups
                       url(r'^api/citizengrid/manage/group$',
                           cg_api_views.MyGroupList.as_view(),
                           name='MyGroupList'),

                       url(r'^api/citizengrid/manage/group/(?P<pk>\d+)$',
                           cg_api_views.MyGroupDetailView.as_view(),
                           name='MyGroupDetailView'),

                       url(r'^api/citizengrid/manage/group/(?P<groupid>\d+)/leave$',
                           cg_api_views.leave_group,
                           name='leave_group'),

                       url(r'^api/citizengrid/manage/group/join',
                           cg_api_views.join_group,
                           name='join_group'),

                       url(r'^api/citizengrid/manage/group/(?P<groupid>\d+)/attachapp$',
                           cg_api_views.GroupApplicationTagView.as_view(),
                           name='GroupApplicationTagView'),

                       url(r'^api/citizengrid/manage/group/(?P<groupid>\d+)/detachapp/(?P<id>\d+)$',
                           cg_api_views.GroupApplicationTagDetailView.as_view(),
                           name='GroupApplicationTagDetailView'),

                       url(r'^api/citizengrid/', include(router.urls)),

                       url(r'^api-auth/citizengrid/',
                           include('rest_framework.urls',
                                   namespace='rest_framework')),

                       # admin
                       url(r'^admin/', include(admin.site.urls)),
                       )
