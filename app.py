import cv2
import numpy as np

def undistort_and_crop(image_path, points):
    # Load image
    image = cv2.imread(image_path)
    
    # Define the points for the perspective transformation
    pts1 = np.float32(points)  # Points marked by user (top-left, top-right, bottom-right, bottom-left)
    
    # Define the destination points for the undistorted image
    width, height = 500, 700  # Adjust as needed
    pts2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    
    # Get the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    
    # Apply the perspective warp
    result = cv2.warpPerspective(image, matrix, (width, height))
    
    return result

# Example usage:
image_path = "W:\\ATTRAVERSO\\undistort\\photo_png\\IMG_3963.png"
# User-defined corner points (top-left, top-right, bottom-right, bottom-left)
points = [(100, 50), (400, 50), (400, 400), (100, 400)]
cropped_image = undistort_and_crop(image_path, points)

# Save or display the result
cv2.imwrite('undistorted_painting.jpg', cropped_image)
cv2.imshow('Result', cropped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()