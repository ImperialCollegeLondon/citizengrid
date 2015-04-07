import json
import base64
from Crypto.Cipher import AES
import bz2
from django.contrib.auth.models import User, Group
from django.http.response import HttpResponse
from rest_framework.renderers import JSONRenderer
from citizengrid import launch_views, DATA_K
from citizengrid.models import UserInfo, ApplicationBasicInfo, ApplicationFile, ApplicationServerInfo, \
    ApplicationClientInfo, Branch, Category, SubCategory, \
    UserCloudCredentials, ApplicationOpenstackImages, ApplicationEC2Images, CloudInstancesOpenstack, GroupApplicationTag
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action, link
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from citizengrid.serializers import UserSerializer, PasswordSerializer, GroupSerializer, ApplicationsSerializer, \
    ApplicationFileSerializer, ApplicationOsImagesSerializer, ApplicationEc2Serializer, BranchSerializer, \
    CategorySerializer, SubCategorySerializer, \
    ApplicationFileDetailSerializer, UserCloudCredentialsSerializer, CloudInstancesSerializer, MyApplicationSerializer, MyGroupSerializer,GroupApplicationTagSerializer
from rest_framework import routers, views, reverse, response
from django.views.decorators.csrf import *
from django.db import transaction, IntegrityError
from citizengrid.view_utils import delete_application
from citizengrid.models import MyGroup
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

"""
Responsible for web-api and associated features of CitizenGrid.
"""


class HybridRouter(routers.DefaultRouter):
    """ HybridRouter for browse-able RestFul API
    """
    def __init__(self, *args, **kwargs):
        super(HybridRouter, self).__init__(*args, **kwargs)
        self._api_view_urls = {}

    def add_api_view(self, name, url):
        self._api_view_urls[name] = url

    def remove_api_view(self, name):
        del self._api_view_urls[name]

    @property
    def api_view_urls(self):
        ret = {}
        ret.update(self._api_view_urls)
        return ret

    def get_urls(self):
        urls = super(HybridRouter, self).get_urls()
        for api_view_key in self._api_view_urls.keys():
            urls.append(self._api_view_urls[api_view_key])
        return urls


    def get_api_root_view(self):
        # Copy the following block from Default Router
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        api_view_urls = self._api_view_urls

        class APIRoot(views.APIView):
            _ignore_model_permissions = True

            def get(self, request, format=None):
                ret = {}
                for key, url_name in api_root_dict.items():
                    ret[key] = reverse.reverse(url_name, request=request, format=format)
                # In addition to what had been added, now add the APIView urls
                for api_view_key in api_view_urls.keys():
                    print api_view_urls[api_view_key].name
                    print api_view_urls[api_view_key].regex
                    if api_view_urls[api_view_key].name == 'ApplicationDetailListView':
                        ret[api_view_key] = reverse.reverse(api_view_urls[api_view_key].name, args=[20],
                                                            request=request, format=format)
                    else:
                        ret[api_view_key] = reverse.reverse(api_view_urls[api_view_key].name, request=request,
                                                            format=format)
                return response.Response(ret)

        return APIRoot.as_view()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows api-users to
    1. list all users
    2. retrieve detailed view of a single user identified by id.
    3. re-set password
    4. set password
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(permission_classes=[IsAdminUser])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.DATA)
        if serializer.is_valid():
            user.set_password(serializer.data['password'])
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors,
                            status=400)

    @action(methods=['POST', 'DELETE'])
    def unset_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=None)
        if serializer.is_valid():
            user.set_password(serializer.data['password'])
            user.save()
            return Response({'status': 'password reset'})
        else:
            return Response(serializer.errors,
                            status=400)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
     """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ApplicationFileList(generics.ListAPIView):
    """
     API Endpoint for listing applicationFile objects linked to an application
     """
    serializer_class = ApplicationFileSerializer
    permission_classes = ( IsAuthenticated,)


    def get_queryset(self):
        user = self.request.user
        appid = self.kwargs.get('appid')
        # self.request.QUERY_PARAMS.get('appid', None)
        print self.kwargs.get('appid')
        print 'appid is %s ' % (appid)
        #if appid is not None:
        #queryset = ApplicationFile.objects.all()
        queryset = ApplicationFile.objects.filter(application=appid)
        return queryset


class ApplicationFileDetail(generics.ListAPIView, generics.RetrieveDestroyAPIView):
    """
     API Endpoint for
     1. querying details of an applicationFile objects linked to an application and
        identified by an id.
     2. deleting an applicationFile identified by an application file id.
     """
    serializer_class = ApplicationFileDetailSerializer
    permission_classes = ( IsAuthenticated,)


    def get_queryset(self):
        user = self.request.user
        appid = self.kwargs['appid']
        fileid = self.kwargs['fileid']

        # self.request.QUERY_PARAMS.get('appid', None)
        if appid is None:
            queryset = ApplicationFile.objects.all()
        else:
            print appid, fileid
            queryset = ApplicationFile.objects.filter(application=appid, id=fileid)
        return queryset

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        appid = self.kwargs['appid']
        fileid = self.kwargs['fileid']
        # delete file corresponding to fileid

        try:
            print ApplicationFile.objects.filter(application=appid, id=fileid)
            return HttpResponse(status=204)

            # return HttpResponse("Image with id %s deleted" %(fileid) )
        except:
            HttpResponse(status=204)


class ApplicationOpenstackImagesList(generics.ListCreateAPIView):
    """
    Implementation for Endpoint responsible for
    1.listing Openstack Images
    2. Creating Openstack imagess
    """
    serializer_class = ApplicationOsImagesSerializer
    permission_classes = ( IsAuthenticated,)


    def get_queryset(self):
        user = self.request.user
        appid = self.kwargs['appid']
        # self.kwargs['appid']
        if appid is None:
            queryset = ApplicationOpenstackImages.objects.all()
        else:
            queryset = ApplicationOpenstackImages.objects.filter(application=appid)

        return queryset


    def create(self, request, *args, **kwargs):
        print "Creating OpenStack images"
        data = request.DATA
        with transaction.atomic():
            # add credentials api
            app = ApplicationBasicInfo.objects.filter(id=int(data.get('application')))[0]
            print app
            new_image = ApplicationOpenstackImages(application=app,
                                                   image_id=str(data.get('image_id')),
                                                   zone_name=str(data.get('zone_name')),
                                                   zone_url=str(data.get('zone_url')),
                                                   image_type=str(data.get('image_type')))
            new_image.save()

        serializer = ApplicationOsImagesSerializer(data)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class ApplicationEc2ImagesList(generics.ListCreateAPIView):
    """
    API endpoint that allows
    1. List all EC2 image list
    2. Create an EC2 image registration
    """
    serializer_class = ApplicationEc2Serializer
    permission_classes = ( IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        appid = self.kwargs.get('appid')
        if appid is None:
            queryset = ApplicationEC2Images.objects.all()
        else:
            queryset = ApplicationEC2Images.objects.filter(application=appid)
        return queryset


    def create(self, request, *args, **kwargs):
        print "Creating EC2 images"
        data = request.DATA
        with transaction.atomic():
            # add credentials api
            app = ApplicationBasicInfo.objects.filter(id=int(data.get('application')))[0]
            print app
            new_image = ApplicationEC2Images(application=app,
                                             image_id=str(data.get('image_id')),
                                             zone_name=str(data.get('zone_name')),
                                             zone_url=str(data.get('zone_url')),
                                             image_type=str(data.get('image_type')))
            new_image.save()

        serializer = ApplicationEc2Serializer(data)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class ApplicationEc2ImageDetail(generics.ListAPIView, generics.RetrieveDestroyAPIView):
    """
    API endpoint that allows
    1. List detail of an  EC2 image list
    2. Delete an EC2 image
    """
    serializer_class = ApplicationEc2Serializer
    permission_classes = ( IsAuthenticated,)


    def get_queryset(self):
        user = self.request.user
        appid = self.kwargs['appid']
        fileid = self.kwargs['fileid']

        # self.request.QUERY_PARAMS.get('appid', None)
        if appid is None:
            queryset = ApplicationEC2Images.objects.all()
        else:
            print appid, fileid
            queryset = ApplicationEC2Images.objects.filter(application=appid, id=fileid)
        return queryset

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        appid = self.kwargs['appid']
        fileid = self.kwargs['fileid']

        # delete file corresponding to fileid

        try:
            # ApplicationFile.objects.filter(application=appid,id=fileid).delete()
            ApplicationEC2Images.objects.filter(application=appid, id=fileid).delete()
            return HttpResponse("Image with id %s deleted" % (fileid))
        except:
            HttpResponse(status=204)


class ApplicationOpenstackImageDetail(generics.ListAPIView, generics.RetrieveDestroyAPIView):
    """
    API endpoint that allows
    1. List detail of an  OpenStack image list
    2. Delete an OpenStack image
    """
    serializer_class = ApplicationOsImagesSerializer
    permission_classes = ( IsAuthenticated,)


    def get_queryset(self):
        user = self.request.user
        appid = self.kwargs['appid']
        fileid = self.kwargs['fileid']

        # self.request.QUERY_PARAMS.get('appid', None)
        if appid is None:
            queryset = ApplicationOpenstackImages.objects.all()
        else:
            print appid, fileid
            queryset = ApplicationOpenstackImages.objects.filter(application=appid, id=fileid)
        return queryset

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        appid = self.kwargs['appid']
        fileid = self.kwargs['fileid']

        # delete file corresponding to fileid

        try:
            # ApplicationFile.objects.filter(application=appid,id=fileid).delete()
            ApplicationOpenstackImages.objects.filter(application=appid, id=fileid).delete()
            return HttpResponse("Image with id %s deleted" % (fileid))
        except:
            HttpResponse(status=204)


class ApplicationListViewByOwnerId(generics.ListAPIView):
    """
    API endpoint that allows
    1. List application by Owner_ID
    """
    serializer_class = ApplicationsSerializer
    permission_classes = ( IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = ApplicationBasicInfo.objects.filter(public=True)
        owner = self.request.QUERY_PARAMS.get('owner', None)
        if owner is not None:
            queryset = queryset.filter(owner=owner)
        # serializer = ApplicationsSerializer(queryset)
        return queryset


class ApplicationListPublicView(generics.ListAPIView):
    """
    API endpoint that list all public applications
    """
    serializer_class = ApplicationsSerializer
    permission_classes = ( IsAuthenticated,)
    allow_empty = False;

    # filter_fields = ('url','id','owner','name',)

    def get_queryset(self):
        user = self.request.user
        queryset = ApplicationBasicInfo.objects.filter(public=True)
        # serializer = ApplicationsSerializer(queryset)
        return queryset


# RetrieveUpdateDestroyAPIView
class ApplicationDetailListView(generics.ListAPIView):
    """
    API endpoint that
    1. Detail view of an application identified by an application-id
    2. Deletes an application identified by an application-id
    """
    serializer_class = ApplicationsSerializer
    permission_classes = ( IsAuthenticated,)
    allow_empty = False;

    # filter_fields = ('url','id','owner','name',)

    def get_queryset(self):
        print "Inside get"
        user = self.request.user
        queryset = ApplicationBasicInfo.objects.filter(public=True, id=self.kwargs['appid'])

        #serializer = ApplicationsSerializer(queryset)
        return queryset

    def delete(self, request, *args, **kwargs):
        print "Inside delete with id as %s" % (self.kwargs['appid'])
        #Only Owner or admin  can delete application
        try:
            id = str(self.kwargs['appid'])
            delete_application(request, int(id))
            return HttpResponse("Application with id as %s is deleted" % (self.kwargs['appid']), status=200)
        except Exception as e:
            print "%s " % (e.message)
            return HttpResponse(status=404)

    def options(self, request, *args, **kwargs):
        pass

    @link()
    def start(self):
        print "In started"
        return HttpResponse("Started application with id %s" % (self.kwargs['appid']))


@login_required()
@csrf_protect
def start(request, appid):

    """
    API to start an application with defined launchtype and identified by the application-id
    """
    print "In started"
    launchtype = request.GET.get("launchtype", None)
    if launchtype is not None:
        launch_views.launchapp(request, appid, launchtype)
        return HttpResponse("started Application", status=202)
    else:
        return HttpResponse("Cannot start application", status=400)


class MyApplicationListView(generics.ListCreateAPIView):
    """
    API endpoint that
    1. List all applications for an owner
    2. Create a vanilla application
    """
    serializer_class = MyApplicationSerializer
    permission_classes = ( IsAuthenticated,)
    allow_empty = True;

    def get_queryset(self):
        user = self.request.user
        queryset = ApplicationBasicInfo.objects.filter(owner=user)
        #serializer = ApplicationsSerializer(queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.DATA
        name = data.get('name')
        public = data.get('public')
        if public == 'on':
            public = True
        else:
            public = False
        desc = data.get('description')
        keywords = data.get('keywords')
        client_downloads = data.get('client_downloads')
        new_app = ApplicationBasicInfo(owner =self.request.user ,name=name,description=desc,client_downloads=client_downloads,
                                       keywords = keywords,public=public)
        new_app.save()
        created_data = ApplicationBasicInfo.objects.filter(id=new_app.id)
        serializer = MyApplicationSerializer(created_data)
        headers = self.get_success_headers(serializer.data)
        #return Response(serializer.data, status=201, headers=headers)
        return HttpResponse("Application Created Successfully!", status=202)

# RetrieveUpdateDestroyAPIView
class MyApplicationDetailListView(generics.ListAPIView, generics.RetrieveDestroyAPIView):
    """
    API endpoint that
    1. Detail view of an application belonging to logged-in user
    2. Deletes an application identified by an application-id
    """
    serializer_class = MyApplicationSerializer
    permission_classes = ( IsAuthenticated,)
    allow_empty = False;

    # filter_fields = ('url','id','owner','name',)

    def get_queryset(self):
        print "Inside get"
        user = self.request.user
        queryset = ApplicationBasicInfo.objects.filter(public=True, id=self.kwargs['appid'])

        #serializer = ApplicationsSerializer(queryset)
        return queryset

    def delete(self, request, *args, **kwargs):
        print "Inside delete with id as %s" % (self.kwargs['appid'])
        #Only Owner or admin  can delete application
        try:
            id = str(self.kwargs['appid'])
            delete_application(request, int(id))
            return HttpResponse("Application with id as %s is deleted" % (self.kwargs['appid']), status=200)
        except Exception as e:
            print "%s " % (e.message)
            return HttpResponse(status=404)

class BranchListView(generics.ListAPIView):
    """
    API endpoint that list all branches of an application
    """

    serializer_class = BranchSerializer
    permission_classes = ( IsAuthenticatedOrReadOnly,)


    def get_queryset(self):
        queryset = Branch.objects.all()
        return queryset


class CategoryListView(generics.ListAPIView):
    """
    API endpoint that list all categories of an application
    """
    serializer_class = CategorySerializer
    permission_classes = ( IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset


class SubCategoryListView(generics.ListAPIView):
    """
    API endpoint that list all subcategories of an application
    """
    serializer_class = SubCategorySerializer
    permission_classes = ( IsAuthenticatedOrReadOnly,)


    def get_queryset(self):
        queryset = SubCategory.objects.all()
        return queryset


# #FBV for stopping an application with id as appid
# @api_view(('GET',))
# @permission_classes((IsAuthenticated,))
# def stop(request, appid, format=None):
#     print "In stop"
#     return HttpResponse(status=200)


class UserCloudCredentialsListView(generics.ListCreateAPIView):
    """
    API endpoint that
    1. list cloud credentials
    2. create credentials
    """
    serializer_class = UserCloudCredentialsSerializer
    permission_classes = ( IsAuthenticated,)
    # filter_fields = ('url','id','owner','name',)

    def get_queryset(self):
        user = self.request.user
        queryset = UserCloudCredentials.objects.filter(user=user)
        #serializer = ApplicationsSerializer(queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        print "Creating credentials"
        data = request.DATA
        print data
        cloud = data.get('host_cloud')
        alias = data.get('key_alias')
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        endpoint = data.get('endpoint')
        PADDING = '{'
        BLOCK_SIZE = 16

        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        key = base64.decodestring(bz2.decompress(base64.decodestring(DATA_K)))
        with transaction.atomic():
            #Check if alias exist
            existing_records = UserCloudCredentials.objects.filter(user=request.user, key_alias=alias)
            if existing_records:
                return Response(status=500)
            else:
                keys_ok = False

                cipher = AES.new(key, AES.MODE_CBC, "enw4d2e3w66dugh2")
                try:
                    if len(access_key) == 0:
                        access_key_enc = cipher.encrypt(access_key)
                    else:
                        if len(access_key) % BLOCK_SIZE != 0:
                            access_key = pad(access_key)
                            access_key_enc = cipher.encrypt(access_key)
                    keys_ok = True
                except ValueError as e:
                    print 'ERROR: ' + e.message
                    #return Response(status=500)
                    keys_ok = False
                try:
                    if len(secret_key) == 0:
                        secret_key_enc = cipher.encrypt(secret_key)
                    else:
                        if len(secret_key) % BLOCK_SIZE != 0:
                            secret_key = pad(secret_key)
                    secret_key_enc = cipher.encrypt(secret_key)
                    keys_ok = True
                except ValueError as e:
                    print 'ERROR: ' + e.message
                    keys_ok = False
                if keys_ok:
                    try:

                        credentials = UserCloudCredentials(user=request.user, host_cloud=cloud, key_alias=alias,
                                                           access_key=base64.encodestring(access_key_enc)[:-1],
                                                           secret_key=base64.encodestring(secret_key_enc)[:-1],
                                                           endpoint=endpoint)
                        credentials.save()
                        print 'Created new credential set with ID: ' + str(credentials.id)
                        created_data = UserCloudCredentials.objects.filter(id=credentials.id)
                        print created_data
                        serializer = UserCloudCredentialsSerializer(created_data)
                        headers = self.get_success_headers(serializer.data)
                        return Response(serializer.data, status=201, headers=headers)
                    except Exception as e:

                        print 'Cannot create credentials. Error message' + e.message
                        return Response(status=500, exception=True)
                else:
                    print 'New credential set not created, there was a key error'
                    return Response(status=500)
                    # created_data = UserCloudCredentials.objects.filter(id=credentials.id)
                    # serializer = UserCloudCredentialsSerializer(created_data)
                    # headers = self.get_success_headers(serializer.created_data)
                    # return Response(serializer.created_data, status=201,headers=headers)


class UserCloudCredentialsDetailView(generics.ListAPIView, generics.RetrieveDestroyAPIView):
    """
    API endpoint that
    1. show detail of a credentials
    2. deletes a credential identified by a credential-id
    """
    serializer_class = UserCloudCredentialsSerializer
    permission_classes = ( IsAuthenticated,)
    #renderer_classes = (JSONRenderer)


    def get_queryset(self):
        print "Inside Detail View"
        user = self.request.user
        queryset = UserCloudCredentials.objects.filter(user=user, id=self.kwargs['credid'])
        #serializer = ApplicationsSerializer(queryset)
        return queryset


    def delete(self, request, *args, **kwargs):
        renderer_classes = (JSONRenderer)
        print "Inside delete with is as %s" % (self.kwargs['credid'])

        #UserCloudCredentials.objects.filter( id=self.kwargs['credid']).delete()
        print "Deleting .."
        try:
            UserCloudCredentials.objects.filter(id=int(self.kwargs['credid'])).delete()
            content = {'message': 'Credentials with id ' + self.kwargs['credid'] + ' deleted', 'status': '200'}

            return Response(data=content, status=200)
        except:
            return HttpResponse(status=404)


class CloudInstancesList(generics.ListAPIView):
    """
    API endpoint that list all cloud instances of an application
    """
    serializer_class = CloudInstancesSerializer
    permission_classes = ( IsAuthenticated,)



    def get_queryset(self):
        user = self.request.user
        application = self.kwargs['appid']
        queryset = CloudInstancesOpenstack.objects.filter(application=application)
        #serializer = ApplicationsSerializer(queryset)
        return queryset


class CloudInstancesDetail(generics.ListCreateAPIView):
    """
    API endpoint that
    1. shows detail of an instance.
    2. stops an running instance
    """
    serializer_class = CloudInstancesSerializer
    permission_classes = ( IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        application = self.kwargs['appid']
        instance_id = self.kwargs['instanceid']
        queryset = CloudInstancesOpenstack.objects.filter(application=application, instance_id=instance_id)
        #serializer = ApplicationsSerializer(queryset)
        return queryset

    def post(self, request, *args, **kwargs):

        """
        Stops a running cloud instance
        """
        appid = self.kwargs['appid']
        instanceid = self.kwargs['instanceid']
        task = request.POST.get('status')
        print "In Stop with instanceid as %s" % (instanceid)
        if instanceid is not None:
            response = launch_views.manage_instances(request, task, appid, instanceid)
            if task == 'status':

                string = response.content
                json_obj = json.loads(string)
                res = json_obj[instanceid]
                return HttpResponse(json.dumps(res), content_type="application/json")
            else:
                return response
        else:
            return HttpResponse("Cannot stop application")


@login_required()
@csrf_protect
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def startapp_locally(request, appid):
    """
    API endpoint that starts  an application
    """
    print "In started"
    launchtype = request.GET.get("launchtype", None)
    if launchtype is not None:
        response = launch_views.launchapp(request, appid, launchtype)
        return response
    else:
        return HttpResponse("Cannot start application")


@login_required()
@csrf_protect
def stopinstance(request, appid, instanceid):
    print "In Stop with instanceid as %s" % (instanceid)
    task = "stop"
    if instanceid is not None:
        response = launch_views.manage_instances(request, task, appid, instanceid)
        #(request, task, appid, instancerecord):
        return HttpResponse(response, content_type='application/x-java-jnlp-file')
    else:
        return HttpResponse("Cannot stop application")


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def start_OpenstackServer(request, *args, **kwargs):

    """
    API endpoint that starts an openstack server
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)
    appid = kwargs.get('appid')
    fileid = kwargs.get('fileid')
    endpoint = request.DATA.get('endpoint')
    key_alias = request.DATA.get('alias')
    instance_type = request.DATA.get('instance_type')
    print "Endpint is" + endpoint
    if endpoint is not None and key_alias is not None and instance_type is not None:
        creds = UserCloudCredentials.objects.filter(user_id=request.user, endpoint=endpoint, key_alias=key_alias)
        print creds[0].access_key, creds[0].secret_key
        image_info = ApplicationOpenstackImages.objects.get(id=appid)
        return launch_views.start_server(appid, creds[0], endpoint, image_info.id, instance_type, image_info, request)
    else:
        return HttpResponse(
            json.dumps({'appid': appid, 'error_status': "1", 'errormsg': 'Post Data not in right format!'}),
            content_type="application/json")


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def start_Ec2server(request, *args, **kwargs):

    """
    API endpoint that starts an EC2 instance
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    appid = kwargs.get('appid')
    fileid = kwargs.get('fileid')
    endpoint = request.DATA.get('endpoint')
    key_alias = request.DATA.get('alias')
    instance_type = request.DATA.get('instance_type')
    print request.DATA.get('instance_type')
    if endpoint is not None and key_alias is not None and instance_type is not None:
        creds = UserCloudCredentials.objects.filter(user_id=request.user, endpoint=endpoint, key_alias=key_alias)
        print creds[0].access_key, creds[0].secret_key
        image_info = ApplicationEC2Images.objects.get(id=appid)
        return launch_views.start_server(appid, creds[0], endpoint, image_info.id, instance_type, image_info, request)
    else:
        post_data = {'endpoint': endpoint, 'key_alias': key_alias, 'instance_type': instance_type}
        keys_not_in_data = [k for k, v in post_data.items() if v is None]
        if len(keys_not_in_data) == 1:
            errormessage = 'The key' + keys_not_in_data[0] + ' was needed but was not posted'
        elif len(keys_not_in_data) > 1:
            errormessage = 'The following keys' + keys_not_in_data + ' were needed but was not posted'
        else:
            erromessage = 'Post Data not in right format!'
        return HttpResponse(json.dumps({'appid': appid, 'error_status': "1", 'errormsg': erromessage}),
                            content_type="application/json")

class MyGroupList(generics.ListCreateAPIView):
    """
    API endpoint to
    1) list all Groups
    2) Create group
    """
    serializer_class = MyGroupSerializer
    permission_classes = ( IsAuthenticated,)

    """
        List all the groups for a user
    """

    def get_queryset(self):
        user = self.request.user
        print " Inside manage groups."

        return MyGroup.objects.select_related().all().filter(user=user)

    """
        Creates a group
    """
    def post(self, request, *args, **kwargs):
        user = self.request.user
        print "Inside Create Groups"
        msg =""
        if 'name' in request.DATA and 'description' in request.DATA:
            grpname = request.DATA['name']
            grpdesc = request.DATA['description']
            try:

                mg = MyGroup(name=str(grpname),description=str(grpdesc),owner=request.user, group_role ='Owner')
                mg.save()
                mg.user.add(user)
            except IntegrityError as e:
                msg = e.message
            else:
                msg = "Group created successfully!"
                return HttpResponse(json.dumps({'data': {'name': grpname, 'description': grpdesc}, 'message': msg}),content_type="application/json",status=201)
        else:
            msg = "GroupName and GroupDesc not found in post parameters!!. You would need to add them in the post request."
            return HttpResponse(json.dumps({ 'message': msg}),content_type="application/json")


class MyGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to \n
    1) find group detail identified by groupid \n
    2) delete a group \n
    3) edit a group
    """
    serializer_class = MyGroupSerializer
    permission_classes = ( IsAuthenticated,)

    def get_queryset(self):
        groupid = self.kwargs['pk']
        print groupid
        return MyGroup.objects.filter(id=int(groupid))

    def delete(self, request, *args, **kwargs):
        print "Inside group delete"
        groupid = self.kwargs['pk']
        try:
            MyGroup.objects.filter(id=groupid).delete()
        except IntegrityError as e:
            return HttpResponse(json.dumps({ 'errormessage': 'Cannot Delete the group' + e.message}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({ 'message': "Successfully deleted group"}),content_type="application/json")

    def put(self, request, *args, **kwargs):
        print "Inside Edit group view"
        groupid = self.kwargs['pk']
        try:
            group = MyGroup.objects.get(id=int(groupid))
        except MyGroup.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        else:
            print request.DATA
            grpname = request.DATA.get('name')
            grpdesc = request.DATA.get('description')
            print grpname
            try:

                serializer = MyGroupSerializer(group,data=request.DATA)
                group.name = grpname
                group.description = grpdesc
                group.save()
            except IntegrityError as e:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.data)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class GroupApplicationTagView(generics.CreateAPIView):
    serializer_class = GroupApplicationTagSerializer
    permission_classes = ( IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        pass

class GroupApplicationTagDetailView(generics.ListAPIView,generics.DestroyAPIView):
    serializer_class = GroupApplicationTagSerializer
    permission_classes = ( IsAuthenticated,)

    def get_queryset(self):
        id = self.kwargs.get('id')
        return GroupApplicationTag.objects.filter(id=int(id))

    def delete(self, request, *args, **kwargs):
        groupid = kwargs.get('groupid')
        id = kwargs.get('id')
        try:
            GroupApplicationTag.objects.get(id=id).delete()
        except GroupApplicationTag.DoesNotExist:
            return HttpResponse(json.dumps({ 'errormessage': 'Cannot Detach the application from the group' }),content_type="application/json")
        else:
            return HttpResponse(json.dumps({ 'message': 'Successfully detached application!!' }),content_type="application/json")





@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def leave_group(request, *args, **kwargs):
    groupid = kwargs.get('groupid')
    user = request.user
    print "Leaving group with Groupid" + groupid
    try:
        groups = MyGroup.objects.select_related().filter(user=request.user).get(id=groupid)
        if groups.group_role == 'Owner':
            return HttpResponse(json.dumps({ 'errormessage': 'Error !!, You are an administrator and cannot leave the group.You might want to delete the group' }),content_type="application/json")
        else:
            groups.user.remove(request.user)
            groups.save()
            print "Removing association user from group"
    except IntegrityError as e:
        return HttpResponse(json.dumps({ 'errormessage': 'Error !!, Cannot Leave the group' + e.message}),content_type="application/json")
    else:
        return HttpResponse(json.dumps({ 'message': "User has succesfully left the group"}),content_type="application/json")

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def join_group(request, *args, **kwargs):
    user = request.user
    groupd_ids = request.POST['group_ids']
    int_ids = [int(str(i)) for i in groupd_ids]
    print "Joining the  group(s) with Groupid(s)" + str(int_ids)
    try:
        with transaction.atomic():
            for i in int_ids:
                group = MyGroup.objects.select_related().get(id=i)
                group.user.add(request.user)
                group.save()
    except IntegrityError as e:
        return HttpResponse(json.dumps({ 'errormessage': 'Error !!, Cannot Join the group' + e.message}),content_type="application/json")
    else:
        return HttpResponse(json.dumps({ 'message': "User has succesfully joined the group|groups"}),content_type="application/json")



