from latk_blender import *
#~
latk_settings=bpy.context.scene.latk_settings
la = fromGpToLatk()
la.clean()
gpMesh(_la=la, _saveLayers=True, _thickness=latk_settings.thickness, _remesh=latk_settings.remesh_mode.lower(), _resolution=latk_settings.resolution, _bevelResolution=latk_settings.bevelResolution, _decimate=latk_settings.decimate, _vertexColorName=latk_settings.vertexColorName)
