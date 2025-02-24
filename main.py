import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (e.g., GOOGLE_API_KEY)
load_dotenv()

st.set_page_config(page_title="Interview Question Generator")
st.title("Interview Question Generator")

# Text area for the user to provide the job profile text
job_profile_text = st.text_area("Paste the Job Profile Text Here:")

# Define the prompt template to generate interview questions based on the job profile
prompt_template = '''
You are an expert interviewer specialized in designing interview questions for specific job roles.
Based on the job profile description provided below, generate a list of interview questions that cover both technical and behavioral aspects.
Your questions should help assess a candidate's suitability for the role.

### Job Profile:
{job_profile_text}

### Interview Questions:
1.
2.
3.
4.
5.
'''

# Retrieve the API key from Streamlit secrets
api_key = st.secrets["GOOGLE_API_KEY"]

def get_interview_questions(job_profile_text):
    # Configure the Google Generative AI library with the API key
    genai.configure(api_key=api_key)
    # Initialize the LLM with the Gemini‑pro model
    llm = ChatGoogleGenerativeAI(model='gemini-pro')
    # Create the prompt using the job profile text
    prompt = PromptTemplate(
        input_variables=["job_profile_text"],
        template=prompt_template
    )
    # Create the LLMChain to run the prompt with the LLM
    chain = LLMChain(llm=llm, prompt=prompt)
    # Run the chain to generate the interview questions
    response = chain.run({"job_profile_text": job_profile_text})
    return response

# When the button is pressed and job profile text is provided, generate and display questions
if st.button("Generate Interview Questions") and job_profile_text.strip() != "":
    questions = get_interview_questions(job_profile_text)
    st.write("### Generated Interview Questions:")
    st.write(questions)
