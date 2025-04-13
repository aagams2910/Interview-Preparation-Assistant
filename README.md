# Advanced Interview Question Generator

This application generates tailored interview questions based on job descriptions. It leverages Google's Gemini 1.5 model to create relevant questions for assessment.

## Features

- **Question Categories**: Generate questions across technical, behavioral, situational, and experience-based categories
- **Difficulty Levels**: Choose between beginner, intermediate, and advanced difficulty settings
- **Number of Questions**: Specify exactly how many questions you need
- **Save Functionality**: Download generated questions as PDF or text files
- **Topic Focus**: Extract and focus on specific skills mentioned in the job description
- **Candidate Profile Matching**: Upload a candidate's resume to generate personalized questions
- **Interview Structure**: Generate a complete interview plan with opening, main, and closing questions
- **Question Scoring Rubric**: Include evaluation criteria alongside questions

## Setup Instructions

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.streamlit/secrets.toml` file with your Google API key:
   ```
   GOOGLE_API_KEY = "your-api-key-here"
   ```
4. Run the application:
   ```
   streamlit run main.py
   ```

## How to Use

1. **Paste Job Description**: Input the job profile text in the provided text area
2. **Extract Skills**: Click "Extract Skills from Job" to automatically identify key skills
3. **Upload Resume** (Optional): Upload a candidate's resume to generate personalized questions
4. **Configure Questions**:
   - Select question categories
   - Choose difficulty level
   - Set number of questions
   - Choose to include interview structure and/or evaluation rubric
5. **Generate Questions**: Click the "Generate Interview Questions" button
6. **Download**: Save the generated questions as PDF or text file

## Requirements

- Python 3.7+
- Google Gemini API key
- See requirements.txt for full dependency list

