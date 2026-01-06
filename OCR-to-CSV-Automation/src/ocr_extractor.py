# src/ocr_extractor.py

from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os

# -------------------------------
# CONFIGURATION
# -------------------------------

# Path to Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r"E:\ocr\tesseract.exe"

# Path to Poppler bin folder (required for pdf2image)
POPPLER_PATH = r"E:\poppler\Library\bin"

# -------------------------------
# OCR FUNCTIONS
# -------------------------------

def pdf_to_text(pdf_path):
    """
    Convert PDF to text using Tesseract OCR.
    Supports multi-page PDFs.
    """
    text = ""
    try:
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img)
            text += page_text + "\n"
    except Exception as e:
        print(f"Error processing PDF '{pdf_path}': {e}")
    return text

def image_to_text(image_path):
    """
    Convert image (PNG/JPG/JPEG) to text using Tesseract OCR.
    """
    text = ""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
    except Exception as e:
        print(f"Error processing image '{image_path}': {e}")
    return text

def file_to_text(file_path):
    """
    Detect file type and convert to text accordingly.
    Supports PDF and common image formats.
    """
    ext = file_path.lower().split('.')[-1]
    if ext == "pdf":
        return pdf_to_text(file_path)
    elif ext in ["png","jpg","jpeg"]:
        return image_to_text(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

# -------------------------------
# QUICK TEST
# -------------------------------

if __name__ == "__main__":
    # Replace with your own test files
    test_pdf = r"data\raw\receipt1.pdf"
    test_img = r"data\raw\receipt2.png"

    print("----- PDF TEST -----")
    print(file_to_text(test_pdf))

    print("\n----- IMAGE TEST -----")
    print(file_to_text(test_img))
