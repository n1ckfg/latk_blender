'''
LIGHTNING ARTIST TOOLKIT (BLENDER)

The Lightning Artist Toolkit was developed with support from:
   Canada Council on the Arts
   Eyebeam Art + Technology Center
   Ontario Arts Council
   Toronto Arts Council
   
Copyright (c) 2020 Nick Fox-Gieg
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

# 2 of 12. MAIN

bl_info = {
    "name": "Lightning Artist Toolkit (Latk)", 
    "author": "Nick Fox-Gieg",
    "blender": (2, 80, 0),
    "description": "Import and export Latk format",
    "category": "Animation"
}

import bpy
import bmesh
import bpy_extras
from bpy_extras import view3d_utils
from bpy_extras.io_utils import unpack_list
from bpy.types import Operator, AddonPreferences
from bpy.props import (BoolProperty, FloatProperty, StringProperty, IntProperty, PointerProperty, EnumProperty)
from bpy_extras.io_utils import (ImportHelper, ExportHelper)
#~
from freestyle.shaders import *
from freestyle.predicates import *
from freestyle.types import Operators, StrokeShader, StrokeVertex
from freestyle.chainingiterators import ChainSilhouetteIterator, ChainPredicateIterator
from freestyle.functions import *
#~
import math
from math import sqrt
from mathutils import *
from mathutils import Vector, Matrix
#~
import json
import xml.etree.ElementTree as etree
import base64
#~
import re
import parameter_editor
import random
import sys
import gc
import struct
import uuid
import contextlib
from collections import defaultdict
from itertools import zip_longest
from operator import itemgetter
#~
import os
import zipfile
import io
from io import BytesIO

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

