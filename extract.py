from PIL import Image
import hashlib
import time
import sys

files = list(sys.argv)

files.pop(0)

for file in files:

  print file
  im = Image.open(file)
  im = im.convert("P")
  im2 = Image.new("P",im.size,255)
  im = im.convert("P")

  temp = {}

  for x in range(im.size[1]):
    for y in range(im.size[0]):
      pix = im.getpixel((y,x))
      temp[pix] = pix
      if pix <60: # these are the numbers to get
        im2.putpixel((y,x),0)

  inletter = False
  foundletter=False
  start = 0
  end = 0

  letters = []

  for y in range(im2.size[0]): # slice across
    for x in range(im2.size[1]): # slice down
      pix = im2.getpixel((y,x))
      if pix != 255:
        inletter = True
    if foundletter == False and inletter == True:
      foundletter = True
      start = y

    if foundletter == True and inletter == False:
      foundletter = False
      end = y
      letters.append((start,end))

    inletter=False

  count = 0

  for letter in letters:
    m = hashlib.md5()
    im3 = im2.crop(( letter[0] , 0, letter[1],im2.size[1] ))
    m.update("%s%s"%(time.time(),count))
    im3.save("./cropped/%s.gif"%(m.hexdigest()))
    count += 1
