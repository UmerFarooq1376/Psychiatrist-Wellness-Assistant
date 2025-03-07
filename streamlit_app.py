import streamlit as st
from langdetect import detect
from textwrap import dedent
from phi.storage.agent.sqlite import SqlAgentStorage
from dotenv import load_dotenv
from phi.agent import Agent
from phi.workflow import Workflow
from phi.model.ollama import Ollama
import os
from datetime import datetime
from PyPDF2 import PdfReader
import webbrowser
from typing import Dict, List


load_dotenv()

# Initialize Ollama model
base_model = Ollama(id="llama3.1:latest")

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
        5. At the end make a bullet points of possible reasons 
         ** CALL THE DOCTOR IF USER ASK YOU TO MAKE A DOCTOR CONSULTATION **
        
        Additional Guidelines:
        - ** CALL THE DOCTOR IF USER ASK YOU TO MAKE A DOCTOR CONSULTATION **
        - If you detect severe symptoms or situations requiring professional medical attention,
          use the doctor_consultation_tool to connect the user with a specialist.
        - Recommend doctor consultation for:
          * Severe depression or anxiety symptoms
          * Suicidal thoughts
          * Complex mental health issues
          * Cases requiring medication
          * Situations beyond AI assistance scope
          
          - Don't Recommend doctor consultation for:
          * Diet plan queries
          * Personal health concerns that are not medical emergencies
        
        -** USE schedule_appointment_tool WHEN: **
          * User requests to schedule a future appointment
          * User wants to plan a consultation
          * User needs to book a specific time with a specialist
          * Follow-up appointments are needed
        
        - ** USE symptom_tracker_tool WHEN: **
          * User mentions new symptoms
          * User wants to track their mental health symptoms
          * User describes changes in their condition
          * Regular monitoring of ongoing health issues is needed
          * User reports anxiety, depression, or mood changes
          * Sleep pattern changes are reported
          * Physical symptoms that may relate to mental health
        
        When recommending a doctor:
        1. Explain why professional help is needed
        2. Call the doctor_consultation_tool with appropriate reason and urgency
        3. Continue providing support while arranging the consultation
        
        When scheduling appointments:
        1. Ask for preferred specialist type
        2. Inquire about preferred time
        3. Use schedule_appointment_tool to arrange the meeting
        4. Confirm the appointment details with the user

        When using symptom tracker:
        1. Ask specific questions about symptom intensity
        2. Inquire about symptom duration
        3. Request additional context or notes
        4. Use symptom_tracker_tool to log the information
        5. Review tracked symptoms to identify patterns
        6. Provide feedback based on tracked symptoms
    
        """ ]



instructions_new=["""You are Psychiatrist, an AI-powered assistant specializing in physical and mental wellness.
                        
                        IMPORTANT: Keep responses between 50-100 words.
                        At the end make a bullet points of possible reasons 
                        
                        1. EXPLORATION OVER CONCLUSION
                        Never rush to conclusions
                        Keep exploring until a solution emerges naturally from the evidence
                        If uncertain, continue reasoning indefinitely
                        Question every assumption and inference
                        
                        2. DEPTH OF REASONING
                        Engage in extensive contemplation (minimum 100 characters)
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
                        
                        Word limit(max 100 words)
                        
# #                         """]

# def doctor_consultation_tool(reason: str, urgency: str = "normal") -> Dict:
#     """
#     Tool for initiating doctor consultation when the AI determines it's necessary.
    
#     Args:
#         reason: The medical reason for consultation
#         urgency: Urgency level ("normal", "urgent", "emergency")
#     """
#     print("======= Calling Doctor ========")
    
#     st.subheader("🏥 Doctor Consultation Recommended")
#     st.write(f"Reason: {reason}")
#     st.write(f"Urgency: {urgency}")
    
#     doctors = {
#         "Dr. Smith (General Psychiatrist)": "+1-555-0123",
#         "Dr. Johnson (Anxiety Specialist)": "+1-555-0124",
#         "Dr. Williams (Depression Specialist)": "+1-555-0125"
#     }
    
#     call_type = st.radio("Select consultation method:", ["Phone Call", "Video Call"])
#     selected_doctor = st.selectbox("Choose a specialist:", list(doctors.keys()))
    
#     if st.button("Connect Now"):
#         phone_number = doctors[selected_doctor]
#         if call_type == "Phone Call":
#             webbrowser.open(f"tel:{phone_number}")
#         else:
#             st.info(f"Initiating video call with {selected_doctor}")
        
#         return {
#             "status": "success",
#             "doctor": selected_doctor,
#             "consultation_type": call_type,
#             "reason": reason
#         }
def call_doctor():
    """Handle doctor call functionality"""
    st.subheader("Contact a Doctor")
    call_type = st.radio("Select contact method:", ["Phone Call", "Video Call"])
    
    # Display available doctors
    doctors = {
        "Dr. Smith": "+1-555-0123",
        "Dr. Johnson": "+1-555-0124",
        "Dr. Williams": "+1-555-0125"
    }
    
    selected_doctor = st.selectbox("Choose a doctor:", list(doctors.keys()))
    
    if st.button("Connect Now"):
        phone_number = doctors[selected_doctor]
        if call_type == "Phone Call":
            # For phone calls, we use tel: protocol
            webbrowser.open(f"tel:{phone_number}")
        else:
            # For video calls, you might want to integrate with a telemedicine platform
            st.info(f"Initiating video call with {selected_doctor}")
            # Add your video call integration here
        
        st.success(f"Connecting you with {selected_doctor}")

#     return {"status": "pending"}
def doctor_consultation_tool(reason: str, urgency: str = "normal") -> str:
    """Tool for initiating doctor consultation"""
    if 'show_doctor_ui' not in st.session_state:
        st.session_state.show_doctor_ui = True
    
    if st.session_state.show_doctor_ui:
        st.subheader("🏥 Doctor Consultation Recommended")
        st.write(f"Reason: {reason}")
        st.write(f"Urgency: {urgency}")
        
        doctors = {
            "Dr. Smith (General Psychiatrist)": "+1-555-0123",
            "Dr. Johnson (Anxiety Specialist)": "+1-555-0124",
            "Dr. Williams (Depression Specialist)": "+1-555-0125"
        }
        
        call_type = st.radio("Select consultation method:", ["Phone Call", "Video Call"], key="doctor_call_type")
        selected_doctor = st.selectbox("Choose a specialist:", list(doctors.keys()), key="doctor_select")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect Now"):
                phone_number = doctors[selected_doctor]
                if call_type == "Phone Call":
                    webbrowser.open(f"tel:{phone_number}")
                else:
                    st.info(f"Initiating video call with {selected_doctor}")
                return f"Consultation arranged with {selected_doctor} via {call_type} for {reason} (Urgency: {urgency})"
        with col2:
            if st.button("Close"):
                st.session_state.show_doctor_ui = False
                return "Consultation cancelled"
    
    return "Doctor consultation interface closed"
def read_pdf(file_path):
    """
    Reads a PDF file and returns its number of pages and text from the first page.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing number of pages and first page text
            or error message if reading fails
    """
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            
            num_pages = len(reader.pages)
            first_page_text = reader.pages[0].extract_text()
            
            return {
                'num_pages': num_pages,
                'first_page_text': first_page_text.strip(),
                'error': None
            }
            
    except FileNotFoundError:
        return {'error': 'File not found'}
    except Exception as e:
        return {'error': f'Error reading PDF: {str(e)}'}
    
#Schedule Appointment Tool 

def schedule_appointment_tool(specialist_type: str, preferred_time: str) -> str:
    """
    Tool for scheduling future appointments with healthcare professionals.
    """
    st.subheader("📅 Schedule an Appointment")
    specialists = {
        "Psychiatrist": ["Dr. Smith", "Dr. Johnson"],
        "Therapist": ["Dr. Brown", "Dr. Davis"],
        "Nutritionist": ["Dr. Wilson", "Dr. Taylor"],
        "Wellness Coach": ["Coach Miller", "Coach Anderson"]
    }
    
    date = st.date_input("Select Date")
    time_slots = st.selectbox("Available Time Slots", 
                            ["9:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"])
    available_specialists = specialists.get(specialist_type, ["No specialists available"])
    selected_specialist = st.selectbox("Choose Specialist", available_specialists)
    
    if st.button("Confirm Appointment"):
        return f"Appointment scheduled with {selected_specialist} for {date} at {time_slots}"
    return "Please confirm your appointment"


def symptom_tracker_tool(symptoms: List[str] = None) -> str:
    """Tool for tracking symptoms"""
    if 'show_symptom_ui' not in st.session_state:
        st.session_state.show_symptom_ui = True
    
    if st.session_state.show_symptom_ui:
        st.subheader("📊 Symptom Tracker")
        
        if symptoms is None:
            symptoms = []
        
        symptom_input = st.text_input("Enter symptoms (comma-separated)", key="symptom_input")
        if symptom_input:
            symptoms.extend([s.strip() for s in symptom_input.split(',')])
        
        if symptoms:
            st.write("Tracking symptoms:", ", ".join(symptoms))
        
        symptom_intensity = st.slider("Symptom Intensity (1-10)", 1, 10, 5, key="symptom_intensity")
        duration = st.text_input("Duration (e.g., 2 days)", key="symptom_duration")
        additional_notes = st.text_area("Additional Notes", key="symptom_notes")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Log Symptoms"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                symptom_log = {
                    'timestamp': timestamp,
                    'symptoms': symptoms,
                    'intensity': symptom_intensity,
                    'duration': duration,
                    'notes': additional_notes
                }
                
                if 'symptom_logs' not in st.session_state:
                    st.session_state.symptom_logs = []
                st.session_state.symptom_logs.append(symptom_log)
                st.session_state.show_symptom_ui = False
                return f"Symptoms logged at {timestamp}: {', '.join(symptoms)} (Intensity: {symptom_intensity}, Duration: {duration})"
        with col2:
            if st.button("Cancel Logging"):
                st.session_state.show_symptom_ui = False
                return "Symptom logging cancelled"
    
    return "Symptom tracker interface closed"    
    

# Truncate function
def truncate_response(text, max_words=1000):
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
    
    # Detect language
    try:
        user_lang = detect(last_user_msg)
    except:
        user_lang = "en"  # Default to English
    
    context = (
            f"Generate the response in the language ,User language: {user_lang} , My name is {user_info['name']} and age {user_info['age']} "
            f"and ethnicity is {user_info.get('ethnicity', 'not provided')} while replying.Include Name in every respnse ,Do not include age and ethinicity in every response "
            f"Keel in mind last response summary {st.session_state.conversation_summary}.Use these instructions {instructions_new} "
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
        debug=False,
        tools=[doctor_consultation_tool,schedule_appointment_tool,symptom_tracker_tool] 
    )

# Initialize session state
if "workflow" not in st.session_state:
    st.session_state.workflow = WellnessWorkflow()
    st.session_state.conversation_summary = ""
    st.session_state.user_info_collected = False
    st.session_state.messages = []
    st.session_state.uploaded_files = []
    st.session_state.health_data = []
    st.session_state.symptom_logs = []

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
            
        if st.button("📞 Call Doctor"):
            call_doctor()
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
            file_content=read_pdf(file_path)
            # with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            #     file_content = f.read()
            
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
        
        try:
            user_lang = detect(prompt)
            print("Print User Language",user_lang)
        except:
            user_lang = "en"  # Default to English
        
        context = dedent(f"""
            User details:
            - Name: {user_info.get('name')}
            - Age: {user_info.get('age')}
            - Ethnicity: {user_info.get('ethnicity', 'Not provided')}
            - Give response in User language = {user_lang}
            - Always use name in generating the response 
            
            Recent health data:
            - Weight: {health_data.get('weight', 'Not logged')}kg
            - Mood: {health_data.get('mood', 'Not logged')}
            - Sleep: {health_data.get('sleep_hours', 'Not logged')} hours
            Last summary: {st.session_state.conversation_summary}
            - Symtoms: {st.session_state.symptom_logs}
            User query: {prompt}
        """).strip()
        response = st.session_state.workflow.physcatrist.run(context)
        response_text = truncate_response(extract_content_from_response(response))
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()