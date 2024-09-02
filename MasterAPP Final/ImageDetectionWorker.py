
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *

import jetson_inference
import jetson_utils

from IMX708Focuser import Focuser

import math
import os
import time

import cv2

import numpy as np


class CapturingImagesWorker(QObject):

    onWorkerFinished = pyqtSignal()
    onValidImageCaptured = pyqtSignal(QImage)
    onInferenceFinished = pyqtSignal(list)
    onNoValidImage = pyqtSignal()

    brightness = 75

    def __init__(self,captureFPS =6):
        super().__init__()

        #Load Model
        self.net = jetson_inference.imageNet(model="model/googlenet_mod.onnx", labels="model/labels.txt", input_blob="input_0", output_blob="output_0")

        #Start Camera
        self.cudaCamera = jetson_utils.videoSource("csi://0", argv=["--framerate=14","--width=4608","--height 2592", "--flip-method=vertical-flip"])
        
        #turn On Backlight
        os.system("python3.8 Backlight.py 1 " + str(self.brightness)) 


        #Dummy capture so it will start capturing
        self.cudaCamera.Capture()
        self.cudaCamera.Capture()
        self.cudaCamera.Capture()
        self.cudaCamera.Capture()
        
        #Set focus points
        self.cameraFocus = Focuser(6)
        self.cameraFocus.reset(Focuser.OPT_FOCUS)
        self.cameraFocus.set(Focuser.OPT_FOCUS, 650)


        self.numberOfConsecutiveValidFramesLimit = 15
        self.numberOfConsecutiveInvalidFramesLimit = 3

        self.numberOfConsecutiveValidFrames = 0
        self.numberOfConsecutiveInvalidFrames = 0

        self.loopTimer = QTimer()
        self.loopTimer.setInterval(int(1000/captureFPS))
        self.loopTimer.timeout.connect(self.checkForValidImage)
        self.loopTimer.start()

        self.checkInProgress = False
    def __del__(self):
        #turn Off Backlight
        os.system("python3.8 Backlight.py 0 0")
    
    def openCVColorDetection(self,numpyImage, crop = False, contourAreaMin = 3000, contourAreaMax = 13000 , debugMode = 0):
        
        #gray =  numpyImage.mean(axis=(0,1), dtype=np.float32) # gray world
        gray = np.median(numpyImage, axis=(0,1)).astype(np.float32) # majority vote
        balanced = (numpyImage / gray) * 0.8  # some moderate scaling so it's not "overexposed"

        hsv = cv2.cvtColor(balanced, cv2.COLOR_BGR2HSV)
        H,S,V = cv2.split(hsv)
        # squares nicely visible

        if debugMode:
            cv2.namedWindow('White balanced', cv2.WINDOW_KEEPRATIO)
            cv2.imshow('White balanced', S) 
            cv2.resizeWindow('White balanced', 1400, 700) 
            cv2.waitKey(0) 
            cv2.destroyAllWindows() 

        # print(S.min(), S.max()) # 0.0 0.9125462
        mask = (S >= 0.3)
        mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, kernel=None, iterations=5).astype(bool)

        (unFilteredcontours, _) = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        #Filter contours to elimate false detections
        contours = []
        for i in unFilteredcontours:
            
            contourArea = cv2.contourArea(i)
            if contourArea > contourAreaMin and contourArea < contourAreaMax:
                contours.append(i)

            
        #If the number of detected contour is not 4 (number of colors in the strip)
        #terminate function as it would result in wrongly cropped image
        if len(contours) < 3 or len(contours) > 4:
            print('Prefiltered Contour Area:')
            for i in unFilteredcontours:
                print(cv2.contourArea(i))
            print('Filtered Contour Area:')
            for i in contours:
                print(cv2.contourArea(i))
            return None

        #Terminate program early if the number of validframes has not been reach
        #no need to waste processing power if images is not used
        if crop == False:
            return []

        hull = cv2.convexHull(np.concatenate(contours))
        rrect = cv2.minAreaRect(hull)


        # visualization
        canvas = numpyImage.copy()
        cv2.drawContours(image=canvas, contours=contours, contourIdx=-1, color=(255,255,0), thickness=7)
        rrect_points = cv2.boxPoints(rrect).round().astype(int)

        if debugMode:
            cv2.polylines(canvas, [rrect_points], isClosed=True, color=(0,255,255), thickness=3)
            cv2.namedWindow('Bounding Rectangle', cv2.WINDOW_KEEPRATIO)
            cv2.imshow('Bounding Rectangle', canvas) 
            cv2.resizeWindow('Bounding Rectangle', 1400, 700) 
            cv2.waitKey(0) 
            cv2.destroyAllWindows() 

        #crop first to the nearest nonrotated box to reduce computational load when doing image rotate

        #Obtain first crop points
        listXCoordinates = [rrect_points[0][0],rrect_points[1][0],rrect_points[2][0],rrect_points[3][0]]
        listYCoordinates = [rrect_points[0][1],rrect_points[1][1],rrect_points[2][1],rrect_points[3][1]]
        xStart = min(listXCoordinates)
        xEnd   = max(listXCoordinates)
        yStart = min(listYCoordinates)
        yEnd   = max(listYCoordinates)

        if xStart < 0:
            xStart = 0
        if yStart < 0:
            yStart = 0

        #Obtain bottom-left and bottom-right coordinates
        s = rrect_points.sum(axis = 1)
        stripTopLeft= rrect_points[np.argmin(s)]
        stripBottomRight = rrect_points[np.argmax(s)]

        diff = np.diff(rrect_points, axis = 1)
        stripTopRight = rrect_points[np.argmin(diff)]
        stripBottomLeft = rrect_points[np.argmax(diff)]

        if debugMode:
            print(xStart,xEnd,yStart,yEnd)
            print('BottomLeft',stripBottomLeft, 'bottomRight', stripBottomRight)

        croppedCanvas = numpyImage[yStart:yEnd, xStart:xEnd]

        if debugMode:
            cv2.imshow('Cropped', croppedCanvas) 
            cv2.waitKey(0) 
            cv2.destroyAllWindows() 

        # Calculate angle
        slope = (stripBottomRight[1]-stripBottomLeft[1])/(stripBottomRight[0]-stripBottomLeft[0])
        angle = (math.atan(abs((slope - 0) / (1 + 0 * slope))) * 180) / math.pi
        # Adjust rotation direction for positive/negative slope
        if slope < 0 :
            angle = angle*-1

        #rotate based on the center
        image_center = tuple(np.array(croppedCanvas.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(croppedCanvas, rot_mat, croppedCanvas.shape[1::-1], flags=cv2.INTER_LINEAR)

        if debugMode:
            cv2.imshow("result",result)
            cv2.waitKey(0) 
            cv2.destroyAllWindows() 


        #Calculate subject height and crop from center
        stripHeight = math.sqrt(((stripBottomLeft[0] - stripTopLeft[0]) ** 2) + ((stripBottomLeft[1] - stripTopLeft[1]) ** 2))/2
        #stripHeight = math.dist(stripBottomLeft, stripTopLeft)  #Only works on python 3.8 or higher
        rotatedImageHeight = result.shape[0]/2
        yStart =  int(rotatedImageHeight-stripHeight)
        yEnd   =  int(rotatedImageHeight+stripHeight)
        result = result[yStart:yEnd, 0:result.shape[1]-1]

        if debugMode:
            cv2.imshow("result",result)
            cv2.waitKey(0) 
            cv2.destroyAllWindows() 

        return result

    def checkForValidImage(self):

        if self.checkInProgress == True:
            return
        else:
            self.checkInProgress = True

        frame = self.captureFrame()
        

        if type(frame) == type(None):
            print('Capture Frame Error: No image detected')
            self.checkInProgress = False
            return
        
        if self.numberOfConsecutiveValidFrames > self.numberOfConsecutiveValidFramesLimit:
            print('Valid Image detected')
            finalFrame = self.openCVColorDetection(frame,True)

            self.numberOfConsecutiveInvalidFrames = 0
            self.numberOfConsecutiveValidFrames   = 0

            if type(finalFrame) == type(None):
                self.checkInProgress = False
                return
            
            im_np = np.array(finalFrame)    
            qtImage = QImage(im_np.data, im_np.shape[1], im_np.shape[0], QImage.Format_RGB888)
            self.onValidImageCaptured.emit(qtImage)

            cudaImage = jetson_utils.cudaFromNumpy(finalFrame)
            jetson_utils.cudaDeviceSynchronize()
            self.startInference(cudaImage)
            # Important to do it like this QImage has a bug wherein 


        else:
            finalFrame = self.openCVColorDetection(frame,False)

            if type(finalFrame) == type(None):
                self.numberOfConsecutiveInvalidFrames = self.numberOfConsecutiveInvalidFrames + 1
                self.numberOfConsecutiveValidFrames = 0

                if self.numberOfConsecutiveInvalidFrames > self.numberOfConsecutiveInvalidFramesLimit:
                    self.numberOfConsecutiveInvalidFrames = 0
                    self.onNoValidImage.emit()
                    print('No Valid Images')
                # else:
                #     print('Invalid Count: ',self.numberOfConsecutiveInvalidFrames)
            else:
                self.numberOfConsecutiveValidFrames = self.numberOfConsecutiveValidFrames + 1
                # print('Valid Count: ', self.numberOfConsecutiveValidFrames)

        self.checkInProgress = False

    def captureFrame(self):
        
        #Capture image
        cudaImg = self.cudaCamera.Capture(format="rgb8")

        if cudaImg is None:
            print("No image detected. Please! try again")
            return None
        
        leftCrop   = 1200 +500
        rightCrop  = 1300 +250
        topCrop    = 875
        bottomCrop = 800


        crop_roi = (leftCrop, topCrop, cudaImg.width - rightCrop, cudaImg.height - bottomCrop)

        croppedCudaImage = jetson_utils.cudaAllocMapped(width=cudaImg.width - leftCrop - rightCrop,
                                            height=cudaImg.height -topCrop - bottomCrop,
                                            format=cudaImg.format)

        jetson_utils.cudaDeviceSynchronize()
        
        jetson_utils.cudaCrop(cudaImg, croppedCudaImage, crop_roi)
        
        jetson_utils.cudaDeviceSynchronize()

        croppedArray = jetson_utils.cudaToNumpy(croppedCudaImage)
        
        jetson_utils.cudaDeviceSynchronize()

        return croppedArray

    def startInference(self,cudaImage):
        # # classify the image
        class_idx, confidence = self.net.Classify(cudaImage)

        # find the object description
        class_desc = self.net.GetClassDesc(class_idx)
        
        # print out the result
        print("image is recognized as '{:s}' (class #{:d}) with {:f}% confidence".format(class_desc, class_idx, confidence * 100))

        self.onInferenceFinished.emit([class_desc,class_idx,confidence * 100])
