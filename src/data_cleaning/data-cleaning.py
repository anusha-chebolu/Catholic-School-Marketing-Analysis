import os
import cv2
import requests
import numpy as np
import pandas as pd
from deepface import DeepFace

def download_image(url):
    """Downloads an image from a URL and returns it as a NumPy array."""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            image_bytes = np.asarray(bytearray(response.content), dtype="uint8")
            image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
            return image
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred while downloading image: {str(e)}")
        return None

def detect_and_crop_faces(image, output_folder, base_filename):
    """
    Detects faces in an image (as a NumPy array) using DeepFace's MTCNN,
    crops them with a margin, and saves each cropped face in the given output folder.
    """
    if image is None:
        raise ValueError("Invalid image array provided.")
    
    try:
        # DeepFace.extract_faces accepts a numpy array for face detection.
        faces = DeepFace.extract_faces(img_path=image, detector_backend='mtcnn', enforce_detection=False)
    except Exception as e:
        print(f"Error in face detection: {str(e)}")
        return 0

    face_count = 0
    for i, face in enumerate(faces):
        if face['confidence'] < 0.9:  # Skip detections with low confidence
            continue

        facial_area = face['facial_area']
        x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']

        # Add a margin to the crop
        margin = 30
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(image.shape[1] - x, w + 2 * margin)
        h = min(image.shape[0] - y, h + 2 * margin)

        face_img = image[y:y+h, x:x+w]
        # Save each face in the common output folder
        output_path = os.path.join(output_folder, f"{base_filename}_face_{i+1}.jpg")
        cv2.imwrite(output_path, face_img)
        face_count += 1

    return face_count

if __name__ == "__main__":
    # Prompt for the school name and build the CSV file path dynamically.
    school_name = input("Enter the school name: ").strip().lower().replace(" ", "")
    csv_file = f"../../data/raw/deduplicate/{school_name}-school-image-urls-unique.csv"
    
    # Load the CSV file containing image URLs.
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading CSV file {csv_file}: {str(e)}")
        exit(1)
    
    if 'Image URL' not in df.columns:
        print("CSV file must have a 'url' column.")
        exit(1)
    
    # Create a single output folder for the school
    output_folder = f"../../data/processed/cropped_faces_{school_name}"
    os.makedirs(output_folder, exist_ok=True)
    
    total_face_count = 0
    # Process each image URL from the CSV file
    for index, row in df.iterrows():
        url = row['Image URL']
        print(f"Processing image {index+1}: {url}")
        
        image = download_image(url)
        if image is None:
            print("Skipping due to download error.")
            continue
        
        # Use the image index in the file name to avoid collisions.
        num_faces = detect_and_crop_faces(image, output_folder, base_filename=f"img{index+1}")
        total_face_count += num_faces
        print(f"Number of faces detected and cropped for image {index+1}: {num_faces}")
    
    print(f"Total faces cropped: {total_face_count}")
    print(f"All cropped faces are saved in: {output_folder}")