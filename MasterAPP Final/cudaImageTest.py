import jetson_utils
import cv2
import time 

input = jetson_utils.videoSource("csi://0", argv=["--framerate=14","--width=4608","--height 2592"])

time.sleep(3)

cudaImg = input.Capture(format="rgb8")
cudaImg = input.Capture(format="rgb8")
cudaImg = input.Capture(format="rgb8")
cudaImg = input.Capture(format="rgb8")


leftCrop   = 1514
rightCrop  = 1454
topCrop    = 476
bottomCrop = 556


crop_roi = (leftCrop, topCrop, cudaImg.width - rightCrop, cudaImg.height - bottomCrop)


imgOutput = jetson_utils.cudaAllocMapped(width=cudaImg.width - leftCrop - rightCrop,
                                         height=cudaImg.height -topCrop - bottomCrop,
                                         format=cudaImg.format)

jetson_utils.cudaDeviceSynchronize()

jetson_utils.cudaCrop(cudaImg, imgOutput, crop_roi)

jetson_utils.cudaDeviceSynchronize()

original_array = jetson_utils.cudaToNumpy(cudaImg)
cropped_array = jetson_utils.cudaToNumpy(imgOutput)

print(original_array.dtype , cropped_array.dtype, cudaImg.format)

cv2.imshow('Original', original_array) 
cv2.imshow('Cropped', cropped_array)

print(original_array.dtype , cropped_array.dtype, cudaImg.format)

cv2.waitKey(0)
cv2.destroyAllWindows() 

print(original_array.dtype , cropped_array.dtype, cudaImg.format)



