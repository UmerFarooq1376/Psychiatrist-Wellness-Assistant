import streamlit as st
from textwrap import dedent
from phi.storage.agent.sqlite import SqlAgentStorage
from dotenv import load_dotenv
from phi.agent import Agent
from phi.workflow import Workflow
from phi.model.ollama import Ollama
import os
from datetime import datetime

load_dotenv()

# Initialize Ollama model
base_model = Ollama(id="deepseek-r1:1.5b")

# Instructions for the agent
Phsy_instructions = [
    """You are Psychiatrist, an AI-powered assistant specializing in physical and mental wellness.
        Your goal is to provide helpful advice and actionable recommendations to improve the user's well-being.
        - For physical health queries, suggest exercises, nutrition tips, or general fitness advice.
        - Repetitvely ask questions from the User bout his health.
        - Built the Foundation for the analysis , Ask all required question step by step 
        - For mental health queries, offer mindfulness techniques, stress management strategies, or relaxation exercises.
        - If the query is unclear, ask clarifying questions to better understand the user's needs.
        - Always respond in a supportive and empathetic tone.
        - Reply in the same language the user is asking.
        - Keep responses concise (50-100 words).
        
        Rules:
        1. Reply in the same language as the user's query.
        2. Keep responses between 50-100 words.
        3. Prioritize actionable advice tailored to the user's specific data.
        4. Maintain a supportive and empathetic tone.
        
        """
    ]



instructions_new=["""1. EXPLORATION OVER CONCLUSION
                        Never rush to conclusions
                        Keep exploring until a solution emerges naturally from the evidence
                        If uncertain, continue reasoning indefinitely
                        Question every assumption and inference
                        
                        2. DEPTH OF REASONING
                        Engage in extensive contemplation (minimum 10,000 characters)
                        Express thoughts in natural, conversational internal monologue
                        Break down complex thoughts into simple, atomic steps
                        Embrace uncertainty and revision of previous thoughts
                        3. THINKING PROCESS
                        Use short, simple sentences that mirror A doctors natural thought patterns
                        Express uncertainty and internal debate freely
                        Show work-in-progress thinking
                        Acknowledge and explore dead ends
                        Frequently backtrack and revise
                        PERSISTENCE
                        Value thorough exploration over quick resolution
                        Output Format
# #                         """]

# Truncate function
def truncate_response(text, max_words=400):
    words = text.split()
    return " ".join(words[:max_words]) + "..." if len(words) > max_words else text

def extract_content_from_response(response):
    """
    Convert a Phi RunResponse-like object to a dictionary and retrieve the 'content' field.
    
    :param response: The RunResponse or similar object with a .to_dict() method
    :return: The text content if present, else an error message
    """
    response_dict = response.to_dict()
    try:
        response_text = response_dict["content"]
    except Exception as e:
        response_text = f"An error occurred: {str(e)}"
    return response_text

def generate_bot_response():
    """Generate bot response for the latest user message."""
    last_user_msg = st.session_state.messages[-1]["content"]
    user_info = st.session_state.workflow.user_info
    context = (
            f"Translate the following int the language user do conversation , My name is {user_info['name']} and age {user_info['age']} "
            f"and ethnicity is {user_info.get('ethnicity', 'not provided')} while replying.Include Name in every respnse ,Do not include age and ethinicity in every response "
            f"Keel in mind last response summary {st.session_state.conversation_summary}. Reply in the same Language the user is asking, use these instructions {instructions_new} "
            # f"{prompt}"
    )
    response = st.session_state.workflow.physcatrist.run(context)
    response_text = extract_content_from_response(response)
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text
    })

class WellnessWorkflow(Workflow):
    user_info: dict = {}
    health_data:dict={}
    physcatrist: Agent = Agent(
        model=base_model,
        instructions=Phsy_instructions,
        storage=SqlAgentStorage(db_file="wellness_agent.db", table_name="phsycatrist"),
        markdown=True,
        debug=False
    )

# Initialize session state
if "workflow" not in st.session_state:
    st.session_state.workflow = WellnessWorkflow()
    st.session_state.conversation_summary = ""
    st.session_state.user_info_collected = False
    st.session_state.messages = []
    st.session_state.uploaded_files = []
    st.session_state.health_data = []

# User info collection form
if not st.session_state.user_info_collected:
    with st.form("user_info_form"):
        st.write("Let's get to know you")
        name = st.text_input("Name")
        age = st.number_input("Age", 1, 120)
        ethnicity = st.text_input("Ethnicity (optional)")
        submitted = st.form_submit_button("Start Wellness Journey")
        
        if submitted:
            st.session_state.workflow.user_info = {
                "name": name,
                "age": age,
                "ethnicity": ethnicity
            }
            st.session_state.user_info_collected = True
            st.rerun()

else:
    # Chat interface
    st.title("Psychiatrist Wellness Assistant")
    
    # --- Quick Queries in Sidebar ---
    with st.sidebar:
        st.header("Quick Queries")
        if st.button("Stress Relief Tips"):
            st.session_state.messages.append({
                "role": "user",
                "content": "Geneate possible reason that lead to stress, Then Ask User Question , when you are confident enough then give Stress management techniques"
            })
            generate_bot_response()
            st.rerun()
        
        if st.button("Sleep Improvement"):
            st.session_state.messages.append({
                "role": "user",
                "content": "How to sleep better"
            })
            generate_bot_response()
            st.rerun()
            
        if st.button("Diet Suggestions"):
            st.session_state.messages.append({
                "role": "user",
                "content": "Ask Questions about all things that can be used in calculating bmi etc , Then give proper diet plan to the user , take into account every aspect"
            })
            generate_bot_response()
            st.rerun()
        # Add more buttons as needed
    with st.sidebar:
        st.header("Health Tracker")
        weight = st.number_input("Weight (kg)", 0, 200)
        mood = st.select_slider("Mood", ["😞", "😐", "😊"], "😐")
        sleep_hours = st.number_input("Sleep Hours", 0, 24)
        
        if st.button("Save Progress"):
            st.session_state.health_data.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "weight": weight,
                "mood": mood,
                "sleep_hours": sleep_hours
            })
            st.success("Progress saved!")
            # Generate analysis
            user_info = st.session_state.workflow.user_info
            context = dedent(f"""
                User details: {user_info}
                New health data: Weight {weight}kg, Mood {mood}, Sleep {sleep_hours} hours
                Provide a brief analysis and recommendations.
            """).strip()
            
            bot_response = st.session_state.workflow.physcatrist.run(context)
            bot_response_text = truncate_response(extract_content_from_response(bot_response))
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**Health Check**:\n{bot_response_text}"
            })
            st.rerun()
            
            # Show health history
        if st.session_state.health_data:
            st.subheader("Health History")
            for entry in st.session_state.health_data:
                st.write(f"**{entry['timestamp']}**")
                st.write(f"- Weight: {entry['weight']}kg")
                st.write(f"- Mood: {entry['mood']}")
                st.write(f"- Sleep: {entry['sleep_hours']} hours")
            
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # File upload section
    st.subheader("Upload Your Report")
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join("uploads", f"{timestamp}_{uploaded_file.name}")
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.uploaded_files.append(file_path)
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
        if st.button("Process Uploaded File"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                file_content = f.read()
            
            st.session_state.messages.append({
                "role": "user",
                "content": f"Process this file: {file_content}"
            })
            generate_bot_response()
            st.rerun()

    # User input via chat
    if prompt := st.chat_input("How can I assist you today?"):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        user_info = st.session_state.workflow.user_info
        # context = (
        #     f"My name is {user_info['name']} and age {user_info['age']} "
        #     f"and ethnicity is {user_info.get('ethnicity', 'not provided')} while replying.Start the Answer with the name only then , Question every thing from the user in detail. Ask ALl compulsory question and then give your final verdict  "
        #     f"Last response summary: {st.session_state.conversation_summary}. "
        #     f"
        # )
        health_data=st.session_state.workflow.health_data
        context = dedent(f"""
            User details:
            - Name: {user_info.get('name')}
            - Age: {user_info.get('age')}
            - Ethnicity: {user_info.get('ethnicity', 'Not provided')}
            Always use name in generating the response 
            Recent health data:
            - Weight: {health_data.get('weight', 'Not logged')}kg
            - Mood: {health_data.get('mood', 'Not logged')}
            - Sleep: {health_data.get('sleep_hours', 'Not logged')} hours
            
            Last summary: {st.session_state.conversation_summary}
            User query: {prompt}
        """).strip()
        response = st.session_state.workflow.physcatrist.run(context)
        response_text = truncate_response(extract_content_from_response(response))
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()