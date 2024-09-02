# ML-pHLevel
For my thesis, my team and I developed an Image Classification System using the NVIDIA Jetson Nano and libraries such as Jetson Inference,OpenCV and PyTorch. The project involved:

Designing a camera backlight PCB using Proteus and getting it manufactured.
Creating a 3D case to house the camera, PCB backlight, and Jetson Nano.
Installing necessary drivers and setting up the Jetson Nano and camera.
We trained the system using PyTorch and OpenCV, employing the OTSU Method for optimal edge detection. The training involved comparing the readings from pH strips dipped in various solutions to a pH meter, using GoogLeNet for our neural network. After training with over 900+ images, we developed a system capable of accurately identifying the pH level of solutions through computer vision, displaying results on a mounted monitor. The system could classify solutions as acidic, neutral, or basic.
