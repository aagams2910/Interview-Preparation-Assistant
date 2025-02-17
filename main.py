import streamlit as st
from openai import OpenAI
import os

client = OpenAI(api_key="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")
#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

# Function to generate an interview question based on job description and (optional) last answer.
def generate_interview_question(job_desc, last_answer=""):
    prompt = f"Based on the following job description:\n{job_desc}\n"
    if last_answer:
        prompt += f"Considering the candidate's last answer: {last_answer}\n"
    prompt += "Please provide a relevant interview question for the candidate."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an interview assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    # Access the content using the new response model.
    question = response.choices[0].message.content.strip()
    return question

# Function to provide feedback on the candidate's answer.
def provide_feedback(question, answer):
    prompt = (f"Interview question: {question}\n"
              f"Candidate's answer: {answer}\n"
              "Provide constructive feedback and suggestions for improvement.")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an experienced interviewer providing feedback."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    feedback = response.choices[0].message.content.strip()
    return feedback

# Initialize session state variables.
if "job_desc" not in st.session_state:
    st.session_state.job_desc = None
if "conversation" not in st.session_state:
    st.session_state.conversation = []  # Each element: {"question": str, "answer": str or None, "feedback": str or None}
if "current_turn" not in st.session_state:
    st.session_state.current_turn = 0

st.title("Interview Preparation Assistant")
st.write("Simulate interview scenarios and get feedback on your answers.")

# Step 1: Enter the job description.
if st.session_state.job_desc is None:
    job_desc = st.text_area("Enter the Job Description:", height=150)
    if st.button("Start Interview"):
        if job_desc.strip():
            st.session_state.job_desc = job_desc
            # Generate the first question.
            first_question = generate_interview_question(job_desc)
            st.session_state.conversation.append({
                "question": first_question,
                "answer": None,
                "feedback": None
            })
            st.session_state.current_turn = 0
            st.experimental_rerun()
        else:
            st.error("Please enter a valid job description.")
else:
    st.write("### Interview Simulation")
    # Display conversation history.
    for turn in st.session_state.conversation:
        st.markdown(f"**Interviewer:** {turn['question']}")
        if turn["answer"]:
            st.markdown(f"**Your Answer:** {turn['answer']}")
        if turn["feedback"]:
            st.markdown(f"**Feedback:** {turn['feedback']}")
        st.markdown("---")

try:
    first_question = generate_interview_question(job_desc)
except OpenAI.RateLimitError as e:
    st.error("Rate limit exceeded: please check your plan and billing details.")
    st.stop()

current_turn = st.session_state.current_turn
if st.session_state.conversation and current_turn < len(st.session_state.conversation):
    if st.session_state.conversation[current_turn]["answer"] is None:
        # Show input for the current unanswered question
        answer = st.text_area("Your Answer", key="answer_input")
        if st.button("Submit Answer"):
            if not answer.strip():
                st.error("Please provide an answer.")
            else:
                question = st.session_state.conversation[current_turn]["question"]
                feedback = provide_feedback(question, answer)
                st.session_state.conversation[current_turn]["answer"] = answer
                st.session_state.conversation[current_turn]["feedback"] = feedback
                # Generate a follow-up question
                next_question = generate_interview_question(st.session_state.job_desc, answer)
                st.session_state.conversation.append({
                    "question": next_question,
                    "answer": None,
                    "feedback": None
                })
                st.session_state.current_turn += 1
                st.experimental_rerun()
else:
    st.write("No active conversation found. Please start the interview first.")
    
    if st.button("Reset Interview"):
        st.session_state.job_desc = None
        st.session_state.conversation = []
        st.session_state.current_turn = 0
        st.experimental_rerun()