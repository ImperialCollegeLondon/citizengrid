from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import os

class UserInfo(models.Model):
    USER_STATUS = (
        ('N', 'New'),
        ('A', 'Active'),
    )

    PRIMARY_ROLE = (
        ('N', 'Not Set'),
        ('P', 'Application Provider'),
        ('U', 'Application User'),
    )

    user = models.ForeignKey(User, primary_key=True)
    user_status = models.CharField(max_length=1, choices=USER_STATUS)
    user_primary_role = models.CharField(max_length=1, choices=PRIMARY_ROLE, default="N")
    user_primary_role_desc = models.CharField(max_length=128, choices=PRIMARY_ROLE, default="Not Set")

class Branch(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=256)
    def __unicode__(self):
        return u'{0}'.format(self.name)

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=60)
    branch =  models.ForeignKey(Branch,null=False)
    def __unicode__(self):
        return u'{0}'.format(self.name)

class SubCategory(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=60)
    category = models.ForeignKey(Category,null=False)
    def __unicode__(self):
        return u'{0}'.format(self.name)

# Database View over Branch ->Category ->SubCategory
class CGView(models.Model):
    name = models.CharField(max_length=30)
    category_name = models.CharField(max_length=30)
    category_id = models.IntegerField(null=False)
    subcategory_name = models.CharField(max_length=30)
    subcategory_id = models.IntegerField(null=False)

class Meta:
    managed = False

class ApplicationBasicInfo(models.Model):
    owner = models.ForeignKey(User) # Not displayed in the basic form
    name = models.CharField(max_length=128)
    #organisation = models.CharField(max_length=128)
    description = models.TextField()
    creation_time = models.DateTimeField(auto_now_add=True) # Not to be displayed in the basic form
    last_updated = models.DateTimeField(auto_now_add=True) # Not to be displayed in the basic form
    client_downloads = models.IntegerField() # Not to be displayed in the basic form
    public = models.BooleanField()
    iconfile = models.ImageField(upload_to='/media/')
    keywords = models.CharField(max_length=128, default='NONE')
    branch = models.ManyToManyField(Branch,default='NONE')
    category = models.ManyToManyField(Category,default='NONE')
    subcategory = models.ManyToManyField(SubCategory,default='NONE')
    def __unicode__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=60)
    def __unicode__(self):
        return u'{0}'.format(self.name)

class MyGroup(models.Model):

    GROUP_ROLE = (
        ('Owner', 'Owner'),
        ('Member','Member'),
    )

    name = models.CharField(max_length=128)
    owner =  models.CharField(max_length=128)
    description = models.TextField()
    creation_time = models.DateTimeField(auto_now_add=True)
    user = models.ManyToManyField(User,default='NONE')
    group_role = models.CharField(max_length=1, choices=GROUP_ROLE, default='Member')

    def __unicode__(self):
        return self.name

class GroupApplicationTag(models.Model):
    tagname = models.CharField(max_length=128)
    description = models.TextField()
    creation_time = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(MyGroup,null=True)
    application = models.ForeignKey(ApplicationBasicInfo,null=True)
    tagid = models.CharField(max_length=128)



def upload_file_location(instance, filename):
    fs = FileSystemStorage()
    base = fs.location
    print "About to save uploaded temp file to: " + os.path.join(base, instance.owner.username, instance.application.name, filename) #there should be app id should be also in this.
    return os.path.join(base, instance.owner.username, instance.application.name, filename)

class ApplicationFile(models.Model):
    FILE_TYPE = (
        ('T', 'Temporary'),
        ('S', 'Stored'),
    )

    FILE_FORMATS = (
        ('NONE', 'File Type Not Specified or Unknown'),
        ('HD', 'RAW Hard Disk Image'),
        ('IMG', 'RAW Hard Disk Image'),
        ('VDI', 'Virtualbox Virtual Disk Image'),
        ('VMDK', 'VMware Virtual Machine Disk'),
        ('ISO', 'CD/DVD ROM Disk Image'),
        ('OVF', 'Open Virtualization Format Descriptor'),
        ('OVA', 'Open Virtualization Format Archive')
    )

    IMAGE_TYPE = (
        ('C', 'Client'),
        ('S', 'Server'),
        ('I', 'Icon'),
    )

    owner = models.ForeignKey(User)
    file = models.FileField(max_length=255, upload_to = upload_file_location,
                            storage = FileSystemStorage())
    application = models.ForeignKey(ApplicationBasicInfo, null=True)
    file_type = models.CharField(max_length=1, choices=FILE_TYPE, default='T')
    file_format = models.CharField(max_length=4, choices=FILE_FORMATS, default='NONE')
    image_type = models.CharField(max_length=1, choices=IMAGE_TYPE, default='C')

    def __unicode__(self):
        return self.filename()

    def filename(self):
        return os.path.basename(self.file.name)

class ApplicationServerInfo(models.Model):
    SERVER_APP_HOST_CHOICES = (('Public', 'Amazon EC2'), ('Private','OpenStack'), ('CitizenGrid','CitizenGrid'), ('Local','Local'),('NONE','None'))
    appref = models.ForeignKey(ApplicationBasicInfo)
    apphost = models.CharField(max_length=64, choices=SERVER_APP_HOST_CHOICES, default='NONE')
    server_image_id = models.CharField(max_length=64)
    server_image_location = models.CharField(max_length=256)

class ApplicationClientInfo(models.Model):
    CLIENT_HOST_CHOICES = (('Public', 'Amazon EC2'), ('Private','OpenStack'), ('Local','VirtualBox'))
    appref = models.ForeignKey(ApplicationBasicInfo)
    clienthost = models.CharField(max_length=64, choices=CLIENT_HOST_CHOICES, default='Local')
    client_image_id = models.CharField(max_length=64)
    client_image_location = models.CharField(max_length=256)

class UserCloudCredentials(models.Model):
    HOST_CHOICES = (('Public', 'Amazon EC2'), ('Private','OpenStack'), ('CitizenGrid','CitizenGrid'),('Other','Other'))
    host_cloud = models.CharField(max_length=64, choices=HOST_CHOICES, default ='Other')
    user = models.ForeignKey(User)
    key_alias = models.CharField(max_length=64)
    access_key = models.CharField(max_length=64)
    secret_key = models.CharField(max_length=64)
    endpoint = models.CharField(max_length=256)

    def __unicode__(self):
        return self.key_alias

class ApplicationEC2Images(models.Model):

    IMAGE_TYPE = (
        ('C', 'Client'),
        ('S', 'Server'),
    )

    #owner = models.ForeignKey(User, default = User)
    application = models.ForeignKey(ApplicationBasicInfo, null=True)
    image_id = models.CharField(max_length=20)
    zone_name = models.CharField(max_length=64)
    zone_url = models.CharField(max_length=256)
    image_type = models.CharField(max_length=1, choices=IMAGE_TYPE, default='C')
    def __unicode__(self):
        return self.image_id

class ApplicationOpenstackImages(models.Model):

    IMAGE_TYPE = (
        ('C', 'Client'),
        ('S', 'Server'),
    )
    #owner = models.ForeignKey(User, default = User)
    application = models.ForeignKey(ApplicationBasicInfo, null=True)
    image_id = models.CharField(max_length=20)
    zone_name = models.CharField(max_length=64)
    zone_url = models.CharField(max_length=256)
    image_type = models.CharField(max_length=1, choices=IMAGE_TYPE, default='C')
    def __unicode__(self):
        return self.image_id

class CloudInstancesOpenstack(models.Model):

    IMAGE_TYPE = (
        ('C', 'Client'),
        ('S', 'Server'),
    )
    owner =  models.ForeignKey(User)
    application = models.ForeignKey(ApplicationBasicInfo)
    application_image = models.ForeignKey(ApplicationOpenstackImages)
    credentials = models.ForeignKey(UserCloudCredentials)
    instance_id = models.CharField(max_length=16)
    status = models.CharField(max_length=32)
    image_type = models.CharField(max_length=1, choices=IMAGE_TYPE, default='C')

class CloudInstancesAWS(models.Model):

    IMAGE_TYPE = (
        ('C', 'Client'),
        ('S', 'Server'),
    )
    owner =  models.ForeignKey(User)
    application = models.ForeignKey(ApplicationBasicInfo)
    application_image = models.ForeignKey(ApplicationEC2Images)
    credentials = models.ForeignKey(UserCloudCredentials)
    instance_id = models.CharField(max_length=16)
    status = models.CharField(max_length=32)
    image_type = models.CharField(max_length=1, choices=IMAGE_TYPE, default='C')

class UsersApplications(models.Model):
    user =  models.ForeignKey(User)
    application = models.ForeignKey(ApplicationBasicInfo)
    creation_time = models.DateTimeField(auto_now_add=True)
    run_count = models.IntegerField(default=1) 
    def __unicode__(self):
        return self.application


class RawApplications(models.Model):
    
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=128)
    start_date = models.DateTimeField(null=True)
    institution = models.CharField(max_length=128,null=True)
    branch = models.CharField(max_length=128,null=True)
    category = models.CharField(max_length=128,null=True)
    subcategory = models.CharField(max_length=128,null=True)
    research_focus = models.TextField(null=True)
    boinc_based = models.BooleanField()
    performance = models.CharField(max_length=128,null=True)
    url = models.CharField(max_length=128,null=True)
    def __unicode__(self):
        return self.name