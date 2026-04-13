# Clinical Document Intelligence System

This project is a Python-based pipeline for extracting and structuring text from PDFs. It’s designed around real-world scenarios where important information is stored in messy documents like invoices, shipping records, and reports.

## Overview

In many healthcare and supply chain systems, critical data is locked inside PDFs that are difficult to process automatically. I wanted to build a system that can take these documents and turn them into structured, usable data.

This project is the first step toward that goal.

## Current Features

- Extracts text from multi-page PDFs using PyMuPDF  
- Stores results in structured JSON format  
- Includes page-level details (page number, character count)  
- Combines all extracted text into a single document field  

## How It Works

- A PDF is loaded using PyMuPDF  
- Each page is processed individually  
- Text is extracted directly from the PDF  
- Metadata is collected for each page  
- Everything is saved into a structured JSON file  

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

  -Python
  -PyMuPDF
  -JSON

## How to Run

  1. Install Dependencies
    pip install -r requirements.txt
  2. Add a PDF to
    data/raw/
  3. Run
    python -m src.ingestion.text_extractor

## Next steps

  -Add OCR for scanned PDFs
  -Classify document types
  -Extract key fields (e.g, invoice number, destination)
  -Build a search and question-answering system

## Why I built this

I wanted to build something with an easy-to-see real-world application, since most systems rely on documents, and not everyone has the luxury to take the time for meticulous examination. The project is very general right
now, but has the potential to be useful in hospitals where quickly processing patients is key, or real estate, where the paperwork can often be heavy.



