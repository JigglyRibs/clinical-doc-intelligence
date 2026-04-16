# Main extraction pipeline
# - extracts native PDF text
# - falls back to OCR if text is weak
# - outputs structured JSON

import pymupdf
import json
from pathlib import Path
from src.ingestion import ocrmethod


pdf_path = r"data\raw\Resume Version 5 - Retail - IP.pdf"
output_path = r"data\processed\output.json"

# open PDF document
with pymupdf.open(pdf_path) as doc:
    info = {
        'file_name': Path(pdf_path).name,
        'doc_id': Path(pdf_path).stem,
        'page_count': doc.page_count,
        'extraction_method': 'native_text'
    }

    pages = []
    full_text = ""
    words = []

    # process each page in the document
    for page_num, page in enumerate(doc, start=1):

        # debug: show page number
        print(f"\n--- Page {page_num} ---")

        # extract native text from PDF
        # measure text length to determine quality
        text = page.get_text()

        # Count characters to assess extraction quality
        char_count = len(text)
        print(f"Native char_count: {char_count}")
        print(f"Native preview: {text[:100]!r}")


        method = 'native_text'

        # decide whether to use OCR based on text quality
        if len(text.strip()) > 1:
            # fallback to OCR for pages with weak native text

            print(f"OCR triggered on page {page_num}")

            # render page as image for OCR
            pix = page.get_pixmap()
            image = pix.pil_image()

            # extract text using OCR
            text = ocrmethod.get_text(image)
            char_count = len(text)
            words = ocrmethod.get_data(image)
            print(f"OCR char_count: {len(text)}")
            print(f"OCR preview: {text[:100]!r}")
            print(words)

            # update metadata after OCR
            method = 'ocr'
            info['extraction_method'] = 'mixed'

        # store page-level results
        page_dict = {
            'page_num': page_num,
            'method': method,
            'char_count': char_count, 
            'text': text
        }

        pages.append(page_dict)
        full_text += text + "\n\n"

        print(f"Final method: {method}")



    # combine results into final structure
    info['pages'] = pages
    info['full_text'] = full_text

# save output to JSON file
with open(output_path, "w", encoding="utf-8") as out:
    json.dump(info, out, indent=4, ensure_ascii=False)

# print summary of extraction results
print("\n--- Document Summary ---")
print(f"Total pages: {info['page_count']}")
print(f"Extraction method: {info['extraction_method']}")

print("Done")
        



