# Image compression
#
# You'll need Python 2.7 and must install these packages:
#
#   scipy, numpy
#
# You can run this *only* on PNM images, which the netpbm library is used for.
#
# You can also display a PNM image using the netpbm library as, for example:
#
#   python netpbm.py images/cortex.pnm


import sys, os, math, time, netpbm, struct
import numpy as np


# Text at the beginning of the compressed file, to identify it


headerText = 'my compressed image - v1.0'



# Compress an image


def compress( inputFile, outputFile ):

  # Read the input file into a numpy array of 8-bit values
  #
  # The img.shape is a 3-type with rows,columns,channels, where
  # channels is the number of component in each pixel.  The img.dtype
  # is 'uint8', meaning that each component is an 8-bit unsigned
  # integer.

  img = netpbm.imread( inputFile ).astype('uint8')

  #to find compressed sizes of jpg and png
  #from PIL import Image
  #img1 = Image.open(inputFile)
  #img1.load()
  #img = np.asarray(img1, dtype='uint8')
  
  # Compress the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO FILL THE 'outputBytes' ARRAY.
  #
  # Note that single-channel images will have a 'shape' with only two
  # components: the y dimensions and the x dimension.  So you will
  # have to detect this and set the number of channels accordingly.
  # Furthermore, single-channel images must be indexed as img[y,x]
  # instead of img[y,x,1].  You'll need two pieces of similar code:
  # one piece for the single-channel case and one piece for the
  # multi-channel case.

  #initialise dictionary
  val_ls = map(str, range(-255, 256))
  count = len(val_ls)
  LZW_dict = dict(zip(val_ls, range(512)))
  s = ""

  startTime = time.time()
 
  outputBytes = bytearray()

  diff_arr = []

  #single channel image
  if (len(img.shape) == 2):
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        #predictive encoding
        if (y == 0):
          val = img[y,x]
        else:
          val = img[y,x] - img[y-1,x]
        val = str(val)
        diff_arr.append(val)

  #multi-channel image
  else:
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        for c in range(img.shape[2]):
          #predictive encoding
          if (y == 0):
            val = img[y,x,c]
          else:
            val = img[y,x,c] - img[y-1,x,c]
          val = str(val)
          diff_arr.append(val)

  #first pixel exists in dictionary
  s += diff_arr[0]
  for i in range(1, len(diff_arr)):
    #LZW compression
    #LZW_dict keys - subsequence, string
    #LZW_dict values - index, int
    tmp_s = s + "," + diff_arr[i]
    if tmp_s in LZW_dict:
      s = tmp_s
    else:
      #convert integer to bytes
      val_b = struct.pack(">H", LZW_dict[s])
      #append bytes to output array
      outputBytes += val_b
      #append to dictionary if not full
      if (count <= 65535):
        LZW_dict[tmp_s] = count
        count += 1
      s = diff_arr[i]
  #output last byte
  val_b = struct.pack(">H", LZW_dict[s])
  #append bytes to output array
  outputBytes += val_b
      
  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.
  
  outputFile.write( '%s\n'       % headerText )
  outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]) )
  outputFile.write( outputBytes )

  # Print information about the compression
  
  inSize  = img.shape[0] * img.shape[1] * img.shape[2]
  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )
  


# Uncompress an image

def uncompress( inputFile, outputFile ):

  # Check that it's a known file

  if inputFile.readline() != headerText + '\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)
    
  # Read the rows, columns, and channels.  

  rows, columns, channels = [ int(x) for x in inputFile.readline().split() ]

  # Read the raw bytes.

  inputBytes = bytearray(inputFile.read())

  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  startTime = time.time()

  img = np.empty( [rows,columns,channels], dtype=np.uint8 )

  #convert byte values back to decimal
  byteIter = []
  for i in range(0, len(inputBytes), 2):
    val = struct.unpack(">H", inputBytes[i:i+2])[0]
    byteIter.append(val)
  byteIter = iter(byteIter)
  
  img_data = np.zeros((rows*columns*channels))
  #initial setup and dictionary
  val_ls = map(str, range(-255, 256))
  count = len(val_ls)
  LZW_dict = dict(zip(range(512), val_ls))
  s = LZW_dict[byteIter.next()]
  s_int = int(s)
  img_data[0] = s_int
  pos = 1

  while True:
    try:
      #next code
      val = byteIter.next()
      #dictionary look up of next code
      if val in LZW_dict:
        t = LZW_dict[val]
      #next code not found in dictionary
      else:
        #s is a string sequence of numbers
        if ',' in s:
          t = s + "," + s.split(',')[0]
        #s is a string of a number
        else:
          t = s + "," + s
        
      #t is a string sequence of numbers
      if ',' in t:
        t_arr = t.split(',')
        for item in t_arr:
          img_data[pos] = int(item)
          pos += 1
        LZW_dict[count] = s + "," + t_arr[0]
      #t is a string of a number
      else:
        t_int = int(t)
        img_data[pos] = t_int
        LZW_dict[count] = s + "," + t
        pos += 1
      
      count += 1
      s = t
      
    #all codes have been processed
    except:
      break
  
  img_iter = iter(img_data)

  #convert to img array
  for y in range(rows):
    for x in range(columns):
      for c in range(channels):
        if (y == 0):
          img[y,x,c] = img_iter.next()
        else:
          img[y,x,c] = img_iter.next() + img[y-1,x,c]

  endTime = time.time()

  # Output the image

  netpbm.imsave( outputFile, img )

  sys.stderr.write( 'Uncompression time: %.2f seconds\n' % (endTime - startTime) )
  
# The command line is 
#
#   main.py {flag} {input image filename} {output image filename}
#
# where {flag} is one of 'c' or 'u' for compress or uncompress and
# either filename can be '-' for standard input or standard output.


if len(sys.argv) < 4:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

# Get input file
 
if sys.argv[2] == '-':
  inputFile = sys.stdin
else:
  try:
    inputFile = open( sys.argv[2], 'rb' )
  except:
    sys.stderr.write( "Could not open input file '%s'.\n" % sys.argv[2] )
    sys.exit(1)

# Get output file

if sys.argv[3] == '-':
  outputFile = sys.stdout
else:
  try:
    outputFile = open( sys.argv[3], 'wb' )
  except:
    sys.stderr.write( "Could not open output file '%s'.\n" % sys.argv[3] )
    sys.exit(1)

# Run the algorithm

if sys.argv[1] == 'c':
  compress( inputFile, outputFile )
elif sys.argv[1] == 'u':
  uncompress( inputFile, outputFile )
else:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)
