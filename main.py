import numpy as np
import cv2 
from queue import MyQueue
import util
import logging

class Engine():
  def __init__(self,capForGoal,capForRecording):

    self.capGoal = capForGoal
    self.capRec = capForRecording
    self.limit = 5*20 # 5 means before sec
    self.storePrev = MyQueue(limit=self.limit)
    self.storeNext = MyQueue(limit=self.limit)
    self.storePrevRec = MyQueue(limit=self.limit)
    self.storeNextRec = MyQueue(limit=self.limit)
    self.isStartNext = False
    self.framenum = 0
    self.fpsGoal = capForGoal.get(cv2.CAP_PROP_FPS)
    self.fpsRec = capForRecording.get(cv2.CAP_PROP_FPS)
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    pass
  def saveVideo(self):
    
    self.isStartNext = False
    #todo
    self.storePrev.queue.extend(self.storeNext.queue)
    image_array_goal = self.storePrev.queue
    self.storePrevRec.queue.extend(self.storeNextRec.queue)
    image_array_rec = self.storePrevRec.queue
    util.saveImageAsVideo(image_array_goal,"goal.avi",fps=self.fpsGoal)
    util.saveImageAsVideo(image_array_rec,"rec.avi",fps=self.fpsRec)
    
    self.storeNext.queue.clear()
    self.storePrev.queue.clear()
    self.storeNextRec.queue.clear()
    self.storePrevRec.queue.clear()
    
    self.framenum = 0
    pass
  def run(self):
    framepos = 0
    capture = self.capGoal
    captureRec = self.capRec
    res,frame = capture.read()
    res,frameRec = captureRec.read()
    oldframe = None
    diff = None
    while(res):
      res,frame = capture.read()
      #sync two video based on frameRate
      frameNumRec = capture.get(cv2.CAP_PROP_POS_FRAMES) * self.fpsRec//self.fpsGoal
      captureRec.set(cv2.CAP_PROP_POS_FRAMES,frameNumRec)

      res,frameRec = captureRec.read()
      if self.isStartNext == True:
        if frame is None:
          self.saveVideo()
          continue
        self.storeNext.insertItem(frame.copy())
        if(frameRec is not None):
          self.storeNextRec.insertItem(frameRec.copy())
        if (len(self.storeNext.getAllItems())> self.limit):
          self.saveVideo()
        continue
      else:
        if frame is None:
          break
        self.storePrev.insertItem(frame.copy())
        self.storePrevRec.insertItem(frameRec.copy())

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
              # if(sign>20):
              #   cv2.circle(frame,center,radius,(0,255,0),2)

        # cv2.imshow("diff",dilation)
        oldframe = frame
      
      if(sign>15):
        h,w,_ = frame.shape
        cv2.putText(frame,"Goal...",(w//2,h//2),cv2.FONT_HERSHEY_SIMPLEX,2,(255,0,0),2,cv2.LINE_AA)
        self.isStartNext = True
        self.framenum = framepos

      cv2.imshow("Image",frame)
      cv2.imshow("ImageRec",frameRec)

      if cv2.waitKey(20)&0xFF == ord('q'):
        break
      elif cv2.waitKey(20)& 0xFF == ord('n'):
        continue
      else:
        pass

    if(self.isStartNext == True):
      self.saveVideo()

capForGoal = cv2.VideoCapture('testVideos/1goal.mp4')
capForGoal.set(cv2.CAP_PROP_POS_FRAMES,700)
capForRecording = cv2.VideoCapture('testVideos/1.mp4')
# capForRecording.set(cv2.CAP_PROP_POS_FRAMES,700)

engine = Engine(capForGoal,capForRecording)
try:
  engine.run()
except:
  logging.warning("engine failed")
