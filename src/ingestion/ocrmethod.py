# Handles OCR extraction using Tesseract
# Includes basic image preprocessing to improve text quality

import pytesseract
import cv2 as cv
import numpy as np

# Preprocess image before OCR
# - converts to grayscale
# - applies thresholding to improve contrast
def preprocessing(image):
    print("Applying preprocessing...")

    # convert PIL image to numpy array for OpenCV
    image_array = np.array(image)

    # convert to grayscale (simplifies image for OCR)
    image_array = cv.cvtColor(image_array, cv.COLOR_RGB2GRAY)

    # apply thresholding to create high-contrast black/white image
    processed_image = cv.adaptiveThreshold(image_array, 255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,11,2)
    return processed_image

# Extract text from image using OCR
# applies preprocessing before running Tesseract
def get_text(image) -> str:
    # preprocess image
    new_image = preprocessing(image)

    # run OCR on processed image
    text = pytesseract.image_to_string(new_image)

    return text
