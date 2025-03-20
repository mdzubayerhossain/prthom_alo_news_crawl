import pandas as pd
import csv
import re

def clean_text(text):
    """Clean text by removing extra whitespace and newlines"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def summarize_bengali_text(text, max_words=60):
    """
    Create a simple summary of Bengali text by taking the first part
    of the text and ensuring it doesn't exceed max_words words.
    """
    if not text or len(text) == 0:
        return ""
    
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Split into words
    words = cleaned_text.split()
    
    # If the text is already short enough, return it as is
    if len(words) <= max_words:
        return cleaned_text
    
    # Take first max_words
    summary = ' '.join(words[:max_words])
    
    # Add ellipsis to indicate truncation
    return summary.strip() + '...'

def process_csv_with_summaries():
    """
    Read the CSV with Bengali articles, create summaries of up to 60 words,
    and save to a new CSV file.
    """
    # Input and output files
    input_csv = 'prothom_alo_full_content.csv'
    output_csv = 'prothom_alo_with_summaries.csv'
    
    try:
        # Read the CSV file
        print(f"Reading CSV file: {input_csv}")
        df = pd.read_csv(input_csv)
        
        # Check if the required column exists
        if 'full_content' not in df.columns:
            print("Error: 'full_content' column not found in the CSV.")
            return
        
        # Add a new column with summaries
        print("Creating 60-word summaries...")
        df['summary_60words'] = df['full_content'].apply(lambda x: summarize_bengali_text(x, 60))
        
        # Save to a new CSV file
        print(f"Saving results to: {output_csv}")
        df.to_csv(output_csv, index=False, quoting=csv.QUOTE_ALL)
        
        # Display some examples
        print("\nSample summaries:")
        for i, row in df.head(5).iterrows():
            title = row['title'] if 'title' in df.columns else 'N/A'
            summary = row['summary_60words']
            print(f"\nTitle: {title}")
            print(f"Summary ({len(summary.split())} words): {summary}")
        
        print(f"\nProcessing complete. Check {output_csv} for results.")
        print(f"Total articles processed: {len(df)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_csv_with_summaries()
