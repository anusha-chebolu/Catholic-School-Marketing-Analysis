#!/usr/bin/env python3
"""
Script to remove duplicate image URLs from a CSV file.
"""

import csv

def remove_duplicate_image_urls(input_file, output_file):
    """
    Reads a CSV file, removes rows with duplicate image URLs,
    and writes the unique rows to a new CSV file.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output CSV file
    """
    try:
        # Open input file and read all rows
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Store all rows
            all_rows = list(reader)
            
        print(f"Total rows before removing duplicates: {len(all_rows)}")
        
        # Process rows to remove duplicates
        unique_rows = []
        image_urls = set()
        
        for row in all_rows:
            # Check if this image URL is already seen
            image_url = row.get('Image URL')
            if image_url and image_url not in image_urls:
                image_urls.add(image_url)
                unique_rows.append(row)
        
        print(f"Total rows after removing duplicates: {len(unique_rows)}")
        print(f"Number of unique image URLs: {len(image_urls)}")
        
        # Write unique rows to output file
        if unique_rows:
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=unique_rows[0].keys())
                writer.writeheader()
                writer.writerows(unique_rows)
            
            print(f"Successfully wrote {len(unique_rows)} unique rows to {output_file}")
        else:
            print("No unique rows found")
            
    except Exception as e:
        print(f"Error: {str(e)}")

# Set your input and output filenames here
input_file = "data_collection/popeaceschools-school-image-urls.csv"  # Input file path
output_file = "data_collection/popeaceschools-school-image-urls-unique.csv"  # Output file path

# Run the function to remove duplicates
remove_duplicate_image_urls(input_file, output_file)