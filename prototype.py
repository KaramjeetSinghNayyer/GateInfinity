import google.generativeai as genai
import os
import json
import time

api_key = ""
genai.configure(api_key=api_key)

def extract_and_answer_questions(pdf_path):
    print(f"Uploading '{pdf_path}' to Gemini...")
    
    
    document = genai.upload_file(pdf_path)
    
    
    time.sleep(2) 

    
    model = genai.GenerativeModel('gemini-2.5-flash')

    
    prompt = """
    You are an expert educational assistant. Read the attached PDF document containing a list of questions.
    
    Your task:
    1. Extract every question from the document serially.
    2. Provide a concise, accurate answer for each extracted question.
    3. Extract the options for the questions that have options.
    4. There can be single correct answer or multiple correct answers or Numerical answers.
    5. Provide the answer to the question where the Numerical answer is given.
    6. Provide the correct option/s where the single correct/multiple correct answers are given.
    3. Output the final data strictly as a JSON array of objects.
    
    Use this exact JSON structure:
    [
      {
        "question": "The exact text of the question?",
        "options": [
          "The first option.",
          "The second option.",
          "The third option."
          "The fourth option."
        ],
        "answer": "The generated answer."
      },
      }
    ]
    """

    print("Analyzing document and generating answers...")
    
    
    response = model.generate_content(
        [document, prompt],
        generation_config={"response_mime_type": "application/json"}
    )

    
    genai.delete_file(document.name)

   
    return response.text


if __name__ == "__main__":
    
    pdf_filename = r""
    try:
        json_result = extract_and_answer_questions(pdf_filename)
        
       
        quiz_data = json.loads(json_result)
        
        print("\n--- Success! Mapped Quiz Data ---")
        print(json.dumps(quiz_data, indent=2))
        
    except FileNotFoundError:
        print(f"Error: Could not find the file '{pdf_filename}'. Please check the path.")
    except Exception as e:
        print(f"An error occurred: {e}")


