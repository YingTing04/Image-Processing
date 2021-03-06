# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow
#
# Note that file loading and saving (with 'l' and 's') do not work on
# Mac OSX, so you will have to change 'imgFilename' below, instead, if
# you want to work with different images.
#
# Note that images, when loaded, are converted to the YCbCr
# colourspace, and that you should manipulate only the Y component of
# each pixel when doing intensity changes.


import sys, os, numpy, math

try: # Pillow
  from PIL import Image
except:
  print 'Error: Pillow has not been installed.'
  sys.exit(0)

try: # PyOpenGL
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print 'Error: PyOpenGL has not been installed.'
  sys.exit(0)



# Globals

windowWidth  = 600 # window dimensions
windowHeight =  800

localHistoRadius = 5  # distance within which to apply local histogram equalization



# Current image

imgDir      = 'images'
imgFilename = 'mandrill.png'

currentImage = Image.open( os.path.join( imgDir, imgFilename ) ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )
tempImage    = None



# File dialog (doesn't work on Mac OSX)

if sys.platform != 'darwin':
  import Tkinter, tkFileDialog
  root = Tkinter.Tk()
  root.withdraw()



# Apply brightness and contrast to tempImage and store in
# currentImage.  The brightness and constrast changes are always made
# on tempImage, which stores the image when the left mouse button was
# first pressed, and are stored in currentImage, so that the user can
# see the changes immediately.  As long as left mouse button is held
# down, tempImage will not change.

def applyBrightnessAndContrast( brightness, contrast ):

  width  = currentImage.size[0]
  height = currentImage.size[1]

  srcPixels = tempImage.load()
  dstPixels = currentImage.load()
  
  # YOUR CODE HERE
  for i in range(width):
    for j in range(height):
        #obtain new intensity after adjusted contrast and brightness
        k = contrast * srcPixels[i,j][0] + brightness
        
        #put new intensity into destination pixel
        tmp = list(dstPixels[i,j])
        tmp[0] = int(round(k))
        dstPixels[i,j] = tuple(tmp)
  print 'adjust brightness = %f, contrast = %f' % (brightness,contrast)

  

# Perform local histogram equalization on the current image using the given radius.

def performHistoEqualization( radius ):
 
  pixels = currentImage.load()
  width  = currentImage.size[0]
  height = currentImage.size[1]

  # YOUR CODE HERE
  #make a copy of original image
  tmpImage = currentImage.copy()
  pixels_copy = tmpImage.load()
    
  #size of neighbourhood
  n = (2 * radius + 1) * (2 * radius + 1)

  for i in range(width):
    for j in range(height):
        #obtain start and end bounds of neighbourhood
        start_x = i - radius
        end_x = i + radius
        start_y = j - radius
        end_y = j + radius
        
        #moderate values that are out of bounds
        if (start_x < 0):
            start_x = 0
        if (start_y < 0):
            start_y = 0
        if (end_x > width - 1):
            end_x = width - 1
        if (end_y > height - 1):
            end_y = height - 1
        
        number = 0
        
        for a in range(start_x, end_x + 1):
            for b in range(start_y, end_y + 1):
                #find number of neighbouring pixels whose value is smaller than target pixel
                if pixels[a,b][0] <= pixels[i,j][0]:
                    number += 1
                
        new_pixel_val = (256/ n)* number + 0 - 1
        
        #put new intensity into pixels_copy
        tmp = list(pixels_copy[i,j])
        tmp[0] = int(round(new_pixel_val))
        pixels_copy[i,j] = tuple(tmp)
        
  #copy the temporary image to the original image      
  for i in range(width):
    for j in range(height):
      pixels[i,j] = pixels_copy[i,j]
      
  print 'perform local histogram equalization with radius %d' % radius



# Scale the tempImage by the given factor and store it in
# currentImage.  Use backward projection.  This is called when the
# mouse is moved with the right button held down.

def scaleImage( factor ):

  width  = currentImage.size[0]
  height = currentImage.size[1]

  srcPixels = tempImage.load()
  dstPixels = currentImage.load()

  # YOUR CODE HERE
  T = numpy.matrix([[factor, 0], [0, factor]])
  #obtain inverse matrix
  T_inv = numpy.linalg.inv(T)

  for i in range(width):
    for j in range(height):
        #using backward projection to obtain coordinates in original image
        new_coords = numpy.matrix([[i],[j]])
        original_coords = numpy.matmul(T_inv, new_coords)
        
        x = original_coords[0][0]
        y = original_coords[1][0]
        
        X = int(numpy.floor(x))
        Y = int(numpy.floor(y))
        
        _X = X + 1
        _Y = Y + 1
        
        #moderate values that are out of bounds
        if (X > width - 2):
            X = width - 1
            _X = width - 1
        elif (X < 0):
            X = 0
            _X = 0
        
        if (Y > height - 2):
            Y = height - 1
            _Y = height - 1
        elif (Y < 0):
            Y = 0
            _Y = 0
        
        #using bilinear interpolation
        #put new value of tuple into dstPixels
        alpha = x - X
        beta = y - Y
        
        tmp = list(dstPixels[i,j])
        for l in range(3):
            val = (1-alpha) * (1-beta) * srcPixels[X,Y][l] + (alpha) * (1-beta) * srcPixels[_X,Y][l] + (1-alpha) * (beta) * srcPixels[X,_Y][l] + (alpha) * (beta) * srcPixels[_X,_Y][l] 
            tmp[l] = int(val)
        
        dstPixels[i,j] = tuple(tmp)
        
  print 'scale image by %f' % factor

  

# Set up the display and draw the current image

def display():

  # Clear window

  glClearColor ( 1, 1, 1, 0 )
  glClear( GL_COLOR_BUFFER_BIT )

  # rebuild the image

  img = currentImage.convert( 'RGB' )

  width  = img.size[0]
  height = img.size[1]

  # Find where to position lower-left corner of image

  baseX = (windowWidth-width)/2
  baseY = (windowHeight-height)/2

  glWindowPos2i( baseX, baseY )

  # Get pixels and draw

  imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

  glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

  glutSwapBuffers()


  
# Handle keyboard input

def keyboard( key, x, y ):

  global localHistoRadius

  if key == '\033': # ESC = exit
    sys.exit(0)

  elif key == 'l':
    if sys.platform != 'darwin':
      path = tkFileDialog.askopenfilename( initialdir = imgDir )
      if path:
        loadImage( path )

  elif key == 's':
    if sys.platform != 'darwin':
      outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
      if outputPath:
        saveImage( outputPath )

  elif key == 'h':
    performHistoEqualization( localHistoRadius )

  elif key in ['+','=']:
    localHistoRadius = localHistoRadius + 1
    print 'radius =', localHistoRadius

  elif key in ['-','_']:
    localHistoRadius = localHistoRadius - 1
    if localHistoRadius < 1:
      localHistoRadius = 1
    print 'radius =', localHistoRadius

  else:
    print 'key =', key    # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

  glutPostRedisplay()



# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.


def loadImage( path ):

  global currentImage

  currentImage = Image.open( path ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )


def saveImage( path ):

  global currentImage

  currentImage.transpose( Image.FLIP_TOP_BOTTOM ).convert('RGB').save( path )
  


# Handle window reshape


def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glutPostRedisplay()



# Mouse state on initial click

button = None
initX = 0
initY = 0



# Handle mouse click/release

def mouse( btn, state, x, y ):

  global button, initX, initY, tempImage

  if state == GLUT_DOWN:
    tempImage = currentImage.copy()
    button = btn
    initX = x
    initY = y
  elif state == GLUT_UP:
    tempImage = None
    button = None

  glutPostRedisplay()

  

# Handle mouse motion

def motion( x, y ):

  if button == GLUT_LEFT_BUTTON:

    diffX = x - initX
    diffY = y - initY

    applyBrightnessAndContrast( 255 * diffX/float(windowWidth), 1 + diffY/float(windowHeight) )

  elif button == GLUT_RIGHT_BUTTON:

    initPosX = initX - float(windowWidth)/2.0
    initPosY = initY - float(windowHeight)/2.0
    initDist = math.sqrt( initPosX*initPosX + initPosY*initPosY )
    if initDist == 0:
      initDist = 1

    newPosX = x - float(windowWidth)/2.0
    newPosY = y - float(windowHeight)/2.0
    newDist = math.sqrt( newPosX*newPosX + newPosY*newPosY )

    scaleImage( newDist / initDist )

  glutPostRedisplay()
  


# Run OpenGL

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )

glutMainLoop()




