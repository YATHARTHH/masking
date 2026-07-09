import os
import json
import re
from pydub import AudioSegment
from pydub.generators import Sine
from google import genai

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def extract_json(text):
    """Extract JSON object from text response."""
    json_matches = re.findall(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", text, re.DOTALL)
    if not json_matches:
        raise ValueError("No JSON object found in model response")
    return json.loads(json_matches[0])

def generate_beep(duration_ms=500, frequency=300):
    """Generate a sine wave beep tone using pydub."""
    beep = Sine(frequency).to_audio_segment(duration=duration_ms)
    return beep

def load_audio(file_path):
    """Load an audio file using pydub (MP3, WAV, etc.)."""
    print(f"Trying to open audio file: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    audio = AudioSegment.from_file(file_path)
    return audio

def add_beep_to_audio(audio_data, start_time, end_time, beep_duration=500, frequency=300):
    """Add beep sound to the audio data between specified start and end times."""
    start_ms = start_time * 1000
    end_ms = end_time * 1000

    beep_duration = end_ms - start_ms
    if beep_duration <= 0:
        print(f"Warning: Invalid duration ({beep_duration}ms) for beep from {start_time}s to {end_time}s")
        return audio_data
    
    beep = generate_beep(beep_duration, frequency)
    before = audio_data[:start_ms]
    after = audio_data[end_ms:]
    
    final_audio = before + beep + after
    return final_audio

def convert_time_to_seconds(time_str):
    """Convert time string (HH:MM:SS) to total seconds."""
    hours, minutes, seconds = map(int, time_str.split(':'))
    return hours * 3600 + minutes * 60 + seconds

def apply_audio_masking(input_file, output_file, detected_pii):
    """Process audio file by adding beep tones for detected PII."""
    audio_data = load_audio(input_file)
    print(f"Type of detected_pii: {type(detected_pii)}")
    print(f"Content of detected_pii: {detected_pii}")
    
    # Handle case where detected_pii might be a string
    if isinstance(detected_pii, str):
        try:
            detected_pii = json.loads(detected_pii)
        except json.JSONDecodeError:
            print(f"Error: detected_pii is a string but not valid JSON: {detected_pii}")
            raise ValueError("detected_pii must be a dictionary or valid JSON string")
    
    # Check if detected_pii has the expected structure
    if not isinstance(detected_pii, dict) or "detected_pii" not in detected_pii:
        print(f"Error: Invalid structure for detected_pii: {detected_pii}")
        raise ValueError("detected_pii must be a dictionary with 'detected_pii' key")
    
    pii_list = detected_pii["detected_pii"]
    print(f"Found {len(pii_list)} PII instances to mask")
    
    for idx, pii in enumerate(pii_list):
        print(f"Processing PII {idx + 1}: {pii.get('type', 'Unknown')} - '{pii.get('original_text', 'N/A')}'")
        start_time = convert_time_to_seconds(pii['start_time'])
        end_time = convert_time_to_seconds(pii['end_time'])
        
        audio_data = add_beep_to_audio(audio_data, start_time, end_time)
    
    print(f"Exporting processed audio to: {output_file}")
    audio_data.export(output_file, format="wav")
    
    return output_file

# Main function matching the signature called from main.py
def process_audio(audio_path, pii_category, highlight_mode):
    """
    Main function to process audio file for PII detection and masking.
    
    Args:
        audio_path: Path to the input audio file
        pii_category: PII categories to detect (comma-separated string or list)
        highlight_mode: Mode for highlighting/masking PII (e.g., 'beep', 'silence', etc.)
    
    Returns:
        Path to the processed audio file
    """
    print(f"=== Audio Processing Started ===")
    print(f"Audio path: {audio_path}")
    print(f"PII Category: {pii_category}")
    print(f"Highlight Mode: {highlight_mode}")
    
    # Verify file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")
    
    audio_prompt = """
Task: Analyze the provided audio file to meticulously identify and document any Personally Identifiable Information (PII) which I am mentioning present. For each instance of PII detected, provide the exact time range(s) or timestamp(s) where it occurs in the audio, ensuring an accurate, comprehensive report. Your task is to detect, document, and categorize PII elements exclusively based on the audio content, without any alteration or masking of data.

Strictly only extract the info which comes under the PII Category I have assigned.

PII Type:
For each identified PII element, determine if the information was spoken aloud (Audio PII). This task exclusively requires the extraction of information from audio content—do not extract PII from visual or textual content.

Output Format:
The output should be in a detailed, structured JSON format, capturing the following:

- Type of PII: The specific category of PII detected (e.g., Full Name, Social Security Number, etc.).
- Original Text: The exact spoken PII detected (e.g., "John Doe," "123-45-6789").
- Start Time: The exact timestamp (in the format HH:MM:SS) when the PII begins.
- End Time: The exact timestamp (in the format HH:MM:SS) when the PII ends.
- Description: A brief description of how the PII was presented in the audio.

Ensure that each instance of PII is documented fully, including exact timestamps for precision.

Example Output:

{
  "detected_pii": [
    {
      "type": "Full Name",
      "original_text": "John Doe",
      "start_time": "00:00:15",
      "end_time": "00:00:17",
      "description": "The speaker introduced themselves with their full name during the introduction of the podcast."
    },
    {
      "type": "Social Security Number",
      "original_text": "123-45-6789",
      "start_time": "00:12:30",
      "end_time": "00:12:35",
      "description": "The SSN was mentioned aloud during a brief conversation about personal financial matters."
    },
    {
      "type": "Date of Birth",
      "original_text": "January 1, 1990",
      "start_time": "00:00:40",
      "end_time": "00:00:50",
      "description": "Speaker mentions their birth date during a personal anecdote."
    }
  ]
}

Rules and Guidelines:
- Be as thorough as possible in identifying each piece of PII, ensuring you capture the exact spoken text.
- Document the full context surrounding each PII instance, describing how and why the information is mentioned in the audio.
- Provide precise timestamps for each identified PII, with both start and end times in HH:MM:SS format. If a piece of PII spans multiple seconds, provide the full time range.
- Classify only based on audio content—ignore any non-audio-based elements such as visual data or on-screen text.
- Do not alter or mask any details. Only document and categorize the PII.
- Ensure output format compliance. The result should be a clean and structured JSON format, with well-defined fields as described.
- IMPORTANT: Return ONLY valid JSON. Do not include any explanatory text before or after the JSON.

PII Categories to Detect:
"""
    
    try:
        print(f"Uploading file to Gemini API...")
        myfile = client.files.upload(file=audio_path)
        
        print(f"Generating content with Gemini...")
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[audio_prompt + pii_category, myfile]
        )
        
        print("=" * 50)
        print("RAW GEMINI RESPONSE:")
        print(response.text)
        print("=" * 50)
        
        # Parse the JSON response
        try:
            # Try to extract JSON from response
            pii_data = extract_json(response.text)


            # Normalize categories: Convert user input string → clean Python list
            if isinstance(pii_category, str):
                pii_category = pii_category.replace("[", "").replace("]", "").replace('"', "")
                pii_category = [cat.strip().lower() for cat in pii_category.split(",")]

            print("User-selected categories:", pii_category)

            # Filter detected PII based on categories
            filtered_pii = []
            for pii in pii_data["detected_pii"]:
                pii_type = pii.get("type", "").lower()
                if any(cat in pii_type for cat in pii_category):   # partial match
                    filtered_pii.append(pii)

            print("Filtered PII (after category match):", filtered_pii)



            # Replace original with filtered
            pii_data["detected_pii"] = filtered_pii

            print("Successfully extracted JSON from response")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Failed to parse JSON: {e}")
            print("Attempting alternative parsing...")
            # Try to find JSON between curly braces
            try:
                start_idx = response.text.index("{")
                end_idx = response.text.rindex("}") + 1
                json_str = response.text[start_idx:end_idx]
                pii_data = json.loads(json_str)
                print("Successfully parsed JSON using alternative method")
            except (ValueError, json.JSONDecodeError) as e2:
                print(f"All parsing attempts failed: {e2}")
                raise ValueError(f"Could not parse JSON from Gemini response. Response was: {response.text[:500]}")
        
        print(f"Parsed PII data: {json.dumps(pii_data, indent=2)}")
        
        # Validate the structure
        if not isinstance(pii_data, dict) or "detected_pii" not in pii_data:
            raise ValueError(f"Invalid PII data structure. Expected dict with 'detected_pii' key, got: {type(pii_data)}")
        
        # Generate output filename
        base_name = os.path.basename(audio_path)
        name_without_ext = os.path.splitext(base_name)[0]
        audio_output_path = os.path.join(PROCESSED_FOLDER, f"{name_without_ext}_processed.wav")
        
        # Apply masking
        print(f"Applying {highlight_mode} masking...")
        apply_audio_masking(audio_path, audio_output_path, pii_data)
        
        print(f"=== Audio Processing Completed Successfully ===")
        print(f"Output file: {audio_output_path}")
        
        return audio_output_path
        
    except Exception as e:
        print(f"ERROR in process_audio: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise