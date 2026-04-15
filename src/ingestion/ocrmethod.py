# OCR utilities for scanned/image-based PDFs
# Includes preprocessing, raw OCR extraction, and line reconstruction

import pytesseract
import cv2 as cv
import numpy as np

def preprocessing(image):
    """Apply basic preprocessing to improve OCR accuracy."""
    
    # Convert PIL image to NumPy array
    image_array = np.array(image)

    # Convert to grayscale
    image_array = cv.cvtColor(image_array, cv.COLOR_RGB2GRAY)

    # Adaptive thresholding (improves contrast for OCR)
    processed_image = cv.adaptiveThreshold(image_array, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)

    return processed_image

def get_text(image) -> str:
    """Extract full OCR text from image."""

    # preprocess image
    new_image = preprocessing(image)

    # run OCR on processed image
    text = pytesseract.image_to_string(new_image)

    return text

def get_data(image) -> list:
    """Extract word-level OCR data and group into lines."""

    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    words = []

    # Iterate over OCR output (column-based format)
    for i in range(len(data['level'])):
        if data['level'][i] == 5 and int(data['conf'][i]) > 0 and data['text'][i].strip() != '':
            words.append({
                'text': data['text'][i].strip(),
                'x': data['left'][i],
                'y': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i],
                'conf': int(data['conf'][i])
            })

    return group_words_into_lines(words)




def group_words_into_lines(words, threshold = 12) -> list:
    """Group OCR words into lines using vertical proximity."""


    if not words:
        return []
    
    # Sort top-to-bottom, then left-to-right
    words = sorted(words, key=lambda x: (x['y'], x['x']))

    lines = []
    current_line = [words[0]]
    current_y = words[0]['y']

    for word in words[1:]:

        #Same line
        if abs(word['y'] - current_y) <= threshold:
            current_line.append(word)

        else:

            #Finalize line
            current_line = sorted(current_line, key = lambda x: x['x'])
            text = ' '.join(w['text'] for w in current_line)

            lines.append({
                'text' : text,
                'words' : current_line
            })

            #Start new line

            current_line = [word]
            current_y = word['y']
    
    #Final line
    current_line = sorted(current_line, key = lambda x: x['x'])
    text = ' '.join(i['text'] for i in current_line)

    lines.append({
        'text' : text,
        'words' : current_line
    })

    return lines
