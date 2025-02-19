#interview a
import streamlit as st
from openai import OpenAI
import os
from typing import List, Dict

# Configuration
MAX_QUESTIONS = 5  # Configurable interview length
DEFAULT_TEMPERATURE = 0.7
SYSTEM_ROLES = {
    "interviewer": "You are an experienced technical interviewer assessing candidates based on their responses. Ask challenging but fair questions.",
    "feedback": "You are a career coach providing constructive feedback. Highlight strengths and suggest improvements."
}

# Initialize OpenAI client securely
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))

def get_ai_response(prompt: str, role: str, temperature: float = DEFAULT_TEMPERATURE) -> str:
    """Generic function to handle OpenAI API calls with error handling."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_ROLES[role]},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error accessing OpenAI API: {str(e)}")
        st.stop()

def generate_interview_question(job_desc: str, conversation_history: List[Dict]) -> str:
    """Generate context-aware interview question."""
    base_prompt = f"Job Description:\n{job_desc}\n\n"
    
    if conversation_history:
        history_context = "\n".join(
            [f"Question: {item['question']}\nAnswer: {item['answer']}" 
             for item in conversation_history if item['answer']]
        )
        base_prompt += f"Conversation History:\n{history_context}\n\n"
    
    base_prompt += "Generate the next relevant interview question. Focus on technical skills and behavioral aspects."
    return get_ai_response(base_prompt, "interviewer")

def provide_feedback(question: str, answer: str) -> str:
    """Generate structured feedback for candidate response."""
    evaluation_prompt = (
        "Evaluate this interview response using this structure:\n"
        "1. Content Quality (0-5)\n"
        "2. Communication (0-5)\n"
        "3. Improvement Suggestions\n"
        "4. Strength Highlights\n\n"
        f"Question: {question}\nAnswer: {answer}"
    )
    return get_ai_response(evaluation_prompt, "feedback")

# Session State Management
def initialize_session():
    """Initialize or reset session state"""
    st.session_state.update({
        "job_desc": None,
        "conversation": [],
        "current_turn": 0,
        "interview_active": False
    })

def render_interview_progress():
    """Show progress bar and question counter"""
    progress = min(st.session_state.current_turn / MAX_QUESTIONS, 1.0)
    st.progress(progress)
    st.caption(f"Question {st.session_state.current_turn + 1} of {MAX_QUESTIONS}")

# UI Components
def main():
    st.title("📝 Interview Preparation Coach")
    st.markdown("Practice your interview skills with AI-powered questions and feedback.")
    
    # Initialize session
    if "conversation" not in st.session_state:
        initialize_session()

    # Job Description Input
    if not st.session_state.job_desc:
        with st.form("job_desc_form"):
            job_desc = st.text_area("Paste the job description:", height=150)
            if st.form_submit_button("Start Practice Session"):
                if job_desc.strip():
                    st.session_state.job_desc = job_desc
                    st.session_state.interview_active = True
                    st.rerun()
                else:
                    st.error("Please enter a job description to continue")

    # Interview Interface
    else:
        render_interview_progress()
        
        # Show conversation history
        for idx, turn in enumerate(st.session_state.conversation):
            with st.expander(f"Question {idx + 1}", expanded=(idx == st.session_state.current_turn)):
                st.markdown(f"**Interviewer:** {turn['question']}")
                if turn['answer']:
                    st.markdown(f"**Your Answer:** {turn['answer']}")
                if turn['feedback']:
                    st.markdown(f"**Feedback:**\n{turn['feedback']}")
        
        # Current question handling
        if st.session_state.current_turn < MAX_QUESTIONS:
            current_q = st.session_state.conversation[st.session_state.current_turn]
            
            with st.form("answer_form"):
                answer = st.text_area("Type your response here:", height=150)
                if st.form_submit_button("Submit Answer"):
                    if answer.strip():
                        # Get feedback and store answer
                        current_q['answer'] = answer
                        with st.spinner("Analyzing your response..."):
                            current_q['feedback'] = provide_feedback(current_q['question'], answer)
                        
                        # Generate next question if needed
                        if st.session_state.current_turn < MAX_QUESTIONS - 1:
                            with st.spinner("Preparing next question..."):
                                next_q = generate_interview_question(
                                    st.session_state.job_desc,
                                    st.session_state.conversation
                                )
                                st.session_state.conversation.append({
                                    "question": next_q,
                                    "answer": None,
                                    "feedback": None
                                })
                                st.session_state.current_turn += 1
                        st.rerun()
                    else:
                        st.error("Please provide a response before submitting")
        else:
            st.success("🎉 Interview complete! Review your feedback below.")
            if st.button("Start New Session"):
                initialize_session()
                st.rerun()

if __name__ == "__main__":
    main()