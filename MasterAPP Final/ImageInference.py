#Very important to import cv2 before jetson_inference/utils 
#else it would throw an importError
import cv2

import jetson_inference
import jetson_utils
import numpy

# # load an image (into shared CPU/GPU memory)
# img = jetson_utils.loadImage('data/test/0/pH_Level-0_00 - 1-b.jpg')
input = jetson_utils.videoSource("csi://0", argv=["--framerate=14","--width=4608","--height 2592"])

# load the recognition network
# net = jetson_inference.imageNet('googlenet')
# net = imageNet(model="model/resnet18.onnx", labels="model/labels.txt", 
#                 input_blob="input_0", output_blob="output_0")
net = jetson_inference.imageNet(model="model/googlenet_mod.onnx", labels="model/labels.txt", input_blob="input_0", output_blob="output_0")

while True:
    # capture the next image
    cudaImg = input.Capture()

    if cudaImg is None:
        continue

    print(type(cudaImg),end=" ")
    array = jetson_utils.cudaToNumpy(cudaImg)
    print(type(array),end=" ")
    cuda_img = jetson_utils.cudaFromNumpy(array)
    print(type(cudaImg))


# # classify the image
# class_idx, confidence = net.Classify(img)

# # find the object description
# class_desc = net.GetClassDesc(class_idx)

# # print out the result
# print("image is recognized as '{:s}' (class #{:d}) with {:f}% confidence".format(class_desc, class_idx, confidence * 100))

