#convert all tif to jpgs
#install libraries first
#!pip install pyrsgis #(for collab -> uncomment this line)
import numpy as np
import glob
import cv2 
from pyrsgis import raster

for i in range(1): #put number of images here
    images = glob.glob('*.tif') #path of images #if possible put in same folder and execute. might cause some error.
    for image in images:
            temp=image.split(".")[0]
            print(temp)
            new_name=temp+".jpg"
            ds2, chip = raster.read(image,bands=[1,2,3])
            t1 = (chip[0]).astype(np.uint16)
            t2 = (chip[1]).astype(np.uint16)
            t3 = (chip[2]).astype(np.uint16)
            tdstck = np.dstack((t3,t2,t1))
            cv2.imwrite(new_name,tdstck)