import prman
import sys, os.path, subprocess
ri = prman.Ri()

def checkAndCompileShader(shader) :
        #.oso is the filetype that rib files read, so .osl files need to be converted into .oso files before rendering
        #so this if statement checks if either there is no .oso file or if the .osl file has been modified more recently than the .oso
        #and in either case it creates a new .oso file from the .osl, by using the command 'oslc shader.osl'
        if os.path.isfile(shader+'.oso') != True  or os.stat(shader+'.osl').st_mtime - os.stat(shader+'.oso').st_mtime > 0 :
            print 'compiling shader %s' %(shader)
            try :
                subprocess.check_call(['oslc', shader+'.osl'])
            except subprocess.CalledProcessError :
                sys.exit('shader compilation failed')

def renderingRoutine(filename):
    ri.Begin(filename)
    
    ri.Display("flowerPot.tiff", "it", "rgb")
    ri.Format(1920,1080,1.0)
    ri.Projection("perspective", {"fov" : [30]})
    ri.Hider("raytrace", {"int incremental" : [1]})
    ri.Integrator("PxrPathTracer", "integrator")

    fstop = 1.0
    focalLength = 0.1 #0.2 for standard angle
    focalDistance = 10 #9.5 for standard angle
    ri.DepthOfField(fstop, focalLength, focalDistance)

    #-----------Move everything back from camera-----------------------
    ri.Translate(0,0,5.5)
    ri.Translate(0,-0.8,0)
    #can remove line below to put it at side of screen
    ri.Translate(1.8,0,0)
    #set below to Rotate(-20,1,0,0) for standard angle
    ri.Rotate(-40,1,0,0)
    #remove lines below for standard angle
    ri.Translate(0,0,-2)
    ri.Translate(0,-0.5,0)

    ri.WorldBegin()

    #------------------Dome Light-------------------------------------
    ri.AttributeBegin()
    ri.Rotate(-90,1,0,0)
    ri.Rotate(10,0,0,1)
    ri.Light("PxrDomeLight","domeLight",
    {
        "float exposure" : [0], 
        "string lightColorMap" : ["envMap.tx"]
    })
    ri.AttributeEnd()

    #----------------Ground Plane--------------------------------------
    s = 32
    planePoints = [ -s, 0, 3,  
                     s, 0, 3, 
                    -s, 0, 3+2*s,
                     s, 0, 3+2*s ]
    ri.AttributeBegin()
    
    ri.Pattern('groundPlaneShader', 'groundPlaneShader',
    {
        'string TextureName' : ["marble.tx"],
    })    
    ri.Pattern('PxrBump', 'groundPlaneBumpMap',
    {
        'string filename' : ["marbleBmp.tx"]
    })
    ri.Pattern('PxrNormalMap', 'groundPlaneNormalMap',
    {
        'string filename' : ["marbleNormal.tx"]
    })
    
    ri.Bxdf('PxrSurface', 'marble',
    {
        'reference color diffuseColor' : ['groundPlaneShader:Cout'],
        'int diffuseDoubleSided' : [1],
        'float diffuseRoughness' : [0.2],
        'float reflectionGain' : [0.001],
        'float glassRoughness' : [0.2]
    })
    ri.Translate(0,-3,0)
    ri.Patch("bilinear", {"P" : planePoints})
    ri.AttributeEnd()

#----------------------FLOWER POT-----------------------------------------
    ri.TransformBegin()
    
    ri.Translate(-2,0,0)
    ri.Translate(0,0,5)
    ri.Translate(0,-0.1,0)
    ri.Rotate(90,1,0,0)

    ri.CoordinateSystem('pot')

    #-----------------Flower Pot Material--------------------------------
    ri.AttributeBegin()

    ri.Attribute('displacementbound', 
    {
        'sphere' : [1],
        'coordinatesystem' : ['shader']
    })

    ri.Displace('PxrDisplace', 'myDisp',
    {
        'float dispAmount' : [2],
        'reference float dispScalar' : ['flowerPotShader:dispOut']
    })

    ri.Pattern('flowerPotShader','flowerPotShader',
    {
        'color cin' : [0.725*0.6, 0.522*0.4, 0.365*0.3]
        #'color cin' : [0.15,0.05,0]
    })

    ri.Bxdf('PxrSurface','flowerPotSurface',
    {
        'reference color diffuseColor' : ['flowerPotShader:cout'],
        'float subsurfaceGain' : [0.025],
        'int diffuseDoubleSided' : [1], 
        'float diffuseRoughness' : [0.6]
    })

    #-------------------Flower Pot Geometry---------------------------
    rCone = 1.6
    hCone = 10
    rMinTorus1 = 0.075
    hCylinder1 = 0.5
    rMinTorus2 = 0.1
    hCylinder2 = 0.05

    ri.Cone(hCone,rCone,360)

    ri.Torus(rCone + rMinTorus1, rMinTorus1, 0, 360, 360)
    ri.Translate(0, 0, -hCylinder1)
    ri.Cylinder(rCone,0,hCylinder1, 360)
    ri.Cylinder(rCone + 2*rMinTorus1, 0, hCylinder1, 360)
    ri.Torus(rCone + rMinTorus1, rMinTorus1, 0, 360, 360)

    ri.Translate(0,0,-rMinTorus1)

    ri.Torus(rCone + rMinTorus1 + rMinTorus2, rMinTorus2, 0, 360, 360)
    ri.Translate(0, 0, -hCylinder2)
    ri.Cylinder(rCone + rMinTorus1, 0, hCylinder2, 360)
    ri.Cylinder(rCone + rMinTorus1 + 2*rMinTorus2, 0, hCylinder2, 360)
    ri.Torus(rCone + rMinTorus1 + rMinTorus2, rMinTorus2, 0, 360, 360)

    ri.AttributeEnd()

    #-------------------------Soil------------------------------------
    
    ri.AttributeBegin()

    ri.Attribute('displacementbound', 
    {
        'sphere' : [1],
        'coordinatesystem' : ['shader']
    })

    ri.Pattern('soilShader','soilShader',
    {
        #'color cin' : [0.1,0.02,0.01]
        'color cin' : [0.243*0.5,0.173*0.5,0.157*0.5]
    })

    ri.Displace('PxrDisplace', 'myDisp',
    {
        'float dispAmount' : [2],
        'reference float dispScalar' : ['soilShader:dispOut']
    })

    ri.Bxdf('PxrSurface','soil',
    {
        'reference color diffuseColor' : ['soilShader:cout'],
        'int diffuseDoubleSided' : [1],
        'float subsurfaceGain' : [0.3],
        'color subsurfaceColor' : [0.001,0.001,0.001],
        'float diffuseRoughness' : [0.7],
        'int specularFresnelMode' : [0],
        'float specularFresnelShape' : [10.0],
        'color specularFaceColor' : [1.0,1.0,1.0],
        'color specularEdgeColor' : [1.0,1.0,1.0],
        'float specularRoughness' : [0.01]
    })

    ri.Disk(-0.2, rCone, 360)
    ri.AttributeEnd()

    ri.TransformEnd();
    ri.WorldEnd()
    ri.End()

#------------------------------MAIN-------------------------------------
if __name__ == '__main__':
    checkAndCompileShader('flowerPotShader')
    checkAndCompileShader('soilShader')
    checkAndCompileShader('groundPlaneShader')
    renderingRoutine('flowerPot.rib')