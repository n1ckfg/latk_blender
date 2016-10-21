'''
The Lightning Artist Toolkit was developed with support from:
   Canada Council on the Arts
   Eyebeam Art + Technology Center
   Ontario Arts Council
   Toronto Arts Council
   
Copyright (c) 2016 Nick Fox-Gieg
http://fox-gieg.com

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Lightning Artist Toolkit is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of 
the License, or (at your option) any later version.

The Lightning Artist Toolkit is distributed in the hope that it will 
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with the Lightning Artist Toolkit.  If not, see 
<http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "LightningArtist Toolkit", 
    "category": "Animation"
}

def register():
	pass

def unregister():
	pass

import bpy
from mathutils import *
from math import sqrt
import json
import re
from bpy_extras.io_utils import unpack_list
#from curve_simplify import *
import random
import bmesh
import sys
import gc

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

