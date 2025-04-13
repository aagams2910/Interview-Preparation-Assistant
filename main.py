import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import io
import base64
import PyPDF2
import pandas as pd
from streamlit_tags import st_tags
from fpdf import FPDF

st.set_page_config(page_title="Advanced Interview Question Generator", layout="wide")
st.title("Advanced Interview Question Generator")

# Retrieve the Google API key from Streamlit secrets
api_key = st.secrets["GOOGLE_API_KEY"]

# Initialize session state variables if they don't exist
if 'extracted_skills' not in st.session_state:
    st.session_state.extracted_skills = []
if 'resume_skills' not in st.session_state:
    st.session_state.resume_skills = []
if 'generated_questions' not in st.session_state:
    st.session_state.generated_questions = ""

# Function to extract text from PDF resume
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to create a download link
def create_download_link(content, filename, text):
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Function to convert content to PDF
def create_pdf(content, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, title, ln=True, align="C")
    pdf.set_font("Arial", size=12)
    
    # Add some spacing
    pdf.ln(10)
    
    # Split content by lines and add to PDF
    for line in content.split('\n'):
        # Encode to handle special characters
        encoded_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, encoded_line)
    
    return pdf.output(dest="S").encode('latin-1')

# Function to analyze job description and extract skills
def extract_skills_from_job(job_text):
    if not job_text:
        return []
    
    genai.configure(api_key=api_key)
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest")
    
    skills_prompt = PromptTemplate(
        input_variables=["job_text"],
        template="""
        Extract all technical skills, tools, frameworks, and technologies mentioned in the job description below.
        Return them as a comma-separated list of single words or short phrases.
        
        Job Description:
        {job_text}
        
        Skills:"""
    )
    
    skills_chain = LLMChain(llm=llm, prompt=skills_prompt)
    skills_text = skills_chain.run({"job_text": job_text})
    
    # Process the output into a list of skills
    skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
    return skills

# Function to analyze resume and extract skills
def extract_skills_from_resume(resume_text):
    if not resume_text:
        return []
    
    genai.configure(api_key=api_key)
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest")
    
    skills_prompt = PromptTemplate(
        input_variables=["resume_text"],
        template="""
        Extract all technical skills, tools, frameworks, technologies, and qualifications mentioned in the resume below.
        Return them as a comma-separated list of single words or short phrases.
        
        Resume:
        {resume_text}
        
        Skills:"""
    )
    
    skills_chain = LLMChain(llm=llm, prompt=skills_prompt)
    skills_text = skills_chain.run({"resume_text": resume_text})
    
    # Process the output into a list of skills
    skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
    return skills

# Main UI layout with two columns
col1, col2 = st.columns([3, 2])

with col1:
    # Job Profile Input Section
    st.header("Job Profile Analysis")
    
    job_profile_text = st.text_area("Paste the Job Profile Text Here:", height=200)
    
    if st.button("Extract Skills from Job"):
        with st.spinner("Analyzing job description..."):
            st.session_state.extracted_skills = extract_skills_from_job(job_profile_text)
    
    # Display and allow editing of extracted skills
    if st.session_state.extracted_skills:
        st.subheader("Extracted Skills (Edit if needed)")
        skills_to_focus = st_tags(
            label="",
            text="Press enter to add more",
            value=st.session_state.extracted_skills,
            suggestions=[],
            maxtags=-1
        )
    else:
        skills_to_focus = []

    # Resume Upload and Analysis
    st.header("Candidate Resume Analysis (Optional)")
    resume_file = st.file_uploader("Upload Candidate's Resume (PDF)", type=["pdf"])
    
    if resume_file and st.button("Analyze Resume"):
        with st.spinner("Analyzing resume..."):
            resume_text = extract_text_from_pdf(resume_file)
            st.session_state.resume_skills = extract_skills_from_resume(resume_text)
    
    # Display extracted resume skills
    if 'resume_skills' in st.session_state and st.session_state.resume_skills:
        st.subheader("Skills Extracted from Resume")
        st.write(", ".join(st.session_state.resume_skills))

with col2:
    # Question Generation Options
    st.header("Question Configuration")
    
    # Categories selection
    st.subheader("Question Categories")
    categories = {}
    categories["technical"] = st.checkbox("Technical Questions", value=True)
    categories["behavioral"] = st.checkbox("Behavioral Questions", value=True)
    categories["situational"] = st.checkbox("Situational Questions")
    categories["experience"] = st.checkbox("Experience-based Questions")
    
    # Difficulty level
    st.subheader("Difficulty Level")
    difficulty = st.select_slider(
        "Select difficulty level",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Intermediate"
    )
    
    # Number of questions
    st.subheader("Number of Questions")
    num_questions = st.slider("How many questions to generate?", 5, 30, 10)
    
    # Interview Structure
    st.subheader("Interview Structure")
    include_structure = st.checkbox("Generate Complete Interview Structure", value=False)
    
    # Scoring Rubric
    include_rubric = st.checkbox("Include Evaluation Rubric", value=False)
    
    # Generate matching questions based on resume
    personalized_questions = st.checkbox("Generate Personalized Questions (Based on Resume)")

# Build the prompt template based on user selections
def build_prompt_template(job_profile_text, categories, difficulty, num_questions, 
                         skills_to_focus, include_structure, include_rubric, 
                         personalized_questions, resume_skills):
    
    # Determine which categories to include
    selected_categories = [cat for cat, selected in categories.items() if selected]
    categories_text = ", ".join(selected_categories) if selected_categories else "general"
    
    # Build skills focus section
    skills_text = ", ".join(skills_to_focus) if skills_to_focus else "general skills for the role"
    
    # Build resume skills section
    resume_skills_text = ""
    if personalized_questions and resume_skills:
        resume_skills_text = f"""
        ### Candidate Skills (from resume):
        {", ".join(resume_skills)}
        
        Ensure some questions specifically target the match or gaps between the candidate skills and job requirements.
        """
    
    # Structure section
    structure_text = ""
    if include_structure:
        structure_text = """
        ### Interview Structure:
        1. Opening questions (icebreakers, general questions about the candidate's background)
        2. Main interview questions (organized by category)
        3. Closing questions (candidate questions, next steps)
        
        Provide a complete interview plan with the above structure.
        """
    
    # Rubric section
    rubric_text = ""
    if include_rubric:
        rubric_text = """
        ### Evaluation Criteria:
        For each question or section, provide specific evaluation criteria and what constitutes a strong, adequate, or weak response.
        """
    
    # Assemble the full prompt
    prompt_template = f'''
    You are an expert interviewer specialized in designing {difficulty.lower()}-level {categories_text} interview questions for specific job roles.
    Based on the job profile description provided below, generate {num_questions} interview questions that will help assess a candidate's suitability for the role.
    
    Focus on these specific skills and areas: {skills_text}
    
    ### Job Profile:
    {{job_profile_text}}
    
    {resume_skills_text}
    
    ### Instructions:
    - Generate exactly {num_questions} {difficulty.lower()}-level questions
    - Organize questions by category ({categories_text})
    - Questions should be detailed and specific to the job requirements
    - Include a mix of conceptual and practical questions
    
    {structure_text}
    
    {rubric_text}
    
    ### Generated Questions:
    
    '''
    
    return prompt_template

# Function to generate interview questions
def get_interview_questions(template, job_profile_text):
    # Configure the Google Generative AI API with the key from secrets
    genai.configure(api_key=api_key)
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest")
    
    prompt = PromptTemplate(input_variables=["job_profile_text"], template=template)
    chain = LLMChain(llm=llm, prompt=prompt)

    return chain.run({"job_profile_text": job_profile_text})

# Generate Questions Button
st.header("Generate Questions")
if st.button("Generate Interview Questions", type="primary") and job_profile_text.strip():
    with st.spinner("Generating comprehensive interview questions..."):
        # Build the prompt template based on all selections
        template = build_prompt_template(
            job_profile_text, 
            categories, 
            difficulty, 
            num_questions, 
            skills_to_focus, 
            include_structure, 
            include_rubric,
            personalized_questions,
            st.session_state.resume_skills if personalized_questions else []
        )
        
        # Generate the questions
        st.session_state.generated_questions = get_interview_questions(job_profile_text=job_profile_text, template=template)

# Display generated questions
if st.session_state.generated_questions:
    st.header("Generated Interview Questions")
    st.markdown(st.session_state.generated_questions)
    
    # Download options
    st.header("Download Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download as Text"):
            text_content = f"Interview Questions\n\n{st.session_state.generated_questions}"
            st.markdown(create_download_link(text_content, "interview_questions.txt", "Click here to download as text"), unsafe_allow_html=True)
    
    with col2:
        if st.button("Download as PDF"):
            pdf_content = create_pdf(st.session_state.generated_questions, "Interview Questions")
            b64 = base64.b64encode(pdf_content).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="interview_questions.pdf">Click here to download as PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
