import pymupdf
import json
from pathlib import Path

pdf_path = r"data\raw\Resume Version 5 - Retail - IP.pdf"
output_path = r"data\processed\output.json"

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
        text = page.get_text()
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

with open(output_path, "w", encoding="utf-8") as out:
    json.dump(info, out, indent=4, ensure_ascii=False)

print("Done")
        



