import cv2
import numpy as np
import glob
import logging
def saveImageAsVideo(img_array,path='output.avi',size=(300,200),fps = 15):
  h,w,_ = img_array[0].shape
  size = (w,h)
  logging.warning(str(w) + " + " + str(h))
  try:
    out = cv2.VideoWriter(path,cv2.VideoWriter_fourcc(*'MJPG'), fps , size)
    for i in range(len(img_array)):
        out.write(img_array[i])
  except:
    logging.warning("writing failed")
  out.release()
