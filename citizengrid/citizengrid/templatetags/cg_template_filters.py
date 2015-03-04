from django.template.defaultfilters import register

import os

from citizengrid.models import ApplicationFile

# Custom template filter to get array index by variable value
#@register.filter(name='indexminusone')
#def indexminusone(arr, index):
#    return arr[int(index) - 1]

# Custom template filter to get application path from dict by dict key
@register.filter(name='getdictitem')
def getdictitem(dict, key):
    return dict[key]

@register.filter(name='getfileformat')
def getfileformat(formatkey):
    for item in ApplicationFile.FILE_FORMATS:
        if item[0] == formatkey:
            return item[1]
    return 'Unknown format'

@register.filter(name='getfileurl')
def getfileurl(path, username):
    base = os.path.basename(str(path))
    return '/' + os.path.join('media', username, base)

@register.filter(name='getfilebasename')
def getfilebasename(path):
    pathstring = str(path)
    return os.path.basename(pathstring)