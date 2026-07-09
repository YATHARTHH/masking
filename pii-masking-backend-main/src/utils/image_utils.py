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
            model="gemini-2.0-flash",
            contents=[prompt+"\n\n\nPII Categories to Identify: "+pii_category, content]
        )
    if response and response.text:
        try:
            pii_data = json.loads(response.text[response.text.index("{"):response.text.rindex("}") + 1])

            return pii_data.get("detected_pii", [])
        except json.JSONDecodeError:
            return []
    return []
def mask_human(image,highlight_mode):
    results = face_model(image) 
    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])  
            if cls == 0:  
                x1, y1, x2, y2 = map(int, box.xyxy[0]) 
                
                if highlight_mode == 'blurring':
                    image[y1:y2, x1:x2] = cv2.GaussianBlur(image[y1:y2, x1:x2], (99, 99), 30) 
                elif highlight_mode == 'rectangular_box':
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 255), -1) 
            
    return image
def blur_pii(image_path, pii_texts ,highlight_mode="blur",facial=False):
    print("Facial=",facial)
    similarity_threshold=0.5
    image = cv2.imread(image_path)
    grayimg=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    results = reader.readtext(grayimg)
    print("Extracted Text from Image:")
    print(results)
    print("\n\n")
    
    distance = textdistance.Levenshtein()

    for bbox, text, _ in results:
        if any(pii.lower() in text.lower() for pii in pii_texts):
            (top_left, top_right, bottom_right, bottom_left) = bbox
            x_min, y_min = int(top_left[0]), int(top_left[1])
            x_max, y_max = int(bottom_right[0]), int(bottom_right[1])

            if highlight_mode == 'blurring':
                roi = image[y_min:y_max, x_min:x_max]
                blurred = cv2.GaussianBlur(roi, (51, 51), 30)
                image[y_min:y_max, x_min:x_max] = blurred
            elif highlight_mode == 'rectangular_box':
                cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 255), -1)
        if results:
            for pii in pii_texts:
                similarity_score = distance.normalized_similarity(text.lower(), pii.lower())
                if similarity_score >= similarity_threshold:
                    print(f"Text '{text}' matched with PII '{pii}' with similarity {similarity_score*100:.2f}%")
                    
                    (top_left, top_right, bottom_right, bottom_left) = bbox
                    x_min, y_min = int(top_left[0]), int(top_left[1])
                    x_max, y_max = int(bottom_right[0]), int(bottom_right[1])

                    if highlight_mode == 'blurring':
                        roi = image[y_min:y_max, x_min:x_max]
                        blurred = cv2.GaussianBlur(roi, (51, 51), 30)
                        image[y_min:y_max, x_min:x_max] = blurred
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
    print(pii_info)
    pii_texts = [entry["original_text"] for entry in pii_info]

    
    return blur_pii(image_path, pii_texts,highlight_mode,facial)