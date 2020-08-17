import numpy as np
import cv2 

def getGoalFrameNumber(capture):
  framepos = 1
  capture.set(cv2.CAP_PROP_POS_FRAMES,framepos)
  res,frame = capture.read()
  oldframe = None
  diff = None
  while(res):
    res,frame = capture.read()
    framepos += 1
    hsv_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    lower_red = np.array([70,30,70])
    upper_red = np.array([230,255,255])
    mask = cv2.inRange(hsv_frame,lower_red,upper_red)
    resImg = cv2.bitwise_and(frame,frame,mask=mask)
    sign = 0
    if oldframe is None:
      oldframe = frame
      pass
    else:
      gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
      gray_frame = cv2.GaussianBlur(gray_frame,(15,15),0)
      gray_old = cv2.cvtColor(oldframe,cv2.COLOR_BGR2GRAY)
      gray_old = cv2.GaussianBlur(gray_old,(15,15),0)
      Conv_hsv_Gray = cv2.subtract(gray_frame,gray_old)
      # color the mask red
      blur = cv2.GaussianBlur(Conv_hsv_Gray,(5,5),0)
      ret, th = cv2.threshold(blur, 30, 255,cv2.THRESH_BINARY)

      #deliation
      kernel = np.ones((5,5),np.uint8)
      dilation = cv2.dilate(th,kernel,iterations = 1)
      # gray_blurred = cv2.blur(dilation, (3, 3)) 

      #detecting circle
      contours,hierarchy = cv2.findContours(dilation,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
      cnt = contours
      sign = 0
      if(cnt is not None):
        for i in cnt:
          (x,y),radius = cv2.minEnclosingCircle(i)
          center = (int(x),int(y))
          radius = int(radius)
          if(3.14*radius*radius<10000 and 3.14*radius*radius>500):
            rect = cv2.boundingRect(i)
            sign += 1
            if(sign>20):
              cv2.circle(frame,center,radius,(0,255,0),2)


      # cv2.imshow("diff",dilation)
      oldframe = frame
    
    cv2.imshow("Image",frame)
    if(sign>15):
      #goal happens
      return framepos

    if cv2.waitKey(50)&0xFF == ord('q'):
      break
    elif cv2.waitKey(50)& 0xFF == ord('n'):
      continue
    else:
      pass
