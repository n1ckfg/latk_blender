'''
LIGHTNING ARTIST TOOLKIT v1.0.0

The Lightning Artist Toolkit was developed with support from:
   Canada Council on the Arts
   Eyebeam Art + Technology Center
   Ontario Arts Council
   Toronto Arts Council
   
Copyright (c) 2018 Nick Fox-Gieg
http://fox-gieg.com

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Lightning Artist Toolkit (Blender) is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of 
the License, or (at your option) any later version.

The Lightning Artist Toolkit (Blender) is distributed in the hope that it will 
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with the Lightning Artist Toolkit (Blender).  If not, see 
<http://www.gnu.org/licenses/>.
'''

# 1 of 10. MAIN

bl_info = {
    "name": "Lightning Artist Toolkit (Latk)", 
    "author": "Nick Fox-Gieg",
    "description": "Import and export latk format",
    "category": "Animation"
}

import bpy
import bpy_extras
from bpy_extras import view3d_utils
from mathutils import *
from mathutils import Vector, Matrix
from math import sqrt
import math
import json
import re
from bpy_extras.io_utils import unpack_list
import parameter_editor
#from curve_simplify import *
import random
import bmesh
import sys
import gc
import xml.etree.ElementTree as etree
from operator import itemgetter
#~
import zipfile
from io import BytesIO
import os
#~
from freestyle.shaders import *
from freestyle.predicates import *
from freestyle.types import Operators, StrokeShader, StrokeVertex
from freestyle.chainingiterators import ChainSilhouetteIterator, ChainPredicateIterator
from freestyle.functions import *
#~
from bpy.types import Operator, AddonPreferences
from bpy.props import (BoolProperty, FloatProperty, StringProperty, IntProperty, PointerProperty, EnumProperty)
from bpy_extras.io_utils import (ImportHelper, ExportHelper)

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

