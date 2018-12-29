# 1 of 10. MAIN

bl_info = {
    "name": "Lightning Artist Toolkit (Latk)", 
    "author": "Nick Fox-Gieg",
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

