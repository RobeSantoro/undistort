import cv2
import numpy as np
import os
from tkinter import Tk, filedialog

def select_points(event, x, y, flags, param):
    global selected_points, image
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_points.append((x, y))
        cv2.circle(image, (x, y), 5, (255, 0, 0), -1)
        cv2.imshow("Select Points", image)

def calculate_width_height(points):
    width_top = np.sqrt((points[1][0] - points[0][0]) ** 2 + (points[1][1] - points[0][1]) ** 2)
    width_bottom = np.sqrt((points[2][0] - points[3][0]) ** 2 + (points[2][1] - points[3][1]) ** 2)
    width = max(int(width_top), int(width_bottom))
    height_left = np.sqrt((points[3][0] - points[0][0]) ** 2 + (points[3][1] - points[0][1]) ** 2)
    height_right = np.sqrt((points[2][0] - points[1][0]) ** 2 + (points[2][1] - points[1][1]) ** 2)
    height = max(int(height_left), int(height_right))
    return width, height

def undistort_and_crop(image_path, points):
    image = cv2.imread(image_path)
    pts1 = np.float32(points)
    width, height = calculate_width_height(points)
    pts2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(image, matrix, (width, height))
    return result

def process_images_in_folder(folder_path):
    global selected_points, image
    # Create an output directory
    output_folder = os.path.join(folder_path, "undistorted")
    os.makedirs(output_folder, exist_ok=True)

    # Get all image files in the directory
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            image = cv2.imread(image_path)
            selected_points = []

            # Create a window and set a mouse callback function
            cv2.imshow("Select Points", image)
            cv2.setMouseCallback("Select Points", select_points)

            # Wait until 4 points are selected
            while len(selected_points) < 4:
                cv2.waitKey(1)
            cv2.destroyAllWindows()

            cropped_image = undistort_and_crop(image_path, selected_points)

            # Save the corrected image
            save_path = os.path.join(output_folder, filename)
            cv2.imwrite(save_path, cropped_image)

if __name__ == "__main__":
    # Use Tkinter to select a directory
    root = Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder with Images")
    if folder_path:
        process_images_in_folder(folder_path)