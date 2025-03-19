# Flashcard Maker

A command-line tool that automatically generates study flashcards from your text and PDF files using Google's Gemini AI.

## Features

- Extract content from TXT and PDF files
- Automatically generate question-answer flashcards using Google's Gemini AI
- Customize the number of flashcards to generate (1-75)
- Export flashcards as print-ready PDF files
- Double-sided cards optimized for printing

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/flashcardmaker.git
   cd flashcardmaker
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Get a Gemini API key from [Google AI Studio](https://ai.google.dev/)

## Usage

1. Place your study materials (TXT or PDF files) in the `uploads` folder
2. Run the console application:
   ```
   python console_flashcard_maker.py
   ```
3. Enter your Gemini API key when prompted
4. Select the file you want to process
5. Choose how many flashcards to generate
6. The generated flashcards will be saved as a PDF in the `output` folder

## Printing Instructions

For best results when printing the generated PDF:
- Use double-sided printing
- Select "flip on short edge" in your printer settings

## Requirements

- Python 3.8+
- Google Gemini API key
- Dependencies:
  - flashcard-generator==0.1.0
  - werkzeug==2.3.7
  - google-generativeai==0.3.1
  - PyPDF2>=3.0.0
  - reportlab>=3.6.0

## Example

After running the application, you'll get a PDF with flashcards that look like:

**Front:**
What is the capital of France?

**Back:**
Paris

## Project Structure

- `console_flashcard_maker.py`: Main application file
- `flashcard_generator.py`: Handles PDF generation
- `aiResponse.py`: Manages communication with Google's Gemini API
- `uploads/`: Place your study materials here
- `output/`: Generated PDFs are saved here

## License

MIT License