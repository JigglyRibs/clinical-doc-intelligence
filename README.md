# Clinical Document Intelligence System

This project is a Python-based pipeline for extracting and structuring text from PDFs. It’s designed around real-world scenarios where important information is stored in messy documents like invoices, shipping records, and reports.

## Overview

In many healthcare and supply chain systems, critical data is locked inside PDFs that are difficult to process automatically. I wanted to build a system that can take these documents and turn them into structured, usable data.

This project is the first step toward that goal.

## Current Features

- Extracts text from multi-page PDFs
- Uses native PDF text when available
- Falls back to OCR for image-based pages
- Applies image preprocessing to improve OCR accuracy
- Outputs structured JSON with page-level metadata
  
## How It Works

  - A PDF is loaded using PyMuPDF  
  - Each page is processed individually  
  - Text is extracted directly from the PDF
  - If extracted text is too weak, OCR is used as a fallback
  - Metadata is collected for each page  
  - Everything is saved into a structured JSON file

## OCR Fallback

For pages with weak or missing text, the system uses Tesseract OCR.

Basic preprocessing is applied before OCR:
  - grayscale conversion
  - adaptive thresholding

This helps improve text extraction from scanned or low-quality documents.

## Example Output

```json
{
  "file_name": "invoice_001.pdf",
  "page_count": 2,
  "pages": [
    {
      "page_number": 1,
      "method": "native_text",
      "char_count": 523,
      "text": "..."
    }
  ],
  "full_text": "..."
}
```

## Tech Stack

  - Python
  - PyMuPDF
  - Tesseract OCR
  - OpenCV
  - JSON

## How to Run

1. Install dependencies  
   `pip install -r requirements.txt`

2. Add a PDF to  
   `data/raw/`

3. Run  
   `python -m src.ingestion.text_extractor`

## Next steps

- Improve OCR accuracy and preprocessing
- Extract structured fields (e.g., invoice number, destination)
- Add document classification
- Build a search and question-answering system

## Why I built this

This project focuses on turning unstructured documents into clear, machine readable data. As it continues to develop, it will tackle a universal problem across all industries; gathering necessary data from wildly unstructured or convoluted documents. Systems like this can allow for a faster access to patient information in healthcare, or reduce paperwork load in real estate spaces where large volumes of documents go into every transaction. 



