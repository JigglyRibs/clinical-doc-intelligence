# Clinical Document Intelligence System

This project is a Python-based pipeline for extracting and structuring text from PDFs. It’s designed around real-world scenarios where important information is stored in messy documents like invoices, shipping records, and reports.

## Overview

In many healthcare and supply chain systems, critical data is locked inside PDFs that are difficult to process automatically. I wanted to build a system that can take these documents and turn them into structured, usable data.

This project is the first step toward that goal.

## Current Features

- Native PDF text extraction using PyMuPDF  
- OCR support for scanned/image-based PDFs (Tesseract + OpenCV)  
- Image preprocessing (detail enhancement, resizing, and grayscale conversion)
- Word-level OCR output with bounding boxes  
- Line reconstruction using spatial grouping  
- Structured JSON output (page + document level)  

## How It Works

### Native PDFs
- Load PDF using PyMuPDF  
- Extract text per page  
- Track metadata (page number, character count)  

### Scanned PDFs
- Convert page to image  
- Apply detail enhancement, resizing, and grayscale conversion
- Run Tesseract OCR  
- Extract word-level data (text + position)  

### Line Reconstruction
- Sort words by position (`y`, then `x`)  
- Group words into lines using vertical proximity  
- Sort each line left-to-right  
- Rebuild readable text  

## Example Output

```json
{
  "page_num": 1,
  "method": "ocr",
  "char_count": 523,
  "text": "EDUCATION\nBachelor of Science...",
  "sections": [
    {
      "header": "EDUCATION",
      "blocks": [
        {
          "text": "EDUCATION\nBachelor of Science",
          "lines": []
        }
      ],
      "text": "EDUCATION\nBachelor of Science"
    }
  ]
}
```

## Tech Stack

  - Python
  - PyMuPDF
  - Tesseract (pytesseract)
  - OpenCV
  - NumPy
  - JSON

## How to Run

1. Install dependencies  
   `pip install -r requirements.txt`

2. Add a PDF to  
   `data/raw/`

3. Run  
   `python -m src.ingestion.text_extractor`

## Next steps

  -Classify document types
  -Extract key fields (e.g, invoice number, destination)
  -Build a search and question-answering system

## Why I built this

This project focuses on turning unstructured documents into clear, machine readable data. As it continues to develop, it will tackle a universal problem across all industries; gathering necessary data from wildly unstructured or convoluted documents. Systems like this can allow for a faster access to patient information in healthcare, or reduce paperwork load in real estate spaces where large volumes of documents go into every transaction. 



