# Psychiatrist-Wellness-Assistant

## Overview

The **Psychiatrist Wellness Assistant** is a wellness application powered by AI developed with Streamlit, Phi Agent Framework, and Ollama models. It offers customized physical and mental health advice based on user input. The assistant has meaningful conversations with users, gathers pertinent health information, and provides actionable suggestions based on their requirements.

Key Features:
- **Customized Wellness Guidance**: Provides recommendations for physical wellness (e.g., exercise, diet) and mental wellness (e.g., mindfulness exercises, stress reduction).
- **Friendly Interface**: Designed using Streamlit for an interactive and easy-to-use interface.
- **Health Metric Recording**: Enables recording of health metrics such as weight, mood, and sleep duration.
- **Document Uploads**: Enables the uploading of files such as medical reports for analysis.
- **Accelerated Query Buttons**: Offers short cuts for routine queries such as stress relief techniques, sleep assistance, and diet advice.
- **Persistent Converse**: Offers session state storage to provide continuous conversations.


## Features

### 1. User Info Collection
- Collect the user’s **name**, **age**, and optional **ethnicity**.
- Tailor responses based on this personal data.

### 2. Chat Interface
- Users can type open-ended questions.
- Responses come from a local LLaMA-based model (`deepseek-r1:1.5b` by default) via [Ollama](https://github.com/jmorganca/ollama).
- The conversation history persists on-screen.

### 3. Quick Queries (Sidebar)
- Pre-set buttons for common health topics (e.g., **Stress Relief Tips**, **Sleep Improvement**).
- Clicking a button automatically inputs a user question, which the AI then answers.

### 4. Health Tracker
- Log **weight**, **mood**, and **sleep hours**.
- Automatically receive AI analysis after saving.
- A history table displays all past logs.

### 5. File Upload(Under development)
- Accept `.pdf` or `.txt` files.
- Stores them in an `uploads` directory.
- The assistant can incorporate uploaded file content into future responses if the user clicks **“Process Uploaded File.”**

### 6. Response Truncation
- Long answers are truncated to 400 words by default.
- Adjustable in the `truncate_response` function if needed.

---

## Prerequisites

### 1. Python 3.7+
- (Tested with Python 3.10 or 3.11. **Avoid Python 3.13** until dependencies are fully compatible.)

### 2. Ollama
- Needed to run local LLaMA-based models.
- **macOS** installation:
  - `brew install ollama/tap/ollama`
- **Windows or Linux**:  
  - See [Ollama docs](https://github.com/jmorganca/ollama) for Docker/WSL instructions.

### 3. Pull the Model
- Example with `deepseek-r1:1.5b`:
  - `ollama pull deepseek-r1:1.5b`
- Verify the model is listed:
  - `ollama list`

---

## Installation

### 1. Clone or Copy the Project
- Download/clone this repository or copy the `streamlit_app.py` file into a local folder.

### 2. Create a Virtual Environment (recommended)
- `python -m venv venv`
- Activate:
  - On macOS/Linux: `source venv/bin/activate`
  - On Windows: `venv\Scripts\activate`

### 3. Install Dependencies
- `pip install -r requirements.txt`

---

## Usage

### 1. Start Streamlit
- `streamlit run streamlit_app.py`
  - If your script file is named differently, replace `streamlit_app.py` accordingly.

### 2. Open in Browser
- By default, [http://localhost:8501](http://localhost:8501).

### 3. Enter User Info
- Fill out **Name**, **Age**, **Ethnicity** on the initial form.
- Click **“Start Wellness Journey.”**

### 4. Explore the Assistant
- The **sidebar** offers **Quick Queries** (Stress Relief Tips, Sleep Improvement, Diet Suggestions).
- **Health Tracker** to log weight, mood, and sleep hours, then see an immediate AI-based analysis.
- **Main Chat** for open-ended user questions.

### 5. File Upload
- Upload a `.pdf` or `.txt` file in the **File Upload** section.
- Click **“Process Uploaded File”** to integrate the file’s text into the conversation.

### 6. Stop the Server
- Press `Ctrl + C` in the terminal to halt Streamlit.

---

## Project Structure

### 1. `WellnessWorkflow` (Subclass of `phi.workflow.Workflow`)
- Holds user data (`user_info`, `health_data`).
- Contains the `physcatrist` agent for LLaMA-based reasoning.

### 2. `physcatrist: Agent`
- Configured with `Ollama(id="deepseek-r1:1.5b")`.
- Instructed as a mental/physical wellness guide.
- Uses `SqlAgentStorage` to optionally store conversation in `wellness_agent.db`.

### 3. Sidebar Elements
- **Quick Queries**: Instantly insert typical user prompts.
- **Health Tracker**: Save weight, mood, sleep data with a time stamp.

### 4. File Upload( Currently in work,)
- Saves uploaded files to the `uploads/` directory.
- Processes text content upon user action.

### 5. Chat Interface
- Maintains a list of messages in `st.session_state.messages`.
- Each entry has a `role` ("user" or "assistant") and `content`.

---

## Configuration

### Model
- Defined in code:
  - `base_model = Ollama(id="deepseek-r1:1.5b")`
- Change to any pulled model by updating the `id`.

### Database File
- `SqlAgentStorage(db_file="wellness_agent.db")`
- Edit if you want a different file name or disable persistent history.

### Response Truncation
- Handled by:
  - `truncate_response(text, max_words=400)`
- Change the `max_words` value for shorter or longer truncation.

---

## Limitations

1. **Local LLaMA Model**  
   - Performance depends on your hardware and the model size.
   - Large models may require a strong GPU or specialized environment.

2. **Not Real Medical Advice**  
   - For demonstration only.
   - Does not replace professional mental or physical health advice.

---

## License

No explicit license is provided.  
Please comply with licenses of any third-party libraries or model weights.

---

**Enjoy using your AI-powered wellness assistant!**  
For troubleshooting and advanced features, consult:
- [Streamlit docs](https://docs.streamlit.io/)
- [Phi Data docs](https://docs.phidata.xyz/)
- [Ollama docs](https://github.com/jmorganca/ollama)

