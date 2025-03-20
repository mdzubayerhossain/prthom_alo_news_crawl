import pandas as pd
import torch
from transformers import pipeline, BertTokenizer, BertModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import csv
import re

def clean_text(text):
    """Clean text by removing extra whitespace and newlines"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_sentence_embeddings(sentences, model, tokenizer):
    """Get embeddings for a list of sentences using BERT"""
    embeddings = []
    
    for sentence in sentences:
        # Tokenize and convert to tensor
        inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # Get embeddings
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Use CLS token as sentence embedding
        embedding = outputs.last_hidden_state[:, 0, :].numpy()
        embeddings.append(embedding[0])
    
    return np.array(embeddings)

def split_into_sentences(text):
    """Split Bengali text into sentences"""
    # Simple rule-based sentence splitting for Bengali
    # This is a basic implementation and might need improvement
    sentences = re.split(r'[।!?]', text)
    return [s.strip() for s in sentences if s.strip()]

def summarize_bengali_with_rag(text, num_sentences=5):
    """
    Summarize Bengali text using a RAG-inspired approach:
    1. Split text into sentences
    2. Get sentence embeddings
    3. Calculate sentence importance based on centrality
    4. Select top sentences maintaining original order
    """
    if not text or len(text.strip()) == 0:
        return ""
    
    # Clean text
    text = clean_text(text)
    
    # Split into sentences
    sentences = split_into_sentences(text)
    
    # If text is already short, return as is
    if len(sentences) <= num_sentences:
        return text
    
    # Load model and tokenizer - using multilingual BERT
    model_name = "bert-base-multilingual-cased"  # Supports Bengali
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertModel.from_pretrained(model_name)
    
    # Get sentence embeddings
    embeddings = get_sentence_embeddings(sentences, model, tokenizer)
    
    # Calculate sentence centrality (similarity to other sentences)
    similarity_matrix = cosine_similarity(embeddings)
    centrality_scores = np.sum(similarity_matrix, axis=1)
    
    # Get indices of top sentences by centrality
    top_indices = np.argsort(centrality_scores)[-num_sentences:]
    
    # Sort indices to maintain original order
    top_indices = sorted(top_indices)
    
    # Construct summary from selected sentences
    selected_sentences = [sentences[i] for i in top_indices]
    summary = '। '.join(selected_sentences) + '।'
    
    return summary

def process_csv_with_rag_summaries():
    """
    Read the CSV with Bengali articles, create summaries using RAG approach,
    and save to a new CSV file.
    """
    # Input and output files
    input_csv = 'prothom_alo_full_content.csv'
    output_csv = 'prothom_alo_with_rag_summaries.csv'
    
    try:
        # Read the CSV file
        print(f"Reading CSV file: {input_csv}")
        df = pd.read_csv(input_csv)
        
        # Check if the required column exists
        if 'full_content' not in df.columns:
            print("Error: 'full_content' column not found in the CSV.")
            return
        
        # Process a sample for demonstration
        sample_size = min(20, len(df))  # Process first 20 or all if fewer
        
        # Create summaries for the sample
        print(f"Creating RAG-based summaries for {sample_size} articles...")
        summaries = []
        for i, row in df.head(sample_size).iterrows():
            print(f"Processing article {i+1}/{sample_size}...")
            summary = summarize_bengali_with_rag(row['full_content'], num_sentences=3)
            summaries.append(summary)
            
        # Add summaries to the dataframe
        df_sample = df.head(sample_size).copy()
        df_sample['rag_summary'] = summaries
        
        # Save to a new CSV file
        print(f"Saving results to: {output_csv}")
        df_sample.to_csv(output_csv, index=False, quoting=csv.QUOTE_ALL)
        
        # Display some examples
        print("\nSample summaries:")
        for i, row in df_sample.head(3).iterrows():
            title = row['title'] if 'title' in df.columns else 'N/A'
            original = row['full_content']
            summary = row['rag_summary']
            print(f"\nTitle: {title}")
            print(f"Original length: {len(original.split())} words")
            print(f"Summary length: {len(summary.split())} words")
            print(f"Summary: {summary}")
        
        print(f"\nProcessing complete. Check {output_csv} for results.")
        print(f"Total articles processed: {sample_size}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_csv_with_rag_summaries()
