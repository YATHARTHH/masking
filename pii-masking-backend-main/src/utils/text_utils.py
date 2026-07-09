import os
import json
import cv2
import numpy as np
from PIL import Image
import fitz
import easyocr
import textdistance
from google import genai
from google.genai import types

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


def process_text(text_path,pii_category,highlight_mode):
    prompt = """Analyze the provided document and carefully identify any Personally Identifiable Information (PII) Which i am Mentioning. Your task is to detect, document, and categorize PII elements accurately without making any changes or masking.
        Strictly only Extract the Info Which comes under the PII Category i have Assigning
        Output Format:
            The output should be a detailed, structured summary of all detected PII in the document or image. Do not make any changes or alterations to the data. The format should include the type of PII, the exact text identified, and the context or description where it was found, ensuring that each category of PII is well-documented.

            Example:

            {
            "detected_pii": [
                {
                "type": "Full Name",
                "original_text": "John Doe"
                },
                {
                "type": "Social Security Number",
                "original_text": "123-45-6789"
                },
                {
                "type": "Personal Email Address",
                "original_text": "john.doe@example.com"
                }
            ]
            }
        Rules:
        Be as descriptive as possible when identifying and categorizing each piece of PII.
        Ensure that the context around each detected PII element is documented, describing where and how the PII is presented.
        ENsure that the PII of any language should listed.
        Only identify the presence of PII; do not alter, mask, or remove any details.
        Ensure the output is properly structured and JSON-compliant.

        Document Content:
    """
    v=open(text_path)
    v.seek(0)
    text=v.read()
    v.close()
    from src.utils.gemini_utils import generate_content_with_retry
    response = generate_content_with_retry(
            client,
            model="gemini-2.0-flash",
            contents=[prompt+text+"\n\n\nPII Categories to Identify: "+pii_category, ]
        )
    if response and response.text:
        try:
            pii_data = json.loads(response.text[response.text.index("{"):response.text.rindex("}") + 1])
            l=[]
            print(pii_data)
            for i in pii_data["detected_pii"]:
                if highlight_mode=="named_replacement":
                    text=text.replace(i["original_text"],"["+i["type"]+"]")
                elif highlight_mode=="replacement":
                    text=text.replace(i["original_text"],"[MASKED]")
                else:
                    text=text.replace(i["original_text"],len(i["original_text"])*"X")
            text_output_path = os.path.join(PROCESSED_FOLDER, os.path.basename(text_path))
            with open(text_output_path,"w+") as w:
                w.write(text)
                w.close()
            return text_output_path
        except Exception as e:
            print(e)
