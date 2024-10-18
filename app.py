import cv2
import numpy as np

selected_points = []  # To store the selected points

def select_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_points.append((x, y))
        cv2.circle(image, (x, y), 5, (255, 0, 0), -1)
        cv2.imshow("Select Points", image)

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

# Load the original image
image_path = "W:\\ATTRAVERSO\\undistort\\photo_png\\IMG_3963.png"
image = cv2.imread(image_path)

# Create a window and set a mouse callback function
cv2.imshow("Select Points", image)
cv2.setMouseCallback("Select Points", select_points)

# Wait until 4 points are selected
while len(selected_points) < 4:
    cv2.waitKey(1)

cv2.destroyAllWindows()

# Use the selected points to undistort and crop the image
cropped_image = undistort_and_crop(image_path, selected_points)

# Save or display the result
cv2.imwrite('undistorted_painting.jpg', cropped_image)
cv2.imshow('Result', cropped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()