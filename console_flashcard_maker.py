import os
import re
import json
import time
import glob
from flashcard_generator import FlashCardGenerator
from aiResponse import geminiResponse

def extract_text_from_file(filepath, filename):
    """Extract text from different file types"""
    try:
        # For PDF files
        if filename.lower().endswith('.pdf'):
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
                return text
            except ImportError:
                print("Error: PyPDF2 library is required to read PDF files.")
                print("Install it with 'pip install PyPDF2'")
                exit(1)
        
        else:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
                
    except Exception as e:
        print(f"Error extracting text from {filename}: {str(e)}")
        return None

def generate_flashcards_with_gemini(text, num_cards=10, max_retries=3):
    """
    Use Gemini API to automatically generate flashcards from study text
    Returns a list of tuples (front, back, extra)
    """
    max_text_length = 12000
    if (len(text) > max_text_length):
        text = text[:max_text_length] + "... [content truncated for processing]"
    
    prompt = f"""
    Create exactly {num_cards} flashcards from the following study material. 
    Each flashcard should have:
    1. A clear question or concept on the front
    2. A concise answer or explanation on the back

    Focus on the most important concepts in the material and try to cover different topics.
    Make sure each card has substantial content on both front and back sides.
    Be concise but thorough in your responses.

    For example:
    Q: What is the capital of France?
    A: Paris

    Study material:
    {text}

    Format your response as a JSON array with objects containing only "front" and "back" fields.
    Ensure you generate exactly {num_cards} flashcards in total.
    The "back" field MUST contain substantive content for every card.
    Do not include any hints or extra information fields.
    """
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt+1} to generate flashcards")
            
            max_api_time = 45
            start_time = time.time()
            
            response_text = geminiResponse(prompt)
            
            if time.time() - start_time > max_api_time:
                print("API call took too long, aborting")
                raise TimeoutError("API call timed out")
                
            try:
                json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
                if json_match:
                    cards_json = json.loads(json_match.group(0))
                    flashcards = []
                    for i, card in enumerate(cards_json):
                        front = (card.get('front') or "").strip()
                        back = (card.get('back') or "").strip()
                        if front and back:
                            flashcards.append((front, back, "", str(i+1)))
                    return flashcards
                else:
                    print("No JSON found in response")
                    return []
            except json.JSONDecodeError:
                print("JSON parsing failed")
                return []
            
        except TimeoutError as te:
            print(f"Timeout error: {te}")
            if attempt < max_retries - 1:
                print(f"Retrying ({attempt+2}/{max_retries})...")
            else:
                return []
        except Exception as e:
            print(f"Error generating flashcards: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                return []
    
    return []

def main():
    uploads_dir = 'uploads'
    output_dir = 'output'
    os.makedirs(uploads_dir, exist_ok=True)
    
    print("\n===== Flashcard Generator =====")
    print("This tool will create flashcards from text or PDF files in your uploads folder.")
    
    api_key = input("\nEnter your Gemini API key: ").strip()
    if not api_key:
        print("API key is required to generate flashcards.")
        return
    
    os.environ["GEMINI_API_KEY"] = api_key
    
    print("\nScanning uploads folder...")
    txt_files = glob.glob(os.path.join(uploads_dir, "*.txt"))
    pdf_files = glob.glob(os.path.join(uploads_dir, "*.pdf"))
    all_files = txt_files + pdf_files
    
    if not all_files:
        print("No .txt or .pdf files found in the uploads folder.")
        print(f"Please add files to: {os.path.abspath(uploads_dir)}")
        return
    
    print("\nAvailable files:")
    for i, file_path in enumerate(all_files, 1):
        filename = os.path.basename(file_path)
        print(f"{i}. {filename}")
    
    selection = input("\nEnter the number of the file to process: ")
    try:
        file_index = int(selection) - 1
        if file_index < 0 or file_index >= len(all_files):
            print("Invalid selection.")
            return
        
        selected_file = all_files[file_index]
        filename = os.path.basename(selected_file)
        print(f"\nSelected: {filename}")
        
        try:
            num_cards = int(input("\nHow many flashcards do you want to generate? (1-75): "))
            if num_cards < 1 or num_cards > 75:
                print("Number of cards must be between 1 and 75.")
                return
        except ValueError:
            print("Please enter a valid number.")
            return
        
        print(f"\nExtracting text from {filename}...")
        text = extract_text_from_file(selected_file, filename)
        if not text:
            print("Failed to extract text from the file.")
            return
        
        text_preview = text[:200] + "..." if len(text) > 200 else text
        print(f"\nText preview: {text_preview}")
        
        print(f"\nGenerating {num_cards} flashcards...")
        flashcards = generate_flashcards_with_gemini(text, num_cards)
        
        if not flashcards:
            print("Failed to generate flashcards.")
            return
        
        print(f"\nSuccessfully generated {len(flashcards)} flashcards.")
        
        output_filename = f"{os.path.splitext(filename)[0]}_flashcards.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"\nGenerating PDF: {output_filename}")
        generator = FlashCardGenerator()
        generator.generate_pdf(flashcards, output_path)
        
        print(f"\nFlashcards saved to: {os.path.abspath(output_path)}")
        print("\nHere's a preview of your flashcards:")
        for i, (front, back, _, index) in enumerate(flashcards[:3], 1):
            print(f"\nCard {i}:")
            print(f"Front: {front}")
            print(f"Back: {back}")
        
        if len(flashcards) > 3:
            print(f"\n... and {len(flashcards) - 3} more cards in the PDF.")
        
    except ValueError:
        print("Please enter a valid number.")
        return
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return

if __name__ == "__main__":
    main()