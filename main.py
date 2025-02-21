import streamlit as st
from transformers import pipeline

# Set up the text-generation pipeline.
# Note: GPT-Neo-2.7B is used here; you can choose another model if preferred.
generator = pipeline('text-generation', model='EleutherAI/gpt-neo-2.7B')

st.title("Interview Preparation Assistant Bot")

# Input field for the job role
job_role = st.text_input("Enter the job role", "")

if st.button("Generate Interview Prep"):
    if not job_role.strip():
        st.error("Please provide a valid job role.")
    else:
        st.info("Generating interview preparation content...")
        prompt = (
            f"Act as an interview preparation assistant. "
            f"Provide a list of common interview questions and well-explained sample answers "
            f"for the position of {job_role}. Also include some tips on how to approach each question."
        )
        # Generate output using the text-generation pipeline
        output = generator(prompt, max_length=500, do_sample=True, temperature=0.7)
        st.success("Interview Preparation Content:")
        st.write(output[0]['generated_text'])
