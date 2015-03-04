from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError

from citizengrid.models import UserInfo
from citizengrid.models import ApplicationFile
from citizengrid.models import ApplicationBasicInfo
from citizengrid.models import Branch
from citizengrid.models import Category
from citizengrid.models import SubCategory

import urlparse

class ExtendedUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label='First name', max_length=30)
    last_name = forms.CharField(label='Surname', max_length=30)
    email = forms.EmailField(label='Email', max_length=128)

    #class Meta:
        #model = User
        #fields = ("username","first_name", "last_name", "email", )
    def create(self, commit = True):
        user = User.objects.create_user(username = self.cleaned_data['username'], email = self.cleaned_data['email'], password = self.cleaned_data['password2'])
        user_info = UserInfo.objects.create(user=user, user_status='N')
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.save()

        # Create a UserInfo object for this user and set it to status 'New'

        user_info.save()

        return user

    def save(self, user, commit=True):
        #user.user_name = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.save()

        # Create a UserInfo object for this user and set it to status 'New'

        #user_info.save()

        return user


    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError('Password do not match.')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('Username is already taken.')


class UpdateUserCreationForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=30)
    last_name = forms.CharField(label='Surname', max_length=30)
    email = forms.EmailField(label='Email', max_length=128)


    def update(self, user, commit=True):
        #user.user_name = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.save()

        # Create a UserInfo object for this user and set it to status 'New'

        #user_info.save()

        return user


    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError('Password do not match.')


def validate_image_location(value):
        print 'Call to override image_location validation...value: ' + value

class ApplicationBasicInfoForm(forms.Form):
    # Store the request object so we can use it in form cleaning
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ApplicationBasicInfoForm, self).__init__(*args, **kwargs)


    name = forms.CharField(max_length=128)
    description = forms.CharField()
    iconfile = forms.FileField(
        label='Select a logo file',
        help_text='jpg or png or gif'
    )
    public = forms.BooleanField(required=False)
    select_category = forms.BooleanField(required=False)
    additional_Information = forms.CharField(required=False)
    keywords = forms.CharField(max_length=128, required=False)

class  ApplicationServerInfoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super( ApplicationServerInfoForm, self).__init__(*args, **kwargs)

    SERVER_APP_HOST_CHOICES = (('Public', 'Amazon EC2'),('Private','OpenStack'),('CitizenGrid','CitizenGrid'),('Local', 'Local'), ('NONE','None'))
    server_hosting_platform = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=SERVER_APP_HOST_CHOICES)
    server_image_id = forms.CharField(max_length=64, required=False)
    server_image_location = forms.CharField(max_length=256, required=False)


class  ApplicationClientInfoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super( ApplicationClientInfoForm, self).__init__(*args, **kwargs)
        
    CLIENT_HOST_CHOICES = (('Public', 'Amazon EC2'), ('Private','OpenStack'), ('Local','VirtualBox'), ('NONE','None'))
    client_platform = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=CLIENT_HOST_CHOICES)
    client_image_id = forms.CharField(max_length=64, required=False)
    client_image_location = forms.CharField(max_length=256, required=False)

    def clean_image_location(self):
        print 'Call to clean image_location...value: ' + str(self.data['image_location'])
        # Check if the user has already uploaded some files for this app
        tempfiles = ApplicationFile.objects.filter(file_type='T', owner=self.request.user)
        print 'PROCESSING APP REGISTRATION: User has prepared ' + str(len(tempfiles)) + ' files...'

        # If the length of tempfiles is 0 then the image location property is required
        if len(tempfiles) == 0:
            imgloc = self.data['image_location']
            if imgloc != '':
                url_pieces = urlparse.urlsplit(imgloc)
                if not url_pieces.scheme or not url_pieces.netloc:
                    imgloc = None
            if not imgloc or imgloc == '':
                print 'PROCESSING APP REGISTRATION: No files uploaded and invalid URL specified for image_location'
                raise ValidationError(u'You must upload an image file OR specify the URL of a remote image.')

class CloudCredentialsForm(forms.Form):
    cloud = forms.ChoiceField(choices=(('Public', 'Amazon EC2'), ('Private','OpenStack'), ('CitizenGrid','CitizenGrid'),('Other','Other')))
    alias = forms.CharField(max_length=64)
    access_key = forms.CharField(max_length=64)
    secret_key = forms.CharField(max_length=64)
    endpoint = forms.URLField(min_length=11, max_length=256, required=True)

class CloudImageForm(forms.Form):
    cloud = forms.ChoiceField(choices=(('Private', 'OpenStack'),('Public','Amazon EC2')))
    endpoint = forms.URLField(min_length=11, max_length=256, required=True)
    image_id = forms.CharField(max_length=64, required=True)
    server_client = forms.ChoiceField(choices=(('C', 'Client Image'),('S','Server Image')))

class LocalImageForm(forms.Form):
    local = forms.ChoiceField(choices=(('vdi', 'VDI'),('ovf','OVF'),('ova','OVA'),('vmdk','VMDK'),('iso','ISO'),('img','RAW_HD'),('hd','RAW_IMG')))
    local_image = forms.FileField


