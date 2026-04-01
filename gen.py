import google.generativeai as genai
import os
import json
import time
from google.api_core import exceptions

# Configuration
api_key = "AIzaSyDEsD1fZ1DTz2hW5Yq9J0mammXEJ3rX5VE"
genai.configure(api_key=api_key)

def extract_and_answer_questions(pdf_path):
    # 1. Upload File
    print(f"Uploading '{pdf_path}' to Gemini...")
    document = genai.upload_file(pdf_path)
    
    # Wait for the file to be processed by Google
    time.sleep(5) 

    # 2. Define Model and Prompt
    # Flash is recommended for Free Tier to avoid frequent 429 errors
    model = genai.GenerativeModel('gemini-2.5-pro')

    prompt = """
    I am using this document for my own personal exam preparation.
    Analyze the technical concepts in the attached workbook and transform them 
    into a structured JSON dataset.
    
    Rules:
    1. Extract every question, its options (if any), and the correct answer.
    2. Output strictly as a JSON array of objects.
    
    JSON Structure:
    [
      {
        "question": "text",
        "options": ["A", "B", "C", "D"],
        "answer": "correct_val"
      }
    ]
    """

    # 3. Generation with Retry (Cooldown) Logic
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}: Analyzing document...")
            response = model.generate_content(
                [document, prompt],
                generation_config={"response_mime_type": "application/json"}
            )
            
            # If successful, delete file and return
            genai.delete_file(document.name)
            return response.text

        except (exceptions.ResourceExhausted, exceptions.ServiceUnavailable) as e:
            # This is where the cooldown happens
            wait_time = (2 ** attempt) + 5  # Exponential: 7s, 9s, 13s, 21s...
            print(f"Server busy or Quota hit. Cooldown for {wait_time} seconds...")
            time.sleep(wait_time)
            
        except Exception as e:
            genai.delete_file(document.name)
            raise e

    genai.delete_file(document.name)
    raise Exception("Max retries exceeded. Please check your API quota dashboard.")

if __name__ == "__main__":
    pdf_filename = "1._OS_WB.pdf"
    try:
        json_result = extract_and_answer_questions(pdf_filename)
        quiz_data = json.loads(json_result)

        print("\n--- Success! Mapped Quiz Data ---")
        print(json.dumps(quiz_data, indent=2))

    except Exception as e:
        print(f"An error occurred: {e}")