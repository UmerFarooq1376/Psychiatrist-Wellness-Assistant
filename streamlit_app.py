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
import json

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
        5. At the end make a bullet points of possible reasons 



        """
        # f"‼️ CRITICAL INSTRUCTION - DOCTOR CONSULTATION FORMAT ‼️\n"
        # f"STRICTLY FORMAT YOUR RESPONSE AS [CALL_DOCTOR] ONLY IN THESE TWO SPECIFIC SCENARIOS:\n"
        # f"1. WHEN USER EXPLICITLY REQUESTS TO SPEAK WITH A DOCTOR\n"
        # f"2. WHEN YOU DETECT ANY OF THESE SEVERE CONDITIONS:\n"
        # f"   - SEVERE DEPRESSION OR ANXIETY SYMPTOMS\n"
        # f"   - SUICIDAL THOUGHTS OR SELF-HARM INDICATORS\n"
        # f"   - COMPLEX MENTAL HEALTH ISSUES REQUIRING PROFESSIONAL INTERVENTION\n"
        # f"   - CASES NEEDING MEDICATION OR CLINICAL ASSESSMENT\n"
        # f"   - SITUATIONS BEYOND AI ASSISTANCE CAPABILITIES\n\n"
        # f"⚠️ DO NOT USE THIS FORMAT FOR ANY OTHER SCENARIOS ⚠️\n"
        # f"When required, format EXACTLY as:\n"
        # f"[CALL_DOCTOR]{{\"action\":\"call_doctor\",\"reason\":\"detailed_critical_reason\",\"urgency\":\"normal/urgent/emergency\",\"consultation_type\":\"phone\"}} followed by your supportive message.\n"
        # f"FOR ALL OTHER CASES, PROVIDE NORMAL SUPPORTIVE RESPONSES WITHOUT THE [CALL_DOCTOR] FORMAT."
        ]
        # Additional Guidelines:
    #     - If you detect severe symptoms or situations requiring professional medical attention,
    #       use the doctor_consultation_tool to connect the user with a specialist.
    #     - Recommend doctor consultation for:
    #       * Severe depression or anxiety symptoms
    #       * Suicidal thoughts
    #       * Complex mental health issues
    #       * Cases requiring medication
    #       * Situations beyond AI assistance scope
    #      - If there is need and user asked request for a calling the doctor ,*** Only then call the doctor NOT EVERYTIME giving ** format your response as: [CALL_DOCTOR]{{\"action\":\"call_doctor\",\"reason\":\"...\",\"urgency\":\"normal\",\"consultation_type\":\"phone\"}} followed by your message.
        
    #     When recommending a doctor:
    #     1. Explain why professional help is needed
    #     2. Call the doctor_consultation_tool with appropriate reason and urgency
    #     3. Continue providing support while arranging the consultation
        
    #     """
    # ]



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

def doctor_consultation_tool(reason: str, urgency: str = "normal") -> Dict:
    """
    Tool for initiating doctor consultation when the AI determines it's necessary.
    
    Args:
        reason: The medical reason for consultation
        urgency: Urgency level ("normal", "urgent", "emergency")
    """
    print("<============ Calling Doctor ===========>")
    st.subheader("🏥 Doctor Consultation Recommended")
    st.write(f"Reason: {reason}")
    st.write(f"Urgency: {urgency}")
    
    doctors = {
        "Dr. Smith (General Psychiatrist)": "+1-555-0123",
        "Dr. Johnson (Anxiety Specialist)": "+1-555-0124",
        "Dr. Williams (Depression Specialist)": "+1-555-0125"
    }
    
    call_type = st.radio("Select consultation method:", ["Phone Call", "Video Call"])
    selected_doctor = st.selectbox("Choose a specialist:", list(doctors.keys()))
    
    if st.button("Connect Now"):
        phone_number = doctors[selected_doctor]
        if call_type == "Phone Call":
            webbrowser.open(f"tel:{phone_number}")
        else:
            st.info(f"Initiating video call with {selected_doctor}")
        
        return {
            "status": "success",
            "doctor": selected_doctor,
            "consultation_type": call_type,
            "reason": reason
        }
    
    return {"status": "pending"}


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

def generate_bot_response(context_new=""):
    """Generate bot response for the latest user message."""
    # last_user_msg = st.session_state.messages[-1]["content"]
    last_user_msg = st.session_state.messages[-1]["content"].lower()
    user_info = st.session_state.workflow.user_info
    
    # Detect language
    try:
        user_lang = detect(last_user_msg)
    except:
        user_lang = "en"  # Default to English

    # Direct user request check
    doctor_keywords = ["call doctor", "need doctor", "see doctor"]
    if any(keyword in last_user_msg for keyword in doctor_keywords):
        consultation_result = doctor_consultation_tool(
            reason=f"Immediate user request for consultation",
            urgency="normal"
        )
        return

    # context = (
    #         f"{context_new}"
    #         f"Generate the response in the language ,User language: {user_lang} , My name is {user_info['name']} and age {user_info['age']} "
    #         f"and ethnicity is {user_info.get('ethnicity', 'not provided')} while replying.Include Name in every respnse ,Do not include age and ethinicity in every response "
    #         f"Keel in mind last response summary {st.session_state.conversation_summary}."
    #         # Use these instructions {instructions_new} "
    #         #f"If you determine professional medical help is needed, start your response with '[DOCTOR_NEEDED]' followed by the reason and urgency level (normal/urgent/emergency)."
    #         # f"{prompt}"
    #         # f"If there is need and user asked request for a calling the doctor , format your response as: [CALL_DOCTOR]{{\"action\":\"call_doctor\",\"reason\":\"...\",\"urgency\":\"normal\",\"consultation_type\":\"phone\"}} followed by your message."
    #         f"‼️ CRITICAL INSTRUCTION - DOCTOR CONSULTATION FORMAT ‼️\n"
    #         f"STRICTLY FORMAT YOUR RESPONSE AS [CALL_DOCTOR] ONLY IN THESE TWO SPECIFIC SCENARIOS:\n"
    #         f"1. WHEN USER EXPLICITLY REQUESTS TO SPEAK WITH A DOCTOR\n"
    #         f"2. WHEN YOU DETECT ANY OF THESE SEVERE CONDITIONS:\n"
    #         f"   - SEVERE DEPRESSION OR ANXIETY SYMPTOMS\n"
    #         f"   - SUICIDAL THOUGHTS OR SELF-HARM INDICATORS\n"
    #         f"   - COMPLEX MENTAL HEALTH ISSUES REQUIRING PROFESSIONAL INTERVENTION\n"
    #         f"   - CASES NEEDING MEDICATION OR CLINICAL ASSESSMENT\n"
    #         f"   - SITUATIONS BEYOND AI ASSISTANCE CAPABILITIES\n\n"
    #         f"⚠️ DO NOT USE THIS FORMAT FOR ANY OTHER SCENARIOS ⚠️\n"
    #         f"When required, format EXACTLY as:\n"
    #         f"[CALL_DOCTOR]{{\"action\":\"call_doctor\",\"reason\":\"detailed_critical_reason\",\"urgency\":\"normal/urgent/emergency\",\"consultation_type\":\"phone\"}} followed by your supportive message.\n"
    #         f"FOR ALL OTHER CASES, PROVIDE NORMAL SUPPORTIVE RESPONSES WITHOUT THE [CALL_DOCTOR] FORMAT."    
    # )

    context = (
        f"{context_new}"
        f"Instructions:\n"
        f"1. Generate response in {user_lang} language\n"
        f"2. Address user as {user_info['name']}\n"
        f"3. Previous conversation summary: {st.session_state.conversation_summary}\n\n"
        
        f"DOCTOR CONSULTATION RULES:\n"
        f"Format as [CALL_DOCTOR] ONLY if:\n"
        f"1. User directly asks for a doctor\n"
        f"2. You detect:\n"
        f"   • Severe depression/anxiety\n"
        f"   • Suicidal thoughts\n"
        f"   • Complex mental health issues\n"
        f"   • Need for medication\n"
        f"   • Issues beyond AI scope\n\n"
        
        f"Response format when doctor needed:\n"
        f'[CALL_DOCTOR]{{"action":"call_doctor","reason":"REASON","urgency":"URGENCY","consultation_type":"phone"}}\n'
        f"Your supportive message here.\n\n"
        
        f"For all other cases: Provide normal supportive response."
        )
    # print("Context",context)
    response = st.session_state.workflow.physcatrist.run(context)
    response_text = extract_content_from_response(response)
    # Check if doctor consultation is recommended
    # if response_text.startswith('[CALL_DOCTOR]') or response_text.startswith('[call_doctor]')  :
    if '[CALL_DOCTOR]' in response_text:
        print("===== Chat Approach =====")
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.find('}') + 1
            json_str = response_text[start_idx:end_idx]
            print("Print Json_str",json_str,type(json_str))
             # Clean malformed JSON
            json_str = json_str.replace('""', '"')  # Fix double quotes
            json_str = json_str.replace('}.', '}')  # Remove trailing period
            json_str = json_str.replace('}"', '}')  # Remove trailing quote

            print("Cleaned JSON:", json_str)

            data = json.loads(json_str)
            print("======Data======",data)
            print(f"Reasoning {data.get('reason')},Urgency {data.get('urgency')}")
            consultation_result = doctor_consultation_tool(
                reason=data.get('reason'),
                urgency=data.get('urgency', 'normal')
            )
            
            # Clean response for display
            message = response_text[end_idx:].strip()
            st.session_state.messages.append({
                "role": "assistant",
                "content": message
            })
        except:
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text
            })
        # Parse the recommendation
        # parts = response_text[14:].split('\n', 2)
        # reason = parts[0].strip()
        # urgency = parts[1].strip() if len(parts) > 1 else "normal"
        # message = parts[2].strip() if len(parts) > 2 else ""
        
        # # Call the doctor consultation tool
        # consultation_result = doctor_consultation_tool(reason, urgency)
        
        # # Append both the AI's message and consultation interface
        # st.session_state.messages.append({
        #     "role": "assistant",
        #     "content": message
        # })
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text
        })
    # st.session_state.messages.append({
    #     "role": "assistant",
    #     "content": response_text
    # })

class WellnessWorkflow(Workflow):
    user_info: dict = {}
    health_data:dict={}
    physcatrist: Agent = Agent(
        model=base_model,
        instructions=Phsy_instructions,
        storage=SqlAgentStorage(db_file="wellness_agent.db", table_name="phsycatrist"),
        markdown=True,
        debug=False
        # tools=[doctor_consultation_tool]
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
            generate_bot_response("Geneate possible reason that lead to stress, Then Ask User Question , when you are confident enough then give Stress management technique")
            st.rerun()
        
        if st.button("Sleep Improvement"):
            st.session_state.messages.append({
                "role": "user",
                "content": "How to sleep better"
            })
            generate_bot_response(context_new="How to sleep better")
            st.rerun()
            
        if st.button("Diet Suggestions"):
            st.session_state.messages.append({
                "role": "user",
                "content": "Ask Questions about all things that can be used in calculating bmi etc , Then give proper diet plan to the user , take into account every aspect"
            })
            generate_bot_response(context_new="sk Questions about all things that can be used in calculating bmi etc , Then give proper diet plan to the user , take into account every aspect")
            st.rerun()
            # Add new Call Doctor button
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
            generate_bot_response(context_new="")
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
        
        context_new = dedent(f"""
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
            User query: {prompt}
            
        """
        # f"If doctor consultation is needed, format your response as: [CALL_DOCTOR]{{\"action\":\"call_doctor\",\"reason\":\"...\",\"urgency\":\"normal\",\"consultation_type\":\"phone\"}} followed by your message.").strip()
        )
        generate_bot_response(context_new)
        st.rerun()
        # response = st.session_state.workflow.physcatrist.run(context)
        # response_text = truncate_response(extract_content_from_response(response))
        
        # st.session_state.messages.append({"role": "assistant", "content": response_text})
        # st.rerun()