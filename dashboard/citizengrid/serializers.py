#===============================================================================
# Webapi serializers
#===============================================================================
import os
from rest_framework import serializers
from citizengrid.models import Branch,Category, SubCategory, ApplicationBasicInfo, ApplicationFile, ApplicationOpenstackImages, ApplicationEC2Images, \
    UserCloudCredentials, CloudInstancesOpenstack,MyGroup, GroupApplicationTag
from django.contrib.auth.models import User, Group


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')
        exclude =('password',)

class PasswordSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('password')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class BranchSerializer(serializers.ModelSerializer):
    """
       Serializes Branches
    """
    class Meta:
         model = Branch
         fields = ('id','name','description')

class CategorySerializer(serializers.ModelSerializer):
    """
       Serializes Categories
    """
    class Meta:
         model = Category
         fields = ('id','name','description')

class SubCategorySerializer(serializers.ModelSerializer):
    """
       Serializes Subcategories
    """
    class Meta:
         model = SubCategory
         fields = ('id','name','description')


class ApplicationsSerializer(serializers.ModelSerializer):
    branch = serializers.RelatedField(many=True)
    category = serializers.RelatedField(many=True)
    subcategory = serializers.RelatedField(many=True)

    class Meta:
            model = ApplicationBasicInfo
            field = ('url','id','owner','name','creation_time','last_updated','client_downloads', 'description','branch','category','subcategory')
            exclude = ('public','iconfile',)

class ApplicationDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
        Serializes application detail
    """
    branch = serializers.RelatedField(many=True)
    category = serializers.RelatedField(many=True)
    subcategory = serializers.RelatedField(many=True)
    class Meta:
          model = ApplicationBasicInfo
          field = ('id','owner','name','description','branch','category','subcategory')
          exclude = ('creation_time','last_updated','client_downloads','public','iconfile')


class MyApplicationSerializer(serializers.ModelSerializer):
    """
        Serializes applications

    """
    branch = serializers.RelatedField(many=True)
    category = serializers.RelatedField(many=True)
    subcategory = serializers.RelatedField(many=True)

    class Meta:
          model = ApplicationBasicInfo
          field = ('id','owner_id','name','description','branch','category','subcategory')
          exclude = ('iconfile',)

class ApplicationFileSerializer(serializers.ModelSerializer):
    owner = serializers.RelatedField(many=False)
    file = serializers.Field(source='filename')

    class Meta:
        model = ApplicationFile

        include = ('url','owner', 'file', 'application', 'file_type', 'file_format','image_type','gadhauKaun')

class ApplicationFileDetailSerializer(serializers.ModelSerializer):
    owner = serializers.RelatedField(many=False)
    #application = serializers.RelatedField(many=False)
    class Meta:
        model = ApplicationFile
        include = ('url','owner', 'filename', 'application', 'file_type', 'file_format','image_type')


class ApplicationOsImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationOpenstackImages
        include = ('application', 'image_id', 'zone_name', 'zone_url', 'image_type')


class ApplicationEc2Serializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationEC2Images
        include = ('application', 'image_id', 'zone_name', 'zone_url', 'image_type')

class UserCloudCredentialsSerializer(serializers.ModelSerializer):
    user = serializers.RelatedField(many=False)
    #application = serializers.RelatedField(many=False)
    class Meta:
        model = UserCloudCredentials
        include = ('user', 'key_alias', 'endpoint')

class CloudInstancesSerializer(serializers.ModelSerializer):
    owner = serializers.RelatedField(many=False)
    application = serializers.RelatedField(many=False)
    application_image = serializers.RelatedField(many=False)
    class Meta:
        model = CloudInstancesOpenstack
        fields = ('owner','application','application_image','instance_id','status')

class MyGroupSerializer(serializers.ModelSerializer):
    user = serializers.RelatedField(many=True)
    class Meta:
        model = MyGroup
        fields = ('name','description','owner','group_role')
        read_only_fields = ('owner','group_role')

class GroupApplicationTagSerializer(serializers.ModelSerializer):
    #application = serializers.RelatedField(many=False)
    #group = serializers.RelatedField(many=False)
    class Meta:
        model = GroupApplicationTag
        fields = ('tagname','description','group','application','tagid')
        read_only_fields = ('group',)







