import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()  # Load API Key from `.env` file

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}


model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
)


chat_session = model.start_chat(history=[])

def load_system_prompt(task_id, local_override=True):
    """Load the system prompt from local file (if available) or GitHub as fallback"""

    local_paths = {
        1: "task1generalprompt_v6.md",
        2: "task2generalprompt_v7.md",
        3: "task2generalprompt_v7.md",
        4: "task2generalprompt_v7.md"
    }

    remote_urls = {
        1: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25-System-Prompts/refs/heads/main/task1generalprompt_v6.md",
        2: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25-System-Prompts/refs/heads/main/task2generalprompt_v7.md",
        3: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25-System-Prompts/refs/heads/main/task2generalprompt_v7.md",
        4: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25-System-Prompts/refs/heads/main/task2generalprompt_v7.md"
    }

    refinement_local = "prompt_refinement.md"
    refinement_url = "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25-System-Prompts/refs/heads/main/prompt_refinement.md"

    # Try to load main system prompt
    try:
        if local_override and task_id in local_paths and os.path.exists(local_paths[task_id]):
            with open(local_paths[task_id], "r", encoding="utf-8") as f:
                sys_prompt = f.read()
            print(f"✅ Loaded system prompt locally from: {local_paths[task_id]}")
        else:
            url = remote_urls.get(task_id, remote_urls[4])
            sys_prompt = requests.get(url).text
            print(f"🌐 Loaded system prompt from GitHub: {url}")
    except Exception as e:
        print(f"❌ Failed to load system prompt: {e}")
        sys_prompt = "You are an IELTS essay evaluator. Evaluate essays based on the IELTS criteria."

    # Try to load refinement markdown
    try:
        if local_override and os.path.exists(refinement_local):
            with open(refinement_local, "r", encoding="utf-8") as f:
                refinement = f.read()
            print(f"✅ Loaded refinement locally from: {refinement_local}")
        else:
            refinement = requests.get(refinement_url).text
            print(f"🌐 Loaded refinement from GitHub: {refinement_url}")
    except Exception as e:
        print(f"⚠️ Could not load refinement: {e}")
        refinement = ""

    # Combine and return
    return sys_prompt + "\n\n" + refinement

# # Load system prompt once at module initialization
# SYSTEM_PROMPT = load_system_prompt(task_id)

def query_gemini(task_id: int, user_prompt: str, examples_context: str = "", question: str = "", essay: str = "") -> str:
    """
    Sends a prompt to Google Gemini and returns the response as a string.
    
    Args:
        user_prompt: The main prompt to send
        examples_context: Optional RAG examples for context
        question: Optional essay question if available
        essay: Optional essay text if available
    """
    try:
        # If question and essay are provided, use them in the prompt
        system_prompt = load_system_prompt(task_id)
        full_prompt = system_prompt

        if examples_context:
            full_prompt += f"\n\nHere are some example graded essays:\n{examples_context}"

        if question and essay:
            # full_prompt += f"\n\nNow, evaluate this new essay:\nNew question: {question}\nNew Essay: {essay}"
            full_prompt += f'\n\nNow, evaluate this new essay:\n"""{question}"""\n"""{essay}"""'

        # Add any additional user prompt
        if user_prompt:
            full_prompt += f"\n\n{user_prompt}"

        print("📡 Sending request to Gemini...")
        # print(f"📝 Prompt start: {full_prompt[:300]}...")  # Print only first 300 chars
        if generation_config["response_mime_type"] == "application/json":
            response = model.generate_content(full_prompt)
            print(f":Full prompt: {full_prompt}")
            print("✅ Gemini API JSON response received")
            print(f"📜 Gemini response: {response}")  # Print the entire response for debugging
            
            if hasattr(response,"text"):
                return response.text
            # Safely extract the JSON payload
            elif hasattr(response, 'candidates') and response.candidates:
                try:
                    json_output = response.candidates[0].content.parts[0].function_call.args
                    return json.dumps(json_output)  # Return a JSON string
                except Exception as e:
                    return f"⚠️ Failed to extract JSON from Gemini response: {str(e)}"
            else:
                return "⚠️ No candidates found in Gemini response."

        else:
            # Fallback for text/plain MIME
            response = chat_session.send_message(full_prompt)
            full_response = []
            for chunk in response:
                if hasattr(chunk, "text"):
                    full_response.append(chunk.text)
            return " ".join(full_response).strip()

    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")
        return f"⚠️ Gemini API Error: {str(e)}"