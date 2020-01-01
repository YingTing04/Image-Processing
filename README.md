# Image-Processing
CISC 457 Image Processing assignments completed at Queen's University in Fall 2019

## A1
- Modifies brightness and contrast and scale of image and performs histogram equalization
- To change the image to be processed, modify `imgFilename`
- To adjust brightness and contrast, use mouse left button
- To perform histogram equalization, press `h`
- To perform scaling, use mouse right button

## A2
- Removes image gridlines using Fourier Transform

## A3
- Performs LZW compression and decompression of images
- To create a compressed image, cortex.cmp, enter `python main.py c images/cortex.pnm cortex.cmp`
- To decompress an image, enter `python main.py u cortex.cmp decompressed.pnm`
- Compression and decompression statistics can be found below

|  Image Name  | Compression Time | Decompression Time | Compression Ratio |
| ------------ | ---------------- | ------------------ | ----------------- |
|  cortex.pnm  | 2.87 | 2.18 | 6.49 |
| barbara.pnm  | 1.20 | 1.02 | 1.94 |
|  crest.pnm   | 15.53 | 5.62 | 19.91 |
| mandrill.pnm | 1.23 | 1.10 | 1.86 |
|  noise.pnm   | 1.54 | 1.82 | 0.89 |
