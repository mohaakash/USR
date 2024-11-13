import cv2
import numpy as np
import glob

def camera_calibration(chessboard_size, frame_size, chessboard_images_path):
    # Criteria for corner detection
    criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)
    
    # Prepare object points like (0,0,0), (1,0,0), (2,0,0), ..., (chessboard_size[0]-1, chessboard_size[1]-1, 0)
    objp = np.zeros((chessboard_size[0]*chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    
    # Arrays to store object points and image points from all the images
    objpoints = []  # 3d points in real world space
    imgpoints = []  # 2d points in image plane

    # Read all images from the provided path
    images = glob.glob(chessboard_images_path + '/*.jpg')
    print(f"Found {len(images)} images.")

    for image_file in images:
        img = cv2.imread(image_file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
            cv2.imshow('Chessboard', img)
            cv2.waitKey(500)
        else:
            print(f"Failed to detect chessboard corners in {image_file}")

    cv2.destroyAllWindows()

    # Perform camera calibration
    if len(objpoints) > 0 and len(imgpoints) > 0:
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frame_size, None, None)
        print("Camera Matrix:\n", camera_matrix)
        print("Distortion Coefficients:\n", dist_coeffs)
        return camera_matrix, dist_coeffs
    else:
        print("Calibration failed: no chessboard corners were detected in any image.")
        return None, None

def undistort_image(image_path, camera_matrix, dist_coeffs):
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    
    # Refine the camera matrix
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # Undistort the image
    undistorted_img = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)

    # Crop the image based on the region of interest (roi)
    x, y, w, h = roi
    undistorted_img = undistorted_img[y:y + h, x:x + w]

    return undistorted_img

if __name__ == "__main__":
    # Chessboard configuration
    chessboard_size = (8, 6)  # Chessboard pattern size (corners per row and column)
    frame_size = (4608, 3456)   # Image size (width, height)

    # Path where chessboard images are stored
    chessboard_images_path = 'photos/camera calibration'

    # Step 1: Calibrate the camera
    camera_matrix, dist_coeffs = camera_calibration(chessboard_size, frame_size, chessboard_images_path)

    if camera_matrix is not None and dist_coeffs is not None:
        # Step 2: Load an image to undistort
        distorted_image_path = 'photos/YDXJ0016.JPG'
        undistorted_image = undistort_image(distorted_image_path, camera_matrix, dist_coeffs)

        # Display the original and undistorted images
        cv2.imshow("Distorted Image", cv2.imread(distorted_image_path))
        cv2.imshow("Undistorted Image", undistorted_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Camera calibration failed.")  
