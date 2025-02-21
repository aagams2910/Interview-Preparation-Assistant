import streamlit as st
import openai
import os
from openai import ChatCompletion  # Import the endpoint directly

# Set your OpenAI API key; you can use an environment variable or Streamlit secrets.
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

def generate_interview_preparation(job_role: str) -> str:
    """
    Generates interview preparation content for the given job role using OpenAI's ChatCompletion.
    """
    # Build the prompt for generating interview questions, sample answers, and tips
    prompt = (
        f"Act as an interview preparation assistant. "
        f"Provide a list of common interview questions and well-explained sample answers "
        f"for the position of {job_role}. Also include some tips on how to approach each question."
    )
    
    try:
        # Call the ChatCompletion API using the new interface
        response = ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert interview preparation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Adjust creativity as needed
            max_tokens=500    # Adjust the output length as needed
        )
        # Extract and return the assistant's reply
        return response.choices[0].message['content'].strip()
    
    except Exception as e:
        return f"An error occurred: {e}"

# Streamlit UI setup
st.title("Interview Preparation Assistant Bot")

# Text input for the job role
job_role = st.text_input("Enter the job role", "")

if st.button("Generate Interview Prep"):
    if not job_role.strip():
        st.error("Please provide a valid job role.")
    else:
        st.info("Generating interview preparation content...")
        result = generate_interview_preparation(job_role)
        st.success("Interview Preparation Content:")
        st.write(result)
