import os
import json
import cv2
import numpy as np
from PIL import Image
import fitz
import easyocr
import textdistance
from pathlib import Path
from src.utils.image_utils import process_image

PROCESSED_FOLDER = "processed"

def process_pdf(pdf_path,pii_category,highlight_mode,facial):
    pdf_path=Path(pdf_path)
    doc = fitz.open(pdf_path)
    # Render PDF pages at 300 DPI to ensure local OCR can read small/colored text accurately
    zoom = 300 / 72
    matrix = fitz.Matrix(zoom, zoom)
    images = [page.get_pixmap(matrix=matrix) for page in doc]  
    processed_images = []

    for i, image in enumerate(images):
        image_path = os.path.join(PROCESSED_FOLDER, f"page_{i}.png")
        image.save(image_path)
        processed_image = process_image(image_path,pii_category,highlight_mode,facial)
        processed_images.append(processed_image)

    pdf_output_path = os.path.join(PROCESSED_FOLDER, os.path.basename(pdf_path))
    doc = fitz.open()
    for img_path in processed_images:
        img_doc = fitz.open()
        img_doc.insert_page(0)
        img_doc[0].insert_image(fitz.Rect(0, 0, 612, 792), filename=img_path)
        doc.insert_pdf(img_doc)
    
    doc.save(pdf_output_path)
    doc.close()
    return pdf_output_path