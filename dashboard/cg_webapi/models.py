from django.db import models

# Create your models here.
class VmcpRequest(models.Model):
    vmcp_key = models.CharField(max_length=64, unique=True)
    content = models.TextField()
