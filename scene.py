#! /usr/bin/python
import getpass
import time
import math

# import the python renderman library
import prman

# create an instance for the RenderMan interface
ri = prman.Ri()

# make the generated RIB file nicely indented
ri.Option("rib", {"string asciistyle": "indented"})

###-------------------------------Function Section--------------------------###

# hyperboloid shapes in the pin
def hyperboloid_wrapper(height, base_radius, top_radius):
    ri.ArchiveRecord(ri.COMMENT, '--Hyperboloid Shape Generated by hyperboloid_wrapper Function--')
    ri.TransformBegin()
    ri.Rotate(-90, 1, 0, 0)
    p_base = [base_radius, 0, 0]
    p_top = [top_radius, 0, height]
    ri.Hyperboloid(p_base, p_top, 360)
    ri.TransformEnd()
    ri.ArchiveRecord(ri.COMMENT, '--!End of hyperboloid_wrapper Function!--')

# model pin
def Pin():
    ri.ArchiveRecord(ri.COMMENT, '--Pin Model Generated by Pin Function--')
    # the pointy end
    ri.TransformBegin()
    end_height = 0.35
    metal_radius = 0.06
    ri.Translate(0, end_height, 0)
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Color([1, 1, 1])
    ri.Rotate(90, 1, 0, 0)
    ri.Surface("metal")
    ri.Cone(end_height, metal_radius, 360)
    ri.AttributeEnd()
    ri.TransformEnd()

    #the metal stick
    metal_height = 0.9
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Color([1,1,1])
    ri.Rotate(-90, 1, 0, 0)
    ri.Surface("metal")
    ri.Cylinder(metal_radius, 0, metal_height, 360)
    ri.AttributeEnd()
    ri.TransformEnd()

    # base for bowly shaped part
    ri.TransformBegin()
    ri.Translate(0, metal_height, 0)
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Color([0.2,0.2,0.8])
    ri.Rotate(-90, 1, 0, 0)
    disk_radius = 0.45
    ri.Surface("plastic")

    ri.Disk(0, disk_radius, 360)
    ri.AttributeEnd()
    ri.TransformEnd()

    # bowly shaped part
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Color([0.2,0.2,0.8])
    bowl_radius = 0.47
    ri.Translate(0, -0.05, 0)
    ri.Rotate(-90, 1, 0, 0)
    y_max = 0.433
    y_min = 0.05
    ri.Surface("plastic")
    ri.Sphere(bowl_radius, y_min, y_max, 360)
    ri.AttributeEnd()
    ri.TransformEnd()

    # plastic main body
    ri.TransformBegin()
    ri.Translate(0, y_max - y_min, 0)
    ri.AttributeBegin()
    ri.Color([0.2,0.2,0.8])
    body_height = 0.7
    body_br = 0.2
    body_tr = 0.15
    ri.Surface("plastic")
    hyperboloid_wrapper(body_height, body_br, body_tr)
    ri.AttributeEnd()

    # top base (tb)
    ri.TransformBegin()
    ri.Translate(0, body_height, 0)
    ri.AttributeBegin()
    ri.Color([0.2,0.2,0.8])
    tb_height = 0.08
    tb_tr = 0.375
    ri.Surface("plastic")
    hyperboloid_wrapper(tb_height, body_tr, tb_tr)
    ri.AttributeEnd()

    # top top (tt)
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Color([0.2,0.2,0.8])
    ri.Translate(0, tb_height, 0)
    tt_tr = 0.35
    ri.Surface("plastic")
    hyperboloid_wrapper(tb_height, tb_tr, tt_tr)
    ri.AttributeEnd()

    # top cup (tc)
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Color([0.2,0.2,0.8])
    ri.Translate(0, tb_height, 0)
    ri.Rotate(-90, 1, 0, 0)
    tc_radius = tt_tr
    ri.Surface("plastic")
    ri.Disk(0, tc_radius, 360)
    ri.AttributeEnd()

    ri.TransformEnd()
    ri.TransformEnd()
    ri.TransformEnd()
    ri.TransformEnd()
    ri.TransformEnd()
    ri.TransformEnd()

    ri.ArchiveRecord(ri.COMMENT, '--!End of Pin Function!--')

def Table():
    ri.ArchiveRecord(ri.COMMENT, '--Table Model Generated by Table Function--')
    ri.AttributeBegin()
    ri.Color([0.7, 0.7, 0.8])
    ri.Surface("plastic")
    face = [10, 0, 10, 10, 0, -10, -10, 0, 10, -10, 0, -10]
    ri.Patch("bilinear",{'P':face})
    ri.AttributeEnd()
    ri.ArchiveRecord(ri.COMMENT, '--!End of Table Function!--')

###-------------------------End of Function Section-------------------------###


filename = "scene.rib"
# begin of RIB archive
ri.Begin(filename)

ri.ArchiveRecord(ri.COMMENT, 'File ' +filename)
ri.ArchiveRecord(ri.COMMENT, "Created by " + getpass.getuser())
ri.ArchiveRecord(ri.COMMENT, "Creation Date: " +time.ctime(time.time()))

# ri.Declare("Ambient" ,"string")
# ri.Declare("Light1" ,"string")
# ri.Declare("Light2" ,"string")
# ri.Declare("Light3" ,"string")

# set up the scene
ri.Display("scene.exr", "framebuffer", "rgba")
ri.Format(720, 575, 1)
# ri.Projection(ri.PERSPECTIVE)

#Fix the sampling to 720 to reduce noise, put pixel variance low for better look. 
ri.Hider("raytrace" ,{"int incremental" :[2], "int maxsamples" : 720, "int minsamples" : 720 })
ri.PixelVariance (0.01)
ri.ShadingRate(10)

#Path tracer for final lighting and shading. 
ri.Integrator ("PxrPathTracer" ,"integrator")

# now set the projection to perspective
ri.Projection(ri.PERSPECTIVE,{ri.FOV:30} )

#Move our camera into place.
ri.Rotate(-25,1,0,0)
ri.Translate(0,-2,2)

# start the World
ri.WorldBegin()

#-------------------Lights--------------------
#Add a few lights to brighten up the scene. 
ri.AttributeBegin()
ri.Declare("areaLight" ,"string")
ri.AreaLightSource( "PxrStdAreaLight", {ri.HANDLEID:"areaLight", 
                                        "float exposure" : [10]
                                       })

ri.Bxdf( "PxrDisney","bxdf", { 
                        "color emitColor" : [ 1,1,1]
                        })
#Light 1 (South West)
ri.TransformBegin()
ri.Translate(10, 8,4)
ri.Scale(4,4,4)
ri.Geometry("spherelight")
ri.TransformEnd()
#Light 2 (North East)
ri.TransformBegin()
ri.Translate(-10, 8,4)
ri.Scale(4,4,4)
ri.Geometry("spherelight")
ri.TransformEnd()
ri.TransformBegin()
#Light 3 (South East)
ri.Translate(10,8,-8)
ri.Scale(4,4,4)
ri.Geometry("spherelight")
ri.TransformEnd()
ri.AttributeEnd()
#-------------------!Lights--------------------


# # place the lights
# ri.LightSource("ambientlight", {ri.HANDLEID:"Ambient", "float intensity": [0.1]})

# ri.LightSource( "pointlight", {ri.HANDLEID:"Light1", "point from":[-2,2,4], "float intensity": [13]})

# ri.TransformBegin()
# ri.Translate(2,2,4)
# ri.LightSource("pointlight", {ri.HANDLEID:"Light2", "point from":[0,0,0] ,"float intensity" :[17]})
# ri.TransformEnd()

# ri.TransformBegin()
# ri.LightSource("pointlight",{ri.HANDLEID: "Light3","point from": [2,1,3] ,"float intensity": [7]})

# # turn on the lights
# ri.Illuminate("Light1",1)
# ri.Illuminate("Light2",1)
# ri.Illuminate("Light3",1)

#adjust camera position(?????)
# ri.Translate(0, -1.5, 4)
# ri.Rotate(-20, 1, 0, 0)

# the groundplane
Table()

# create and move the pin
ri.TransformBegin()
ri.Scale(1.5, 1.5, 1.5)
ri.Rotate(45, 1, 0, 0)
Pin()
ri.TransformEnd()

# ri.TransformEnd()

# end of the world
ri.WorldEnd()

# end of rib file
ri.End()
