# RendermanProject

MSc Rendering project: the task was to procedurally model and shade an object using the python renderman API. My object was a ceramic flowerpot. The final renders are below:

![flowerPot1](https://github.com/BenCarey88/RendermanProject/blob/master/FlowerPot1.png)

![flowerPot2](https://github.com/BenCarey88/RendermanProject/blob/master/FlowerPot2.png)

To run the code, you need to first run flowerPot.py in python to generate the rib file and oso versions of the osl shaders, then render the files with Renderman, which can be done with the following commands in the terminal:

python flowerPot.py

prman flowerPot.rib

Currently, the code is set up to generate the second of these two images. To switch to the first angle, there are commented instructions in the flowerPot.py file under the 'move everything back from camera' section.

