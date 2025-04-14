# import os
# import json
# from deepface import DeepFace

# def analyze_race_from_images(cropped_folder, limit=1000):
#     """
#     Analyzes up to 'limit' images in cropped_folder for race/ethnicity and returns a dictionary
#     with counts for each detected dominant race.
#     """
#     race_counts = {}

#     # Filter for image files (jpg, jpeg, png)
#     image_files = [f for f in os.listdir(cropped_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
#     image_files = sorted(image_files)[:limit]  # Sort and take the first 'limit' files

#     for image_file in image_files:
#         image_path = os.path.join(cropped_folder, image_file)
#         try:
#             # Analyze only the race attribute
#             results = DeepFace.analyze(img_path=image_path, actions=['race'], enforce_detection=False)

#             if isinstance(results, list):
#                 for result in results:
#                     dominant_race = result.get("dominant_race", "Unknown")
#                     race_counts[dominant_race] = race_counts.get(dominant_race, 0) + 1
#             else:
#                 dominant_race = results.get("dominant_race", "Unknown")
#                 race_counts[dominant_race] = race_counts.get(dominant_race, 0) + 1

#         except Exception as e:
#             print(f"Error analyzing {image_file}: {e}")

#     return race_counts

# if __name__ == '__main__':
#     school_name = input("Enter the school name: ").strip().lower().replace(" ", "")
#     cropped_folder = f"../../data/processed/cropped_faces_{school_name}"

#     if not os.path.isdir(cropped_folder):
#         print(f"Folder not found: {cropped_folder}")
#         exit(1)

#     race_counts = analyze_race_from_images(cropped_folder, limit=1000)

#     # Print results
#     print("\nRace/Ethnicity counts:")
#     for race, count in race_counts.items():
#         print(f"{race}: {count}")

#     # Save to JSON
#     os.makedirs("../../results", exist_ok=True)
#     output_file = os.path.join("../../results", f"{school_name}_demographs.json")
#     with open(output_file, "w") as f:
#         json.dump(race_counts, f, indent=4)
    
#     print(f"\nResults saved to: {output_file}")


import os
import json
from collections import Counter
from deepface import DeepFace
from PIL import Image

def analyze_and_organize_faces(cropped_folder, results_base_path, school_name, limit=None, confidence_threshold=0.6):
    """
    Analyze all images in 'cropped_folder' for race and move them into folders under results_base_path/school_name/{race}/.
    Save a cumulative demographics JSON at the root of results_base_path.
    """
    race_counts = Counter()
    image_files = [f for f in os.listdir(cropped_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # If limit is set (optional)
    if limit:
        image_files = sorted(image_files)[:limit]

    for i, image_file in enumerate(image_files):
        image_path = os.path.join(cropped_folder, image_file)
        try:
            results = DeepFace.analyze(
                img_path=image_path,
                actions=['race'],
                enforce_detection=False,
                detector_backend='retinaface'
            )

            result = results[0] if isinstance(results, list) else results
            dominant_race = result.get("dominant_race", "Unknown")
            race_scores = result.get("race", {})
            confidence = race_scores.get(dominant_race, 0) / 100.0

            final_race = dominant_race if confidence >= confidence_threshold else "LowConfidence/Unknown"
            race_counts[final_race] += 1

            # Create output path: ../../results/{school_name}/{race}/
            target_dir = os.path.join(results_base_path, school_name, final_race)
            os.makedirs(target_dir, exist_ok=True)

            # Save image in respective race folder
            img = Image.open(image_path).convert("RGB")
            save_path = os.path.join(target_dir, image_file)
            img.save(save_path)

        except Exception as e:
            print(f"[{i+1}] ❌ Error processing {image_file}: {e}")
            race_counts["Error"] += 1

            # Save problematic image (if possible)
            error_dir = os.path.join(results_base_path, school_name, "Error")
            os.makedirs(error_dir, exist_ok=True)
            try:
                img = Image.open(image_path).convert("RGB")
                img.save(os.path.join(error_dir, image_file))
            except:
                pass  # If image is unreadable, skip

    return dict(race_counts)

if __name__ == '__main__':
    school_name = input("Enter the school name: ").strip().lower().replace(" ", "")
    cropped_folder = f"../../data/processed/cropped_faces_{school_name}"
    results_base_path = "../../results"

    if not os.path.isdir(cropped_folder):
        print(f"❌ Folder not found: {cropped_folder}")
        exit(1)

    print(f"🔍 Processing images in: {cropped_folder}")
    race_summary = analyze_and_organize_faces(cropped_folder, results_base_path, school_name)

    # Save cumulative race summary
    output_json_path = os.path.join(results_base_path, f"{school_name}_demographs.json")
    with open(output_json_path, "w") as f:
        json.dump(race_summary, f, indent=4)

    print("\n📊 Cumulative Race/Ethnicity Counts:")
    for race, count in race_summary.items():
        print(f" - {race}: {count}")

    print(f"\n✅ Summary JSON saved at: {output_json_path}")
    print(f"🖼️ Categorized images saved in: {os.path.join(results_base_path, school_name)}")
