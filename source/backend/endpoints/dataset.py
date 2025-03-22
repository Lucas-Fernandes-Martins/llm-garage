from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import json
import csv
import fitz  # PyMuPDF
import re
import unicodedata
from utils.file_handler import save_uploaded_file

router = APIRouter()

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    # Save the file using a utility function
    file_location = await save_uploaded_file(file)
    
    # Get file extension
    _, file_extension = os.path.splitext(file.filename)
    file_extension = file_extension.lower()
    
    # Process based on file type
    try:
        if file_extension == '.pdf':
            json_output = process_pdf_file(file_location)
            return {"message": "PDF processed successfully", "file_location": json_output}
        elif file_extension == '.json':
            # JSON files don't need processing
            return {"message": "JSON dataset uploaded successfully", "file_location": file_location}
        elif file_extension == '.csv':
            # Process CSV file to convert it to JSON format
            json_output = process_csv_file(file_location)
            return {"message": "CSV processed successfully", "file_location": json_output}
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

def process_pdf_file(pdf_path):
    """
    Process a PDF file and convert it to JSON for fine-tuning dataset
    """
    # Extract text from PDF
    extracted_json = pdf_path.replace('.pdf', '_extracted.json')
    fine_tuning_json = pdf_path.replace('.pdf', '_finetuning.json')
    
    # Extract text from PDF
    extract_text_from_pdf(pdf_path, extracted_json)
    
    # Process extracted text into fine-tuning format
    process_pdf_json(extracted_json, fine_tuning_json)
    
    return fine_tuning_json

def extract_text_from_pdf(pdf_path, output_json):
    """
    Extracts text from each page of a PDF and saves it in a JSON file.
    Each key is formatted as "page_X" where X is the page number.
    """
    doc = fitz.open(pdf_path)
    pdf_content = {}
    for page_number in range(doc.page_count):
        page = doc[page_number]
        text = page.get_text()
        pdf_content[f"page_{page_number + 1}"] = text
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(pdf_content, f, indent=2, ensure_ascii=False)
    return output_json

def remove_headers_footers(text):
    """
    Remove lines that are likely headers or footers, such as page numbers
    or lines that match "Page X" patterns.
    """
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        # Skip lines that contain only numbers
        if re.match(r'^\s*\d+\s*$', line):
            continue
        # Skip lines matching patterns like "Page 1" (case-insensitive)
        if re.match(r'^\s*Page\s+\d+\s*$', line, re.IGNORECASE):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()

def clean_special_characters(text):
    """
    Normalize unicode characters and remove non-printable characters.
    Also collapses multiple spaces/newlines.
    """
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^\x20-\x7E]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, max_words=100):
    """
    Split text into smaller chunks if it exceeds max_words.
    Adjust max_words based on your model's input size limitations.
    """
    words = text.split()
    if len(words) <= max_words:
        return [text]
    
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

def process_pdf_json(input_file, output_file, max_words_per_chunk=100):
    """
    Loads the extracted PDF JSON, cleans the text, and splits long pages into chunks.
    Then, it formats each chunk as a dictionary with a "text" key and saves the data.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        pdf_data = json.load(f)
    
    training_examples = []
    
    for key, raw_text in pdf_data.items():
        # Remove headers/footers
        cleaned_text = remove_headers_footers(raw_text)
        # Clean special characters and extra whitespace
        cleaned_text = clean_special_characters(cleaned_text)
        # Split the cleaned text into chunks if necessary
        chunks = chunk_text(cleaned_text, max_words=max_words_per_chunk)
        # Add each chunk as a separate training example
        for chunk in chunks:
            training_examples.append({"text": chunk})
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(training_examples, f, indent=2, ensure_ascii=False)
    
    return output_file

def process_csv_file(csv_path):
    """
    Process a CSV file and convert it to JSON for fine-tuning dataset.
    Assumes that the CSV contains text data that needs to be formatted for fine-tuning.
    """
    # Output JSON path
    output_json = csv_path.replace('.csv', '_finetuning.json')
    
    training_examples = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            # Get headers
            headers = next(csv_reader, None)
            
            # If no headers, use default column names
            if not headers:
                headers = [f"column_{i}" for i in range(len(next(csv_reader)))]
                # Reset file pointer
                f.seek(0)
                
            # Read rows
            for row in csv_reader:
                if not row:  # Skip empty rows
                    continue
                
                # Combine all text fields in the row
                text = " ".join([str(value) for value in row if value.strip()])
                
                # Clean special characters
                cleaned_text = clean_special_characters(text)
                
                # Add as training example
                if cleaned_text:
                    training_examples.append({"text": cleaned_text})
    except Exception as e:
        # If CSV reading fails, try a more flexible approach with different delimiters
        training_examples = process_flexible_csv(csv_path)
    
    # Write to JSON file
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(training_examples, f, indent=2, ensure_ascii=False)
    
    return output_json

def process_flexible_csv(csv_path):
    """
    Process CSV with different delimiters if standard CSV reading fails.
    Tries different delimiters (comma, tab, semicolon) to parse the file.
    """
    delimiters = [',', '\t', ';', '|']
    training_examples = []
    
    for delimiter in delimiters:
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                # Try reading with this delimiter
                csv_reader = csv.reader(f, delimiter=delimiter)
                for row in csv_reader:
                    if not row:  # Skip empty rows
                        continue
                    
                    # Combine all text fields in the row
                    text = " ".join([str(value) for value in row if value.strip()])
                    
                    # Clean special characters
                    cleaned_text = clean_special_characters(text)
                    
                    # Add as training example
                    if cleaned_text:
                        training_examples.append({"text": cleaned_text})
                
                # If we got here, parsing succeeded with this delimiter
                if training_examples:
                    break
        except Exception:
            # Try next delimiter
            continue
    
    return training_examples
