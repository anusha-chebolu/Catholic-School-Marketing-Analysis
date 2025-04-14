import os
import json
from collections import Counter
from deepface import DeepFace
from PIL import Image
import numpy as np

# These are the full race classes used in DeepFace (FairFace)
DEEPFACE_RACES = {
    "white", "black", "asian", "indian", "middle eastern", "latino hispanic", "other"
}

def softmax(scores):
    vals = np.array(list(scores.values()), dtype=np.float64)
    exp_scores = np.exp(vals - np.max(vals))  # for numerical stability
    probs = exp_scores / np.sum(exp_scores)
    return dict(zip(scores.keys(), probs))

def analyze_with_backends(image_path, backends):
    all_preds = []
    for backend in backends:
        try:
            result = DeepFace.analyze(
                img_path=image_path,
                actions=['race'],
                detector_backend=backend,
                enforce_detection=False
            )
            result = result[0] if isinstance(result, list) else result
            scores = result.get("race", {})
            soft_scores = softmax(scores)
            dominant = max(soft_scores, key=soft_scores.get)
            all_preds.append((dominant.lower(), soft_scores))
        except Exception as e:
            print(f"⚠️ Backend '{backend}' failed: {e}")
    return all_preds

def get_final_race(predictions, ambiguity_gap=0.05):
    """
    Get final race by combining predictions from multiple backends.
    """
    if not predictions:
        return "Unknown", {}, 0.0

    # Combine scores from all backends
    combined_scores = {}
    for _, score_dict in predictions:
        for race, score in score_dict.items():
            race = race.lower()
            combined_scores[race] = combined_scores.get(race, 0) + score

    for race in combined_scores:
        combined_scores[race] /= len(predictions)

    sorted_scores = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    if len(sorted_scores) >= 2:
        top_score = sorted_scores[0][1]
        second_score = sorted_scores[1][1]
        if abs(top_score - second_score) < ambiguity_gap:
            return "Ambiguous", Counter(), top_score

    top_race = sorted_scores[0][0]
    return top_race, Counter({top_race: 1}), sorted_scores[0][1]

def analyze_and_organize_faces(cropped_folder, results_base_path, school_name):
    race_counts = Counter()
    debug_logs = []

    image_files = [f for f in os.listdir(cropped_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for i, image_file in enumerate(image_files):
        image_path = os.path.join(cropped_folder, image_file)
        try:
            img = Image.open(image_path).convert("RGB")
            if img.size[0] < 50 or img.size[1] < 50:
                print(f"[{i+1}] ⛔ Skipping low-res image: {image_file}")
                race_counts["LowQuality"] += 1
                continue

            predictions = analyze_with_backends(image_path, ["mtcnn", "retinaface", "opencv"])
            final_race, votes, confidence = get_final_race(predictions)

            # Clean folder name
            final_race_folder = final_race.lower().replace(" ", "_")
            race_counts[final_race] += 1

            target_dir = os.path.join(results_base_path, school_name, final_race_folder)
            os.makedirs(target_dir, exist_ok=True)
            img.save(os.path.join(target_dir, image_file))

            debug_logs.append({
                "image": image_file,
                "final_race": final_race,
                "confidence": round(confidence, 4)
            })

        except Exception as e:
            print(f"[{i+1}] ❌ Error processing {image_file}: {e}")
            race_counts["Error"] += 1
            error_dir = os.path.join(results_base_path, school_name, "error")
            os.makedirs(error_dir, exist_ok=True)
            try:
                img.save(os.path.join(error_dir, image_file))
            except:
                pass

    return dict(race_counts), debug_logs

if __name__ == '__main__':
    school_name = input("Enter the school name: ").strip().lower().replace(" ", "")
    cropped_folder = f"../../data/processed/cropped_faces_{school_name}"
    results_base_path = "../../results"

    if not os.path.isdir(cropped_folder):
        print(f"❌ Folder not found: {cropped_folder}")
        exit(1)

    print(f"🔍 Processing images in: {cropped_folder}")
    race_summary, debug_logs = analyze_and_organize_faces(cropped_folder, results_base_path, school_name)

    summary_path = os.path.join(results_base_path, f"{school_name}_demographs.json")
    with open(summary_path, "w") as f:
        json.dump(race_summary, f, indent=4)

    debug_path = os.path.join(results_base_path, f"{school_name}_debug_log.json")
    with open(debug_path, "w") as f:
        json.dump(debug_logs, f, indent=4)

    print("\n📊 Final Race Summary:")
    for race, count in race_summary.items():
        print(f" - {race}: {count}")

    print(f"\n✅ Demographics JSON saved at: {summary_path}")
    print(f"🧪 Debug log saved at: {debug_path}")
    print(f"🖼️ Categorized images saved in: {os.path.join(results_base_path, school_name)}")
