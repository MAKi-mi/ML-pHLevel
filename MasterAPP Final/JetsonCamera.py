import cv2 as cv2
import time


class JetCam:

    gstreamer_pipeline =(
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)4608, height=(int)2592, "
        "format=(string)NV12, framerate=(fraction)14/1 ! "
        "nvvidconv flip-method=0 ! "
        "video/x-raw, width=(int)4608, height=(int)2592, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
    )
    
    cam = None
    image = None

    def __init__(self):
        print("Opening Camera")
        self.cam  = cv2.VideoCapture(self.gstreamer_pipeline,cv2.CAP_GSTREAMER)
        if self.cam.isOpen():
            print("Camera opened sucessfully")
        else :
            print("Could not open camera")
    
    def capture(self):
        result,self.image = self.cam.read()
        if result:
            return self.image
        else:
            self.image = None
            print("No image detected. Please! try again")

    def saveLastCapturedImage(self,filename):
        if self.image is not None:
            cv2.imwrite(filename, self.image) 
        else:
            pass
            

    def saveImage(self,filename,img=None):
        if img is not None:
            cv2.imwrite(filename,img)

    def __del__(self):
        self.cam.release()
        print('Destroying JetCam. Camera released')
 

if __name__ == "__main__":

    start_time = time.process_time() 
    a= JetCam()
    end_time = time.process_time() 
    print("Jetcam create time: ",end_time - start_time, "s")
    
    start_time = time.process_time() 
    a.capture()
    end_time = time.process_time() 
    print("Jetcam image capture time: ",end_time - start_time, "s")

    start_time = time.process_time()
    a.saveLastCapturedImage("z.png")
    end_time = time.process_time()
    print("Jetcam image save time: ",end_time - start_time, "s")
    


