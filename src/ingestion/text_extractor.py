# Main extraction pipeline
# - extracts native PDF text
# - falls back to OCR if text is weak
# - outputs structured JSON

import pymupdf
import json
from pathlib import Path
from src.ingestion import ocrmethod
import numpy as np


pdf_path = r"data\raw\sample-scanned.pdf"
output_path = r"data\processed\output.json"

Path(output_path).parent.mkdir(parents=True, exist_ok=True)

with pymupdf.open(pdf_path) as doc:
    info = {
        'file_name': Path(pdf_path).name,
        'doc_id': Path(pdf_path).stem,
        'page_count': doc.page_count,
        'extraction_method': 'native_text'
    }

    pages = []
    full_text = ""

    
    for page_num, page in enumerate(doc, start=1):

        
        print(f"\n--- Page {page_num} ---")

        # extract native text from PDF
        # measure text length to determine quality
        text = page.get_text()
        text = text.replace("\u200b", "").replace("–","-").replace("’","'")

        # Count characters to assess extraction quality
        char_count = len(text)
        print(f"Native char_count: {char_count}")
        print(f"Native preview: {text[:100]!r}")

        sections = []
        method = 'native_text'

        # decide whether to use OCR based on text quality
        if len(text.strip()) < 50:
            print(f"OCR triggered on page {page_num}")

            # render page as image for OCR
            matrix = pymupdf.Matrix(300 / 72, 300 / 72)

            pix = page.get_pixmap(
                matrix=matrix,
                colorspace=pymupdf.csRGB,
                alpha=False
            )

            img_array = np.frombuffer(
                pix.samples,
                dtype=np.uint8
            ).reshape(pix.height, pix.width, 3)

            
            text = ocrmethod.get_text(img_array)
            char_count = len(text)
            sections = ocrmethod.get_data(img_array)
            print(f"OCR char_count: {len(text)}")
            print(f"OCR preview: {text[:100]!r}")
            
            # update metadata after OCR
            method = 'ocr'
            info['extraction_method'] = 'mixed'

        # store page-level results
        page_dict = {
            'page_num': page_num,
            'method': method,
            'char_count': char_count, 
            'text': text,
            'sections': sections
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


print("\n--- Document Summary ---")
print(f"Total pages: {info['page_count']}")
print(f"Extraction method: {info['extraction_method']}")


print("Done")
        



