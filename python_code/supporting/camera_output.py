#This function capture one frame from the video frame and undistort the image with second function
import cv2
import numpy as np


def capture_one_frame():
    # Initialize the webcam (0 is the default camera)
    cap = cv2.VideoCapture(1)
    
    # Check if the webcam is opened correctly
    if not cap.isOpened():
        print("Could not open webcam")
        return None
    
    # Read a single frame
    ret, frame = cap.read()
    
    # Release the webcam
    cap.release()
    
    # Check if the frame was captured successfully
    if ret:
        return frame
    else:
        print("Failed to capture image")
        return None


def undistort_image(frame):

    # Define the camera matrix with the specified values
    camera_matrix = np.array([
        [1.98739085e+03, 0.00000000e+00, 2.30406719e+03],
        [0.00000000e+00, 1.97195676e+03, 1.63585773e+03],
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
    ])    

    dist_coeffs = np.array([[-0.21450995, 0.03875602, 0.00168561, -0.00679188, 0.02712468]])

    img = frame
    h, w = img.shape[:2]
    
    # Refine the camera matrix
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # Undistort the image
    undistorted_img = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)

    # Crop the image based on the region of interest (roi)
    x, y, w, h = roi
    undistorted_img = undistorted_img[y:y + h, x:x + w]

    return undistorted_img