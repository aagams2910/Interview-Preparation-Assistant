import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

st.set_page_config(page_title="Interview Question Generator")
st.title("Interview Question Generator")

# Retrieve the Google API key from Streamlit secrets
api_key = st.secrets["GOOGLE_API_KEY"]

# Text area for job profile input
job_profile_text = st.text_area("Paste the Job Profile Text Here:")

# Define the prompt template
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

def get_interview_questions(job_profile_text):
    # Configure the Google Generative AI API with the key from secrets
    genai.configure(api_key=api_key)
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest")  # Use the compatible model
    
    prompt = PromptTemplate(input_variables=["job_profile_text"], template=prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)

    return chain.run({"job_profile_text": job_profile_text})

if st.button("Generate Interview Questions") and job_profile_text.strip():
    questions = get_interview_questions(job_profile_text)
    st.write("### Generated Interview Questions:")
    st.write(questions)
