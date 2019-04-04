import prman
import sys,os.path,subprocess
ri = prman.Ri()

def checkAndCompileShader(shader) :
        #.oso is the filetype that rib files read, but we write in osl
        #so this if statement checks if either there is no .oso file
        #or if the .osl file has been modified more recently than the .oso
        #in either case we need to create a new .oso file from the .osl (by command 'oslc shader.osl')
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

    #Move everything back from camera
    ri.Translate(0,0,10)
    ri.Translate(0,-1,0)
    ri.Rotate(-20,1,0,0)

    ri.WorldBegin()

    #Rect Light - NEEDS REPOSITIONING
    ri.AttributeBegin()
    ri.Translate(-2,2,-2)
    ri.Rotate(45,1,0,0)
    ri.Rotate(45,0,1,0)
    ri.Light("PxrRectLight","rectLight", {"float exposure" : [5]})
    ri.AttributeEnd()

    #Dome Light
    ri.AttributeBegin()
    ri.Rotate(-90,1,0,0)
    ri.Rotate(10,0,0,1)
    ri.Light("PxrDomeLight","domeLight",{"float exposure" : [0], "string lightColorMap" : ["envMap.tx"]})
    ri.AttributeEnd()

    #Ground Plane
    planePoints = [ -6, 0, 0,  
                    6, 0, 0, 
                    -6, 0, 10,
                    6, 0, 10 ]
    ri.AttributeBegin()
    ri.Translate(0,-3,0)
    ri.Patch("bilinear", {"P" : planePoints})
    ri.AttributeEnd()

    #Flower Pot
    ri.AttributeBegin()

    ri.Pattern('flowerPotShader','flowerPotShader',
    {
        'color cin' : [1,0,0]
    })

    ri.Bxdf('PxrSurface', 'plastic', 
    { 
        'reference color diffuseColor' : ['flowerPotShader:cout'],
        'reference color specularFaceColor' : ['flowerPotShader:specOut'],
        'float specularRoughness' : [0.8],
        'int diffuseDoubleSided' : [1],
    })

    #switch to pxrDisney - but can only attach things to color and normal here

    """ri.Bxdf('PxrDisney','bxdf',
    { 
        'reference color baseColor' : ['flowerPotShader:cout'] ,
    })"""

    ri.Translate(-2,0,0)
    ri.Translate(0,0,5)
    ri.Rotate(90,1,0,0)

    rCone = 1.6
    rMinTorus1 = 0.1
    hCylinder1 = 0.4
    rMinTorus2 = 0.1
    hCylinder2 = 0.05

    ri.Cone(10,rCone,360)
            
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

    ri.WorldEnd()
    ri.End()

if __name__ == '__main__':
    checkAndCompileShader('flowerPotShader')
    renderingRoutine('flowerPot.rib')