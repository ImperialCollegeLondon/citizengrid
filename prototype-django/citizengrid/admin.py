from django.contrib import admin
from citizengrid.models import *

# Setting up access of application's branch, categories and subcategories through CitizenGrid Admin site

admin.site.register(Branch)
admin.site.register(Category)
admin.site.register(SubCategory)