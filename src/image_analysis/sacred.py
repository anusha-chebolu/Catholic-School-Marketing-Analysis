#!/usr/bin/env python3
"""
Batch Catholic Sacred Image Detector using GPT-4o Vision

This script processes a CSV of image URLs and detects Catholic religious iconography
using OpenAI's GPT-4o model. Images deemed to contain such iconography are saved to a new CSV.
"""

import pandas as pd
from tqdm import tqdm
from openai import OpenAI

# ====== SET YOUR OPENAI API KEY HERE ======
client = OpenAI(api_key=OPENAI_API_KEY)
# ==========================================

# Ask for school name
school_name = input("Enter the school name (used in CSV filename): ").strip()

# File paths
input_csv_path = f"../../data/raw/deduplicate/{school_name}-school-image-urls-unique.csv"
output_csv_path = f"../../results/{school_name}_sacred_images.csv"

# Vision prompt for GPT-4o
vision_prompt = (
    "Does this image contain Catholic religious iconography such as crosses, crucifixes, "
    "religious figures (Jesus, Mary, saints), church interiors, priests, nuns, Catholic rituals, "
    "or Catholic religious symbols? Answer only YES or NO."
)

def analyze_image_with_gpt4o(image_url):
    """Send image to GPT-4o Vision and return True if sacred iconography is detected"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in religious image analysis."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
        )
        answer = response.choices[0].message.content.strip().lower()
        return answer.startswith("yes")
    except Exception as e:
        print(f"[Error] GPT-4o failed for: {image_url}\n{e}")
        return False

# Load image URLs
print(f"\nLoading image URLs from: {input_csv_path}")
df = pd.read_csv(input_csv_path)

if 'Image URL' not in df.columns:
    raise ValueError("CSV must contain a column named 'Image URL'")

sacred_image_urls = []

# Process only the first 50 image URLs
print(f"\nProcessing first 50 images...\n")
for url in tqdm(df['Image URL'].dropna().head(50)):
    if analyze_image_with_gpt4o(url):
        sacred_image_urls.append(url)

# Save results
print(f"\nSaving {len(sacred_image_urls)} sacred image URLs to {output_csv_path}")
pd.DataFrame(sacred_image_urls, columns=['Image URL']).to_csv(output_csv_path, index=False)
print("✅ Done.")
