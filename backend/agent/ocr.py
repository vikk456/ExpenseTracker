import pytesseract
from PIL import Image
import io
import os

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_receipt(image_bytes: bytes) -> str:
    # Check if it's a PDF
    if image_bytes[:4] == b'%PDF':
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(image_bytes)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img)
        return text
    else:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text