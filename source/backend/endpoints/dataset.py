from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Query
from fastapi.responses import JSONResponse
import os
import json
import csv
import fitz  # PyMuPDF
import re
import unicodedata
from utils.file_handler import save_uploaded_file, UPLOAD_DIR
import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
import nlpaug.flow as naf
import nltk
from pydantic import BaseModel
import ssl
from nlpaug.util import Action

from nlpaug.util.file.download import DownloadUtil


router = APIRouter()

class AugmentationRequest(BaseModel):
    augmentation_type: str
    dataset_path: str

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

@router.get("/preview")
async def preview_dataset(path: str = Query(None)):
    """
    Returns a preview of the current dataset (first few entries)
    """
    try:
        # If path is not provided, try to find the most recent dataset
        if not path:
            uploads_dir = "./uploads"
            files = [f for f in os.listdir(uploads_dir) if f.endswith('.json')]
            if not files:
                return []
            path = max([os.path.join(uploads_dir, f) for f in files], key=os.path.getmtime)
        
        # Debug log
        print(f"Preview requested for path: {path}")
        
        # Check if file exists
        if not os.path.exists(path):
            # Try finding the file in uploads directory if it's not an absolute path
            if not os.path.isabs(path):
                potential_path = os.path.join("./uploads", path)
                if os.path.exists(potential_path):
                    path = potential_path
                else:
                    raise HTTPException(status_code=404, detail=f"File not found: {path}")
            else:
                raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        # Debug log
        print(f"Using path for preview: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Handle both list and dict formats
            if isinstance(data, list):
                full_count = len(data)
                preview = data[:5]  # Just show first 5 entries
            else:
                full_count = len(data)
                preview = list(data.values())[:5]
                
            # Return preview data with count
            return {
                "preview": preview,
                "full_count": full_count
            }
    except Exception as e:
        print(f"Error in preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading dataset preview: {str(e)}")

@router.post("/augment")
async def augment_dataset(request: AugmentationRequest):
    """
    Augment a dataset file with various text augmentation techniques
    and return both the file location and the augmented data.
    Handles structured text with Instruction/Input/Output sections.
    """
    try:
        # Get the full path of the input dataset
        input_file_path = os.path.join(UPLOAD_DIR, request.dataset_path)
        if not os.path.exists(input_file_path):
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        # Load the dataset
        with open(input_file_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Configure the augmenter based on the selected type
        augmenter = None
        if request.augmentation_type == "keyboard":
            augmenter = nac.KeyboardAug( aug_char_min=0, aug_char_max=2)
        elif request.augmentation_type == "random_word":
            augmenter = naw.RandomWordAug()
        elif request.augmentation_type == "spelling":
            augmenter = nac.SpellingAug()
        elif request.augmentation_type == "synonym":
            augmenter = naw.SynonymAug(aug_src='wordnet')
        else:
            raise HTTPException(status_code=400, detail="Invalid augmentation type")
        
        # Process each item in the dataset
        augmented_dataset = []
        for item in dataset:
            if "text" in item:
                text = item["text"]
                
                # Extract the sections using regex - ONLY extract the content, not the labels
                instruction_match = re.search(r"Instruction:(.*?)(?=Input:|$)", text, re.DOTALL)
                input_match = re.search(r"Input:(.*?)(?=Output:|$)", text, re.DOTALL)
                output_match = re.search(r"Output:(.*?)(?=$)", text, re.DOTALL)
                
                # If structured format is detected
                if instruction_match or input_match or output_match:
                    augmented_text = ""
                    
                    # Process instruction section if found
                    if instruction_match:
                        # Keep the label, only augment the content
                        instruction_content = instruction_match.group(1)
                        augmented_instruction = augmenter.augment(instruction_content)
                        if isinstance(augmented_instruction, list):
                            augmented_instruction = augmented_instruction[0]
                        augmented_text += "Instruction: " + augmented_instruction
                    
                    # Process input section if found
                    if input_match:
                        input_content = input_match.group(1)
                        augmented_input = augmenter.augment(input_content)
                        if isinstance(augmented_input, list):
                            augmented_input = augmented_input[0]
                        augmented_text += " Input: " + augmented_input
                    
                    # Process output section if found
                    if output_match:
                        output_content = output_match.group(1)
                        augmented_output = augmenter.augment(output_content)
                        if isinstance(augmented_output, list):
                            augmented_output = augmented_output[0]
                        augmented_text += " Output: " + augmented_output
                    
                    # Create a new item with the augmented text
                    augmented_item = item.copy()
                    augmented_item["text"] = augmented_text.strip()
                    augmented_dataset.append(augmented_item)
                else:
                    # No structured format found, augment the entire text
                    augmented_text = augmenter.augment(text)
                    if isinstance(augmented_text, list):
                        augmented_text = augmented_text[0]
                    
                    # Create a new item with the augmented text
                    augmented_item = item.copy()
                    augmented_item["text"] = augmented_text.strip()
                    augmented_dataset.append(augmented_item)
        
        # Save the augmented dataset
        output_filename = f"augmented_{os.path.basename(request.dataset_path)}"
        output_file_path = os.path.join(UPLOAD_DIR, output_filename)
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(augmented_dataset, f, ensure_ascii=False, indent=2)
        
        # Prepare preview data (first 5 examples)
        preview_data = augmented_dataset[:5] if len(augmented_dataset) > 5 else augmented_dataset
        
        # Return both the file location and the augmented data
        return {
            "status": "success",
            "message": "Dataset augmented successfully",
            "file_location": output_filename,
            "augmented_data": {
                "preview": preview_data,
                "full_count": len(augmented_dataset)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
