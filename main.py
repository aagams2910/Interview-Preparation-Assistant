import streamlit as st
import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("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") 

def generate_interview_preparation(job_role: str) -> str:
    """
    Generates interview preparation content for the given job role using OpenAI's ChatCompletion.
    """
    # Construct a prompt to generate interview questions, sample answers, and tips
    prompt = (
        f"Act as an interview preparation assistant. "
        f"Provide a list of common interview questions and well-explained sample answers "
        f"for the position of {job_role}. Also include some tips on how to approach each question."
    )
    
    try:
        # Call the OpenAI ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can change to another model if needed
            messages=[
                {"role": "system", "content": "You are an expert interview preparation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Adjust for more/less creative responses
            max_tokens=500    # Adjust the output length as needed
        )
        return response.choices[0].message['content'].strip()
    
    except Exception as e:
        return f"An error occurred: {e}"

# Streamlit UI
st.title("Interview Preparation Assistant Bot")

# Input field for the job role
job_role = st.text_input("Enter the job role", "")

if st.button("Generate Interview Prep"):
    if not job_role.strip():
        st.error("Please provide a valid job role.")
    else:
        st.info("Generating interview preparation content...")
        result = generate_interview_preparation(job_role)
        st.success("Interview Preparation Content:")
        st.write(result)
