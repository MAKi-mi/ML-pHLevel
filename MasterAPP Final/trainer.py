import sys
import cv2 as cv2


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *




from ImageDetectionWorker import CapturingImagesWorker



#startUp the camera


class SavingImagesWorker(QObject):

   finished = pyqtSignal()
   imageSaved = pyqtSignal(list)

   imageDataToSave = None
   filename= None
   fileextension =None
   threadNumber = None

   def __init__(self,QImageData,name,extension,id):
      super().__init__() 

      self.imageDataToSave = QImageData
      self.filename=name
      self.fileextension = extension
      self.threadNumber = id

   def startSaving(self):
      if self.imageDataToSave.save(self.filename + '.' + self.fileextension) == True:
         print("Save successfull. Thread Number: " + str(self.threadNumber) + " File: " + self.filename + '.' + self.fileextension)
         self.imageSaved.emit([True,self.threadNumber])
         
         
      else:
         print("Warning: Save file was not successfull. Thread Number: " + str(self.threadNumber) + " File: " + self.filename + '.' + self.fileextension)
         self.imageSaved.emit([False,self.threadNumber])
         
      self.finished.emit()





class Window(QMainWindow): 


   def __init__(self): 
      super().__init__() 

      self.setWindowTitle("Python ")
      self.UiComponents()
      self.showMaximized()

      # Step 2: Create a QThread object
      self.thread = QThread()
      # Step 3: Create a worker object
      self.worker = CapturingImagesWorker()
      # Step 4: Move worker to the thread
      self.worker.moveToThread(self.thread)
      # Step 5: Connect signals and slots
      #self.thread.started.connect(self.worker.waitForValidImage)

      self.worker.onValidImageCaptured.connect(self.onCapturedImage)
      self.worker.onInferenceFinished.connect(self.onInference)
      self.worker.onNoValidImage.connect(self.resetUiComponents)
      self.worker.onWorkerFinished.connect(self.thread.quit)

      # Step 6: Start the thread
      self.thread.start()


   def UiComponents(self): 

      parentHeight = self.frameGeometry().height()
      parentWidth = self.frameGeometry().width() + 95
      edgePaddingX = int(parentWidth*0.01)
      edgePaddingY = int(parentHeight*0.01)

      # setGeometry(X,Y,WIDTH,HEIGHT)
      self.imageFrame1 = QLabel("PLEASE INSERT STRIP", self) 
      self.imageFrame1.setGeometry(0, 0, parentWidth, parentHeight) 
      #self.imageFrame1.setPixmap()
      self.imageFrame1.setScaledContents(True)
      self.imageFrame1.setStyleSheet("border : 0.5px solid black") 
      self.imageFrame1.setFont(QFont('Arial', 30)) 
      self.imageFrame1.setAlignment(Qt.AlignCenter)

      self.classText = QLabel("SCORE", self)
      self.classText.setGeometry(edgePaddingX, edgePaddingX, int(parentWidth*0.4), int(parentHeight * 0.1)) 
      self.classText.setFont(QFont('Arial', 30)) 
      self.classText.setAlignment(Qt.AlignLeft)
      self.classText.hide()


      self.confidenceText = QLabel("CNFDNCE",self)
      self.confidenceText.setGeometry(edgePaddingX, int(parentHeight * 0.1) + (edgePaddingX*1), int(parentWidth*0.4), int(parentHeight * 0.1)) 
      self.confidenceText.setFont(QFont('Arial', 12)) 
      self.confidenceText.hide()

      # self.categoryText = QLabel("CTGRY",self)
      # self.categoryText.setGeometry(edgePaddingX, int(parentHeight * 0.2) + (edgePaddingX*2), int(parentWidth*0.4), int(parentHeight * 0.1)) 
      # self.categoryText.setFont(QFont('Arial', 12)) 
      # self.categoryText.hide()

      buttonHeight = int(parentHeight * 0.1)

      lineEditWidth = int(parentWidth*0.4)
      self.phLevelLabel = QLineEdit("pH_Level-",self)
      self.phLevelLabel.setGeometry(edgePaddingX, parentHeight-int(buttonHeight*1.5)-edgePaddingY, lineEditWidth, buttonHeight )

      self.captureButton = QPushButton(self)
      self.captureButton.setIcon(QIcon('icons/capture.png'))
      self.captureButton.setIconSize(QSize(buttonHeight, buttonHeight))
      self.captureButton.setToolTip('Start capturing images')
      self.captureButton.setGeometry(parentWidth-buttonHeight-edgePaddingX, parentHeight-int(buttonHeight*1.5)-edgePaddingY, buttonHeight, buttonHeight )
      self.captureButton.setFlat(True)
      self.captureButton.setStyleSheet("QPushButton { background-color: transparent; border: 0px }")
      self.captureButton.clicked.connect(self.onCaptureImageButtonClicked)

      self.saveButton = QPushButton(self)
      self.saveButton.setIcon(QIcon('icons/save.png'))
      self.saveButton.setIconSize(QSize(buttonHeight, buttonHeight))
      self.saveButton.setToolTip('Save Images to file')
      self.saveButton.setGeometry(parentWidth-(buttonHeight*2)-(edgePaddingX*2), parentHeight-int(buttonHeight*1.5)-edgePaddingY, buttonHeight, buttonHeight ) 
      self.saveButton.setFlat(True)
      self.saveButton.setStyleSheet("QPushButton { background-color: transparent; border: 0px }")
      self.saveButton.clicked.connect(self.onSaveImageButtonClicked)

      self.trashButton = QPushButton(self)
      self.trashButton.setIcon(QIcon('icons/trash.png'))
      self.trashButton.setIconSize(QSize(buttonHeight, buttonHeight))
      self.trashButton.setToolTip('Discards current image')
      self.trashButton.setGeometry(parentWidth-(buttonHeight*3)-(edgePaddingX*3), parentHeight-int(buttonHeight*1.5)-edgePaddingY, buttonHeight, buttonHeight ) 
      self.trashButton.setFlat(True)
      self.trashButton.setStyleSheet("QPushButton { background-color: transparent; border: 0px }")
      self.trashButton.clicked.connect(self.onTrashButtonClicked)
      
      self.saveButton.hide()
      self.phLevelLabel.hide()
      self.trashButton.hide()

   #helper Function
   def resetUiComponents(self):
      self.image1 = None
      self.imageFrame1.clear()
      self.imageFrame1.setText("PLEASE INSERT STRIP")
      self.imageFrame1.setFont(QFont('Arial', 30)) 
      self.imageFrame1.setAlignment(Qt.AlignCenter)
      
      self.classText.hide()
      self.confidenceText.hide()

      self.phLevelLabel.setEnabled(True)
      self.captureButton.setEnabled(True)
      self.saveButton.setEnabled(True)
      self.trashButton.setEnabled(True)

      self.trashButton.hide()
      self.phLevelLabel.hide()
      self.saveButton.hide()
      # self.statusText.setText("Ready")

   @pyqtSlot()
   def onCaptureImageButtonClicked(self):

      # self.statusText.setText("Starting Capture...")
      self.captureButton.setEnabled(False)
      self.saveButton.setEnabled(False)
      self.trashButton.setEnabled(False)

   
   @pyqtSlot(QImage)
   def onCapturedImage(self,data):

      self.saveButton.setEnabled(True)
      self.captureButton.setEnabled(True)
      self.trashButton.setEnabled(True)
   
      self.saveButton.show()
      self.phLevelLabel.show()
      self.trashButton.show()

      self.image1 = data
      self.imageFrame1.setPixmap(QPixmap(data))
      self.imageFrame1.setScaledContents(True)

      self.classText.setText('-')
      self.confidenceText.setText('-')

      self.classText.show()
      self.confidenceText.show()
         
   @pyqtSlot()
   def onSaveImageButtonClicked(self):
      
      # self.statusText.setText("Starting Save...")
      self.phLevelLabel.setEnabled(False)
      self.captureButton.setEnabled(False)
      self.saveButton.setEnabled(False)
      self.trashButton.setEnabled(False)
   
      extension = "png"

      txt = str(self.phLevelLabel.text())
      x = txt.find(".")

      if x >= 0:
         # self.statusText.setText("Illegal File Name")
         return 
      
      number = 1
      path = str(self.phLevelLabel.text()) + " - " + str(number)


      while(True):
               
         filename = "./images/" + path 

         fileInfoA = QFileInfo(filename + '.' + extension)

         if fileInfoA.exists():
            number = number + 1
         else:
            break
   


      self.saveThread1 = QThread()
      self.saveWorker1  = SavingImagesWorker(self.image1, filename + "-a", extension, 1)

      self.saveWorker1.moveToThread(self.saveThread1)

      # Step 5: Connect signals and slots
      self.saveThread1.started.connect(self.saveWorker1.startSaving)
      self.saveWorker1.finished.connect(self.saveThread1.quit)
      self.saveWorker1.finished.connect(self.saveWorker1.deleteLater)
      self.saveThread1.finished.connect(self.saveThread1.deleteLater)
      self.saveWorker1.imageSaved.connect(self.onImageFileSaved)
   
      # Step 6: Start the thread
      self.saveThread1.start()

   @pyqtSlot()
   def onTrashButtonClicked(self):
      self.resetUiComponents()

   @pyqtSlot(list)
   def onImageFileSaved(self):
      self.resetUiComponents()

   @pyqtSlot(list)
   def onInference(self,data):
      
      #data[0] = (String) Class discription
      #data[1] = (String) Class id
      #data[2] = (int) confidence 

      x = float(data[0])
      if x < 7:
         category = ' - Acidic'
      elif x == 7:
         category = ' - Neutral'
      elif x > 7:
         category = ' - Basic'


      self.classText.setText("<font color='Yellow'>" + data[0] +  category + "</font>" )
      self.confidenceText.setText("<font color='Yellow'>" + str(round(data[2], 2)) + "</font>" )

      self.classText.show()
      self.confidenceText.show()
      pass



if __name__ == "__main__":

   # create pyqt5 app 
   App = QApplication(sys.argv)

   # create the instance of our Window 
   window = Window() 
   # start the app 
   sys.exit(App.exec()) 
