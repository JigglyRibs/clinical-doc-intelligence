# Extracts text from PDF files using PyMuPDF
# Outputs structured data with page-level metadata and full document text

import pymupdf
import json
from pathlib import Path

pdf_path = r"data\raw\Resume Version 5 - Retail - IP.pdf"
output_path = r"data\processed\output.json"

#Opens the PDF and turns the information into a dictionary 
with pymupdf.open(pdf_path) as doc:
    info = {
        'file_name': Path(pdf_path).name,
        'doc_id': Path(pdf_path).stem,
        'page_count': doc.page_count,
        'extraction_method': 'native_text'
    }

    pages = []
    full_text = ""

    # Iterate through each page and extract text + metadata
    for page_num, page in enumerate(doc, start=1):
        # Extract raw text from the page
        text = page.get_text()

        # Count characters to assess extraction quality
        char_count = len(text)
        page_dict = {
            'page_num': page_num,
            'method': 'native_text',
            'char_count': char_count, 
            'text': text
        }
        pages.append(page_dict)
        full_text += text + "\n\n"
    info['pages'] = pages
    info['full_text'] = full_text
    
# Save structured document data to JSON file
with open(output_path, "w", encoding="utf-8") as out:
    json.dump(info, out, indent=4, ensure_ascii=False)

print("Done")
        



