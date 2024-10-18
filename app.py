import cv2
import numpy as np
import os
from tkinter import Tk, filedialog

def draw_instructions(image, text):
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    text_x = (image.shape[1] - text_size[0]) // 2  # Center the text
    y = image.shape[0] - 6
    # Draw the white text on top of the black rectangle
    cv2.putText(image, text, (text_x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

selected_points = []

def select_points(event, x, y, flags, param):
    global selected_points, image_display, original_image
    if event == cv2.EVENT_LBUTTONDOWN and len(selected_points) < 4:
        selected_points.append((x, y))
        draw_points_and_lines()
    elif event == cv2.EVENT_RBUTTONDOWN and selected_points:
        selected_points.pop()
        draw_points_and_lines()

def draw_points_and_lines():
    global image_display
    image_display = original_image.copy()  # Use the canvas with padding
    for i, point in enumerate(selected_points):
        cv2.circle(image_display, point, 5, (255, 0, 0), -1)
        if i > 0:
            cv2.line(image_display, selected_points[i - 1], point, (255, 255, 255), 2)
    if len(selected_points) == 4:
        instructions = "Press Space to Crop"
    else:
        instructions = "Left-click: Set Corners | Right-click or 'u': Undo last point. | ESC: Skip image."
    draw_instructions(image_display, instructions)
    cv2.imshow("Select Points", image_display)

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

def scale_image_for_display(image, padding=50):
    root = Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    scale_factor = 1.0

    image_height, image_width = image.shape[:2]
    
    max_width = screen_width - padding
    max_height = screen_height - padding

    if image_width > max_width or image_height > max_height:
        scale_factor = min(max_width / image_width, max_height / image_height)
        image = cv2.resize(image, (int(image_width * scale_factor), int(image_height * scale_factor)))

    # Create a black canvas
    canvas = np.zeros((int(image.shape[0] + padding), int(image.shape[1] + padding), 3), dtype=np.uint8)
    canvas[padding//2:int(image.shape[0] + padding//2), padding//2:int(image.shape[1] + padding//2)] = image
    
    return canvas, scale_factor, padding

def process_images_in_folder(folder_path):
    global selected_points, image_display, original_image
    output_folder = os.path.join(folder_path, "undistorted")
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            image = cv2.imread(image_path)
            original_image, scale_factor, padding = scale_image_for_display(image.copy())

            selected_points = []
            draw_points_and_lines()  # Initial draw instructions

            cv2.setMouseCallback("Select Points", select_points)

            while True:
                key = cv2.waitKey(0)
                
                # Check if the window has been closed (ALT+F4)
                if cv2.getWindowProperty("Select Points", cv2.WND_PROP_VISIBLE) < 1:
                    cv2.destroyAllWindows()
                    return
                
                if key == 27:  # ESC to skip the image
                    break
                elif key == ord('u'):  # 'u' to undo the last point
                    if selected_points:
                        selected_points.pop()
                        draw_points_and_lines()
                elif len(selected_points) == 4 and key == 32:  # Space to proceed with cropping
                    original_points = [
                        (int((x - padding//2) / scale_factor), int((y - padding//2) / scale_factor))
                        for x, y in selected_points
                    ]
                    cropped_image = undistort_and_crop(image_path, original_points)
                    save_path = os.path.join(output_folder, filename)
                    cv2.imwrite(save_path, cropped_image)
                    break

            cv2.destroyAllWindows()

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder with Images")
    if folder_path:
        process_images_in_folder(folder_path)