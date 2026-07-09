import os
import json
import cv2
import numpy as np
from PIL import Image
import easyocr
import textdistance
import fitz  # PyMuPDF
import easyocr
import cv2
from PIL import Image
import textdistance
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from pdf2image import convert_from_path
from google import genai
from google.genai import types
import pandas as pd
from pydub import AudioSegment
from pydub.generators import Sine
import math
import audioread
import wave
from ultralytics import YOLO
from docx import Document
from paddleocr import PaddleOCR
from rapidfuzz import process, fuzz
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import time
from pathlib import Path


UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
face_model = YOLO("yolov8n.pt") 
reader = easyocr.Reader(["en",'hi'])  
def detect_pii(content,pii_category):
    prompt = """Analyze the provided document or image and carefully identify any Personally Identifiable Information (PII) Which i am Mentioning. Your task is to detect, document, and categorize PII elements accurately without making any changes or masking.
        Strictly only Extract the Info Which comes under the PII Category i have Assigning
        Output Format:
            The output should be a detailed, structured summary of all detected PII in the document or image. Do not make any changes or alterations to the data. The format should include the type of PII, the exact text identified, and the context or description where it was found, ensuring that each category of PII is well-documented.

            Example:

            {
            "detected_pii": [
                {
                "type": "Full Name",
                "original_text": "John Doe",
                "description": "Full name of the individual identified in the document header."
                },
                {
                "type": "Social Security Number",
                "original_text": "123-45-6789",
                "description": "SSN found in the personal details section."
                },
                {
                "type": "Personal Email Address",
                "original_text": "john.doe@example.com",
                "description": "Email address found in the contact information section."
                }
            ]
            }
        Rules:
        Be as descriptive as possible when identifying and categorizing each piece of PII.
        Ensure that the context around each detected PII element is documented, describing where and how the PII is presented.
        ENsure that the PII of any language should listed.
        Only identify the presence of PII; do not alter, mask, or remove any details.
        Ensure the output is properly structured and JSON-compliant.
    """
    from src.utils.gemini_utils import generate_content_with_retry
    response = generate_content_with_retry(
            client,
            model="gemini-2.5-flash",
            contents=[prompt+"\n\n\nPII Categories to Identify: "+pii_category, content]
        )
    if response and response.text:
        try:
            pii_data = json.loads(response.text[response.text.index("{"):response.text.rindex("}") + 1])

            return pii_data.get("detected_pii", [])
        except json.JSONDecodeError:
            return []
    return []
def heavy_blur_roi(roi):
    """
    Applies a heavy, secure blur using pixelation/downsampling combined with Gaussian smoothing.
    This guarantees text is mathematically unreadable, regardless of the resolution.
    """
    h, w = roi.shape[:2]
    if h <= 0 or w <= 0:
        return roi
    # Scale down to destroy details
    scale = 0.1
    small_w = max(4, int(w * scale))
    small_h = max(4, int(h * scale))
    
    small_roi = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
    pixelated = cv2.resize(small_roi, (w, h), interpolation=cv2.INTER_LINEAR)
    
    # Smooth the pixelated blocks
    k_w = int(w * 0.1) | 1
    k_h = int(h * 0.1) | 1
    k_w = max(5, k_w if k_w % 2 != 0 else k_w + 1)
    k_h = max(5, k_h if k_h % 2 != 0 else k_h + 1)
    
    blurred = cv2.GaussianBlur(pixelated, (k_w, k_h), 0)
    return blurred

def mask_human(image,highlight_mode):
    results = face_model(image) 
    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])  
            if cls == 0:  
                x1, y1, x2, y2 = map(int, box.xyxy[0]) 
                
                if highlight_mode == 'blurring':
                    roi = image[y1:y2, x1:x2]
                    h, w = roi.shape[:2]
                    if h > 0 and w > 0:
                        image[y1:y2, x1:x2] = heavy_blur_roi(roi)
                elif highlight_mode == 'rectangular_box':
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 255), -1) 
            
    return image

def blur_pii(image_path, pii_texts ,highlight_mode="blur",facial=False):
    print("Facial=",facial)
    
    # Clean and filter pii_texts to avoid empty or very short strings matching everything
    valid_pii_texts = []
    for pii in pii_texts:
        if pii and isinstance(pii, str):
            cleaned = pii.strip()
            # Ignore empty strings or single characters which cause false positive matches
            if len(cleaned) >= 2:
                valid_pii_texts.append(cleaned.lower())
                
    image = cv2.imread(image_path)
    
    if not valid_pii_texts:
        print("No valid PII texts to blur.")
        if facial:
            image = mask_human(image, highlight_mode)
            blurred_path = os.path.join(PROCESSED_FOLDER, os.path.basename(image_path))
            cv2.imwrite(blurred_path, image)
            return blurred_path
        return image_path

    grayimg=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    results = reader.readtext(grayimg)
    print("Extracted Text from Image:")
    print(results)
    print("\n\n")
    
    distance = textdistance.Levenshtein()
    similarity_threshold=0.5

    for bbox, text, _ in results:
        if any(pii in text.lower() for pii in valid_pii_texts):
            (top_left, top_right, bottom_right, bottom_left) = bbox
            x_min, y_min = int(top_left[0]), int(top_left[1])
            x_max, y_max = int(bottom_right[0]), int(bottom_right[1])

            if highlight_mode == 'blurring':
                # Add padding to fully obscure character borders
                padding_x = int((x_max - x_min) * 0.1) + 2
                padding_y = int((y_max - y_min) * 0.1) + 2
                x_min_pad = max(0, x_min - padding_x)
                y_min_pad = max(0, y_min - padding_y)
                x_max_pad = min(image.shape[1], x_max + padding_x)
                y_max_pad = min(image.shape[0], y_max + padding_y)

                roi = image[y_min_pad:y_max_pad, x_min_pad:x_max_pad]
                image[y_min_pad:y_max_pad, x_min_pad:x_max_pad] = heavy_blur_roi(roi)
            elif highlight_mode == 'rectangular_box':
                cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 255), -1)
        if results:
            for pii in valid_pii_texts:
                similarity_score = distance.normalized_similarity(text.lower(), pii)
                if similarity_score >= similarity_threshold:
                    print(f"Text '{text}' matched with PII '{pii}' with similarity {similarity_score*100:.2f}%")
                    
                    (top_left, top_right, bottom_right, bottom_left) = bbox
                    x_min, y_min = int(top_left[0]), int(top_left[1])
                    x_max, y_max = int(bottom_right[0]), int(bottom_right[1])

                    if highlight_mode == 'blurring':
                        # Add padding to fully obscure character borders
                        padding_x = int((x_max - x_min) * 0.1) + 2
                        padding_y = int((y_max - y_min) * 0.1) + 2
                        x_min_pad = max(0, x_min - padding_x)
                        y_min_pad = max(0, y_min - padding_y)
                        x_max_pad = min(image.shape[1], x_max + padding_x)
                        y_max_pad = min(image.shape[0], y_max + padding_y)

                        roi = image[y_min_pad:y_max_pad, x_min_pad:x_max_pad]
                        image[y_min_pad:y_max_pad, x_min_pad:x_max_pad] = heavy_blur_roi(roi)
                    elif highlight_mode == 'rectangular_box':
                        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 255), -1)
    if facial:
        image=mask_human(image,highlight_mode)
    blurred_path = os.path.join(PROCESSED_FOLDER, os.path.basename(image_path))
    cv2.imwrite(blurred_path, image)
    return blurred_path
def process_image(image_path,pii_category,highlight_mode,facial):
    highlight_mode=highlight_mode
    content=Image.open(image_path)
    pii_info = detect_pii(content,pii_category)
    from src.utils.gemini_utils import filter_pii_by_categories
    pii_info = filter_pii_by_categories(pii_info, pii_category)
    print("Filtered PII:", pii_info)
    pii_texts = [entry["original_text"] for entry in pii_info]

    
    return blur_pii(image_path, pii_texts,highlight_mode,facial)