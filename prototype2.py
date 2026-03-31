import google.generativeai as genai
import json
import time
import os


api_key = "AIzaSyC8231rSgb1jpP3hp83fHNf_PI5hUxHTWM"  
genai.configure(api_key=api_key)

def process_workbook_with_taxonomy(pdf_path, csv_path, output_json_path):
    # 1. Read the Taxonomy CSV
    print(f"1. Reading taxonomy from '{csv_path}'...")
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            taxonomy_data = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Taxonomy file '{csv_path}' not found.")
        return

    # 2. Upload the PDF
    print(f"2. Uploading '{pdf_path}' to Gemini...")
    try:
        document = genai.upload_file(pdf_path)
        print(f"   File uploaded successfully. URI: {document.uri}")
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return

    # Wait briefly for backend processing
    time.sleep(3) 

    # We use gemini-2.5-flash as it is highly capable for multimodal document processing
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 3. Define the Prompt (Injecting the CSV data)
    prompt = f"""
    You are an expert educational assistant. Read the attached PDF document containing a list of questions.
    
    You are also provided with a classification taxonomy in CSV format here:
    --- START TAXONOMY ---
    {taxonomy_data}
    --- END TAXONOMY ---
    
    Your task:
    1. Extract every question from the document serially.
    2. Provide a concise, accurate answer for each extracted question.
    3. Extract the options for the questions that have options.
    4. There can be single correct answer or multiple correct answers or Numerical answers.
    5. Provide the answer to the question where the Numerical answer is given.
    6. Provide the correct option/s where the single correct/multiple correct answers are given.
    7. Classify each of the questions on the basis of the difficulty.
    8. Add the explanation from the pdf document to the answer under the heading explanation.
    9. If the solution is given in the pdf document, add the solution to the answer under the heading solution.
    10. If the solution is not given in the pdf document, generate the solution as a string under the heading solution that should be precise and accurate.
    11. Scan the taxonomy spreadsheet and add the subject, chapter, topic, and subtopic of the question.
    
    Output the final data STRICTLY as a JSON array of objects. 
    Do not include markdown blocks (like ```json), just the raw JSON array.
    
    Use this EXACT JSON structure:
    [
      {{
        "question": "The exact text of the extracted question?",
        "options": [
          "Option A",
          "Option B",
          "Option C",
          "Option D"
        ],
        "correct_answer": "The correct answer text.",
        "difficulty_level": "Medium",
        "explanation": "The explanation extracted from the document, or null if none.",
        "solution": "The solution extracted from the document or accurately generated.",
        "subject": "Subject Name strictly from CSV",
        "chapter": "Chapter Name strictly from CSV",
        "topic": "Topic Name strictly from CSV",
        "subtopic": "Subtopic Name strictly from CSV"
      }}
    ]
    """

    print("3. Analyzing document, extracting questions, and applying CSV taxonomy...")
    try:
        # Enforce JSON output formatting
        response = model.generate_content(
            [document, prompt],
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse the response text into a Python list
        quiz_data = json.loads(response.text)
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        
        # Save to the output JSON file
        print(f"4. Exporting data to '{output_json_path}'...")
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, indent=4)
            
        print(f"\n✅ Success! Extracted and classified {len(quiz_data)} questions.")
        print(f"Data successfully saved to: {output_json_path}")

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON. The model might have returned malformed text. Error: {e}")
        print("Raw output:")
        print(response.text)
    except Exception as e:
        print(f"❌ An error occurred during generation: {e}")
    finally:
        # Clean up the file from Google's servers to save space
        print("5. Cleaning up uploaded file...")
        try:
            genai.delete_file(document.name)
            print("   Cleanup complete.")
        except Exception as e:
            print(f"   Cleanup failed: {e}")

if __name__ == "__main__":
    # FIX 1: Use 'r' before Windows paths to treat backslashes correctly
    pdf_filename = r"C:\Users\Karamjeet\OneDrive\Desktop\New folder\Project\algo1.pdf" 
    csv_filename = r"C:\Users\Karamjeet\OneDrive\Desktop\New folder\Project\subject_taxonomy.csv"
    
    # Using absolute path for output to avoid working directory confusion
    output_filename = r"C:\Users\Karamjeet\OneDrive\Desktop\New folder\Project\algo_workbook_classified.json"
    
    # Check if necessary files exist before running
    if not os.path.exists(pdf_filename):
        print(f"Error: The PDF file '{pdf_filename}' does not exist.")
    elif not os.path.exists(csv_filename):
        print(f"Error: The CSV file '{csv_filename}' does not exist.")
    else:
        process_workbook_with_taxonomy(pdf_filename, csv_filename, output_filename)
