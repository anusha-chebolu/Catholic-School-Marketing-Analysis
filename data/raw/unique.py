import pandas as pd
import os

def extract_unique_image_urls(input_csv_path):
    """
    Extracts unique image URLs from a CSV file, discarding Page URLs.
    Saves the output in the same directory as the input file.
    
    Parameters:
    input_csv_path (str): Path to the input CSV file
    
    Returns:
    str: Path to the output CSV file
    """
    # Get the directory and filename without extension
    directory = os.path.dirname(input_csv_path)
    filename = os.path.basename(input_csv_path)
    filename_base = os.path.splitext(filename)[0]
    
    # Create output filename
    output_csv_path = os.path.join(directory, f"{filename_base}_unique_urls.csv")
    
    try:
        # Read the CSV file
        df = pd.read_csv(input_csv_path)
        
        # Check if required column exists
        if 'Image URL' not in df.columns:
            print(f"Error: 'Image URL' column not found in {input_csv_path}")
            return None
        
        # Extract only the Image URL column
        image_urls = df['Image URL'].dropna()
        
        # Remove empty strings
        image_urls = image_urls[image_urls != '']
        
        # Get unique values
        unique_urls = image_urls.unique()
        
        # Create a new DataFrame with only unique Image URLs
        result_df = pd.DataFrame({'Image URL': unique_urls})
        
        # Save the result
        result_df.to_csv(output_csv_path, index=False)
        
        print(f"Found {len(unique_urls)} unique image URLs")
        print(f"Results saved to {output_csv_path}")
        
        return output_csv_path
        
    except Exception as e:
        print(f"Error processing {input_csv_path}: {e}")
        return None

# Run the function with the specified input path
input_path = "/Users/anushachebolu/Catholic-School-Marketing-Analysis/data/raw/setonschools-school-image-urls.csv"
extract_unique_image_urls(input_path)