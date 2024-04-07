#!/usr/bin/python3

#importing image object from PIL 
import math
# Import Pillow module
# From help('PIL')
# enter pyhton3 in terminal to enter shell, q to quit or exit()
from PIL import Image, ImageDraw, PSDraw


  
w, h = 220, 190
  
# creating new Image object 
img = Image.new("RGB", (w, h)) 
  
# create  rectangleimage 
img1 = ImageDraw.Draw(img)   
img1(fill ="# 800080")
img.show() 

