# Generate a visicon to use for an application's unique image

import visicon
from PIL.Image import Image

from numpy.random.mtrand import RandomState
import binascii
import time 

def create_icon(filename):

    rand = RandomState()
      
    lo = 1000000000000000
    hi = 999999999999999999
    random_string = binascii.b2a_hex(rand.randint(lo, hi, 4).tostring())[:64]
    time_millis = int(round(time.time() * 1000))
    
    v = visicon.Visicon(random_string, str(time_millis), 128)
    i = v.draw_image()
    i.save(filename)
