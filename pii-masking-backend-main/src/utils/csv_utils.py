import pandas as pd
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


def process_csv(csv_path,pii_category,highlight_mode):
    
    if csv_path.lower().endswith(".csv"):
        d=pd.read_csv(csv_path)
    else:
        d=pd.read_excel(csv_path)   
    csv_prompt="""
    Analyze the provided CSV data and identify any Personally Identifiable Information (PII) Which i am Mentioning present within the columns. For each column that contains PII data, you need to document the type of PII, the column name, and the description of where the PII is found. If a column contains PII in any row, document the column once and categorize the type of PII it contains, without repeating values for every individual row.
    Strictly only Extract the Info Which comes under the PII Category i have Assigning
    
   Output Format:

    The output should be a detailed, structured summary of all detected PII in the CSV data. For each column that contains PII, include the type of PII and the column name. The output must be in JSON format and must follow the structure provided below:


    {
    "detected_pii": [
        {
        "type": "Full Name",
        "column_name": "Name",
        "description": "Full name information present in the Name column."
        },
        {
        "type": "Social Security Number",
        "column_name": "SSN",
        "description": "Social Security Number information present in the SSN column."
        },
        {
        "type": "Personal Email Address",
        "column_name": "Email",
        "description": "Email address information present in the Email column."
        },
        {
        "type": "Date of Birth",
        "column_name": "DOB",
        "description": "Date of birth information present in the DOB column."
        }
    ]
    }
    Rules:

    Column Name: Report only the columns that contain PII. Do not repeat the PII values per row; document the column once if it contains PII.
    No Repetition: If PII is found in a column, only report that column once, along with the type of PII.
    Context Description: Document where the PII is found (i.e., the column name and a brief description of the PII present in that column).
    No Alterations: Do not alter, mask, or remove any PII from the data. Only detect and report.
    Structured Output: The output must be properly structured in JSON format and compliant with the structure provided above.
    Example Input:

    Name	SSN	Email	DOB
    John Doe	123-45-6789	john.doe@example.com	01/01/1990
    Jane Smith	234-56-7890	jane.smith@example.com	02/02/1985
    Expected Output:


    {
    "detected_pii": [
        {
        "type": "Full Name",
        "column_name": "Name",
        "description": "Full name information present in the Name column."
        },
        {
        "type": "Social Security Number",
        "column_name": "SSN",
        "description": "Social Security Number information present in the SSN column."
        },
        {
        "type": "Personal Email Address",
        "column_name": "Email",
        "description": "Email address information present in the Email column."
        },
        {
        "type": "Date of Birth",
        "column_name": "DOB",
        "description": "Date of birth information present in the DOB column."
        }
    ]
    }




    PII Categories to Detect:
    """
    inputs=[csv_prompt+pii_category+"\n\n\nCSV Data: \n"+d.head().to_string()]
    from src.utils.gemini_utils import generate_content_with_retry
    response = generate_content_with_retry(
            client,
            model="gemini-2.0-flash",
            contents=inputs
        )
    if response and response.text:
        try:
            pii_data = json.loads(response.text[response.text.index("{"):response.text.rindex("}") + 1])
            print(pii_data)
            print(type(pii_data))
            for i in pii_data["detected_pii"]:
                c=i.get("column_name")
                l=[]
                for j in d[c]:
                    if highlight_mode=="named_replacement":
                        temp="["+i.get("type")+"]"
                    elif highlight_mode=="replacement":
                        temp="[MASKED]"
                    else:
                        temp=" ".join(["X"*len(k) for k in str(j).split()])
                    l.append(temp)
                d[c]=l
            csv_output_path = os.path.join(PROCESSED_FOLDER, os.path.basename(csv_path))
            if csv_path.lower().endswith(".csv"):
                d.to_csv(csv_output_path)
            else:
                d.to_excel(csv_output_path)
            return csv_output_path
        except json.JSONDecodeError:
            return []
    return []