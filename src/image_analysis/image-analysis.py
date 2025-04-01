import os
import json
from deepface import DeepFace

def analyze_race_from_images(cropped_folder, limit=1000):
    """
    Analyzes up to 'limit' images in cropped_folder for race/ethnicity and returns a dictionary
    with counts for each detected dominant race.
    """
    race_counts = {}

    # Filter for image files (jpg, jpeg, png)
    image_files = [f for f in os.listdir(cropped_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files = sorted(image_files)[:limit]  # Sort and take the first 'limit' files

    for image_file in image_files:
        image_path = os.path.join(cropped_folder, image_file)
        try:
            # Analyze only the race attribute
            results = DeepFace.analyze(img_path=image_path, actions=['race'], enforce_detection=False)

            if isinstance(results, list):
                for result in results:
                    dominant_race = result.get("dominant_race", "Unknown")
                    race_counts[dominant_race] = race_counts.get(dominant_race, 0) + 1
            else:
                dominant_race = results.get("dominant_race", "Unknown")
                race_counts[dominant_race] = race_counts.get(dominant_race, 0) + 1

        except Exception as e:
            print(f"Error analyzing {image_file}: {e}")

    return race_counts

if __name__ == '__main__':
    school_name = input("Enter the school name: ").strip().lower().replace(" ", "")
    cropped_folder = f"../../data/processed/cropped_faces_{school_name}"

    if not os.path.isdir(cropped_folder):
        print(f"Folder not found: {cropped_folder}")
        exit(1)

    race_counts = analyze_race_from_images(cropped_folder, limit=1000)

    # Print results
    print("\nRace/Ethnicity counts:")
    for race, count in race_counts.items():
        print(f"{race}: {count}")

    # Save to JSON
    os.makedirs("../../results", exist_ok=True)
    output_file = os.path.join("../../results", f"{school_name}_demographs.json")
    with open(output_file, "w") as f:
        json.dump(race_counts, f, indent=4)
    
    print(f"\nResults saved to: {output_file}")
