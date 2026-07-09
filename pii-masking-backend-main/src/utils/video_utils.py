import os
import cv2
import asyncio
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import tempfile
import shutil
from typing import List, Tuple
import json
from PIL import Image
import easyocr
import textdistance
from google import genai
from ultralytics import YOLO

# Constants
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
TEMP_FRAMES_FOLDER = "temp_frames"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(TEMP_FRAMES_FOLDER, exist_ok=True)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
face_model = YOLO("yolov8n.pt")
reader = easyocr.Reader(["en", 'hi'])


def detect_pii_for_video(frame_image, pii_category):
    """Detect PII in a video frame using Gemini API"""
    prompt = """Analyze the provided image frame and identify any Personally Identifiable Information (PII) from the specified categories.
    Extract only the PII that matches the categories provided.
    
    Output Format (JSON only):
    {
        "detected_pii": [
            {
                "type": "Category Name",
                "original_text": "Detected Text",
                "description": "Context description"
            }
        ]
    }
    
    Rules:
    - Be descriptive when identifying PII
    - Support multiple languages
    - Only identify, do not alter or mask
    - Return valid JSON only
    """
    
    try:
        from src.utils.gemini_utils import generate_content_with_retry
        response = generate_content_with_retry(
            client,
            model="gemini-2.5-flash",
            contents=[prompt + "\n\n\nPII Categories to Identify: " + pii_category, frame_image]
        )
        
        if response and response.text:
            try:
                pii_data = json.loads(response.text[response.text.index("{"):response.text.rindex("}") + 1])
                detected_list = pii_data.get("detected_pii", [])
                from src.utils.gemini_utils import filter_pii_by_categories
                filtered_list = filter_pii_by_categories(detected_list, pii_category)
                return filtered_list
            except json.JSONDecodeError:
                return []
    except Exception as e:
        print(f"Error detecting PII: {e}")
        return []
    
    return []


def mask_human_in_frame(image, highlight_mode):
    """Mask human faces in a frame using YOLO"""
    results = face_model(image)
    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            if cls == 0:  # Person class
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                if highlight_mode == 'blurring':
                    image[y1:y2, x1:x2] = cv2.GaussianBlur(image[y1:y2, x1:x2], (99, 99), 30)
                elif highlight_mode == 'rectangular_box':
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 255), -1)
    
    return image


def blur_pii_in_frame(frame, pii_texts, highlight_mode="blurring", facial=False, similarity_threshold=0.5):
    """Blur or mask PII in a single video frame"""
    grayimg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = reader.readtext(grayimg)
    
    distance = textdistance.Levenshtein()
    
    for bbox, text, _ in results:
        # Direct match
        if any(pii.lower() in text.lower() for pii in pii_texts):
            (top_left, top_right, bottom_right, bottom_left) = bbox
            x_min, y_min = int(top_left[0]), int(top_left[1])
            x_max, y_max = int(bottom_right[0]), int(bottom_right[1])
            
            if highlight_mode == 'blurring':
                roi = frame[y_min:y_max, x_min:x_max]
                blurred = cv2.GaussianBlur(roi, (51, 51), 30)
                frame[y_min:y_max, x_min:x_max] = blurred
            elif highlight_mode == 'rectangular_box':
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 255), -1)
        
        # Fuzzy match
        if results:
            for pii in pii_texts:
                similarity_score = distance.normalized_similarity(text.lower(), pii.lower())
                if similarity_score >= similarity_threshold:
                    (top_left, top_right, bottom_right, bottom_left) = bbox
                    x_min, y_min = int(top_left[0]), int(top_left[1])
                    x_max, y_max = int(bottom_right[0]), int(bottom_right[1])
                    
                    if highlight_mode == 'blurring':
                        roi = frame[y_min:y_max, x_min:x_max]
                        blurred = cv2.GaussianBlur(roi, (51, 51), 30)
                        frame[y_min:y_max, x_min:x_max] = blurred
                    elif highlight_mode == 'rectangular_box':
                        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 255), -1)
    
    # Mask facial features if requested
    if facial:
        frame = mask_human_in_frame(frame, highlight_mode)
    
    return frame


async def extract_frames_async(video_path: str, output_folder: str, sample_rate: int = 30) -> Tuple[List[str], dict]:
    """
    Extract frames from video asynchronously
    sample_rate: Extract 1 frame every N frames (default 30 = 1 fps for 30fps video)
    """
    def extract():
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        video_info = {
            'fps': fps,
            'total_frames': total_frames,
            'width': width,
            'height': height,
            'sample_rate': sample_rate
        }
        
        frame_paths = []
        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample frames based on sample_rate
            if frame_count % sample_rate == 0:
                frame_filename = f"frame_{saved_count:06d}.jpg"
                frame_path = os.path.join(output_folder, frame_filename)
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                saved_count += 1
            
            frame_count += 1
        
        cap.release()
        return frame_paths, video_info
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        frame_paths, video_info = await loop.run_in_executor(executor, extract)
    
    return frame_paths, video_info


async def process_frame_async(frame_path: str, pii_texts: List[str], highlight_mode: str, facial: bool) -> str:
    """Process a single frame asynchronously"""
    def process():
        frame = cv2.imread(frame_path)
        processed_frame = blur_pii_in_frame(frame, pii_texts, highlight_mode, facial)
        cv2.imwrite(frame_path, processed_frame)
        return frame_path
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, process)
    
    return result


async def process_frames_batch_async(frame_paths: List[str], pii_texts: List[str], 
                                     highlight_mode: str, facial: bool, batch_size: int = 10):
    """Process frames in batches asynchronously"""
    processed_paths = []
    
    for i in range(0, len(frame_paths), batch_size):
        batch = frame_paths[i:i + batch_size]
        tasks = [process_frame_async(frame_path, pii_texts, highlight_mode, facial) 
                for frame_path in batch]
        
        batch_results = await asyncio.gather(*tasks)
        processed_paths.extend(batch_results)
        
        print(f"Processed {len(processed_paths)}/{len(frame_paths)} frames")
    
    return processed_paths


async def create_video_from_frames_async(frame_folder: str, output_path: str, 
                                        video_info: dict, original_video_path: str):
    """Create video from processed frames asynchronously"""
    def create():
        # Get sorted frame files
        frame_files = sorted([f for f in os.listdir(frame_folder) if f.endswith('.jpg')])
        
        if not frame_files:
            raise ValueError("No frames found to create video")
        
        # Read first frame to get dimensions
        first_frame = cv2.imread(os.path.join(frame_folder, frame_files[0]))
        height, width = first_frame.shape[:2]
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = video_info['fps']
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Write frames
        for frame_file in frame_files:
            frame_path = os.path.join(frame_folder, frame_file)
            frame = cv2.imread(frame_path)
            
            # Duplicate frames based on sample_rate to maintain original video length
            sample_rate = video_info.get('sample_rate', 1)
            for _ in range(sample_rate):
                out.write(frame)
        
        out.release()
        
        # Copy audio from original video if exists
        try:
            import subprocess
            temp_output = output_path.replace('.mp4', '_temp.mp4')
            os.rename(output_path, temp_output)
            
            cmd = [
                'ffmpeg', '-i', temp_output, '-i', original_video_path,
                '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
                '-shortest', output_path, '-y'
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            os.remove(temp_output)
        except Exception as e:
            print(f"Could not copy audio: {e}")
            if os.path.exists(temp_output):
                os.rename(temp_output, output_path)
        
        return output_path
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, create)
    
    return result


async def process_video_optimized(video_path: str, pii_category: str, 
                                  highlight_mode: str, facial: bool = False, 
                                  sample_rate: int = 30):
    """
    Main function to process video with PII masking using async operations
    
    Args:
        video_path: Path to input video
        pii_category: Categories of PII to detect
        highlight_mode: 'blurring' or 'rectangular_box'
        facial: Whether to mask faces
        sample_rate: Extract 1 frame every N frames (higher = faster but less accurate)
    
    Returns:
        Path to processed video
    """
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    temp_folder = os.path.join(TEMP_FRAMES_FOLDER, f"{video_name}_frames")
    os.makedirs(temp_folder, exist_ok=True)
    
    try:
        print("Step 1: Extracting frames from video...")
        frame_paths, video_info = await extract_frames_async(video_path, temp_folder, sample_rate)
        print(f"Extracted {len(frame_paths)} frames (sampled from {video_info['total_frames']} total frames)")
        
        # Detect PII from first few frames (sample)
        print("Step 2: Detecting PII in sample frames...")
        sample_frames = frame_paths[:min(5, len(frame_paths))]
        all_pii_texts = set()
        
        for frame_path in sample_frames:
            frame_image = Image.open(frame_path)
            pii_info = detect_pii_for_video(frame_image, pii_category)
            pii_texts = [entry["original_text"] for entry in pii_info]
            all_pii_texts.update(pii_texts)
        
        pii_texts_list = list(all_pii_texts)
        print(f"Detected PII: {pii_texts_list}")
        
        # Process all frames with detected PII
        print("Step 3: Processing frames with PII masking...")
        await process_frames_batch_async(frame_paths, pii_texts_list, highlight_mode, facial, batch_size=10)
        
        # Create output video
        print("Step 4: Creating processed video...")
        output_filename = f"processed_{video_name}.mp4"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        await create_video_from_frames_async(temp_folder, output_path, video_info, video_path)
        
        print(f"Video processing complete: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error processing video: {e}")
        raise e
    
    finally:
        # Cleanup temporary frames
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
            print(f"Cleaned up temporary frames")


# Wrapper function for non-async contexts
def process_video_optimized_sync(video_path: str, pii_category: str, 
                                 highlight_mode: str, facial: bool = False):
    """Synchronous wrapper for process_video_optimized"""
    return asyncio.run(process_video_optimized(video_path, pii_category, highlight_mode, facial))