import os
from deepface import DeepFace

def analyze_race_from_images(cropped_folder):
    """
    Analyzes each image in cropped_folder for race/ethnicity and returns a dictionary
    with counts for each detected dominant race.
    """
    race_counts = {}
    
    # Filter for image files (jpg, jpeg, png)
    image_files = [f for f in os.listdir(cropped_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    for image_file in image_files:
        image_path = os.path.join(cropped_folder, image_file)
        try:
            # Analyze only the race attribute
            results = DeepFace.analyze(img_path=image_path, actions=['race'], enforce_detection=False)

            # If DeepFace returns a list, iterate through the detected faces
            if isinstance(results, list):
                for result in results:
                    dominant_race = result.get("dominant_race", "Unknown")
                    race_counts[dominant_race] = race_counts.get(dominant_race, 0) + 1
            else:  # Handle cases where only one face is detected (not returned as a list)
                dominant_race = results.get("dominant_race", "Unknown")
                race_counts[dominant_race] = race_counts.get(dominant_race, 0) + 1

        except Exception as e:
            print(f"Error analyzing {image_file}: {e}")
    
    return race_counts

if __name__ == '__main__':
    # Dynamically derive the school name
    school_name = input("Enter the school name: ").strip().lower().replace(" ", "")
    
    # Construct the cropped folder name
    cropped_folder = f"../data-cleaning/cropped_faces_{school_name}"
    
    # Ensure the folder exists
    if not os.path.isdir(cropped_folder):
        print(f"Folder not found: {cropped_folder}")
        exit(1)
    
    # Analyze race/ethnicity across all cropped face images in the folder
    race_counts = analyze_race_from_images(cropped_folder)
    
    # Print out the results
    print("\nRace/Ethnicity counts:")
    for race, count in race_counts.items():
        print(f"{race}: {count}")
