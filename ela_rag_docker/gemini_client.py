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
  "response_mime_type": "application/json",
}


model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
)



chat_session = model.start_chat(history=[])

def load_system_prompt(task_id):
    """Load the system prompt from GitHub"""
    
    prompt_urls = {
        # 2: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25/refs/heads/staging/ela_rag_docker/task2_academic_system_prompt.md",
        3: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25/refs/heads/staging/ela_rag_docker/task1generalprompt_v6.md",
        4: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25/refs/heads/staging/ela_rag_docker/task2generalprompt_v7.md"
    }

    url = prompt_urls.get(task_id, "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25/refs/heads/staging/ela_rag_docker/system.md")
    
    try:
        sys_prompt = requests.get(url).text
        refinement = requests.get("https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25/refs/heads/staging/ela_rag_docker/prompt_refinement.md").text
        return sys_prompt + "\n\n" + refinement
    except Exception as e:
        print(f"Error loading system prompt: {str(e)}")
        return "You are an IELTS essay evaluator. Evaluate essays based on the IELTS criteria."

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
            # Safely extract the JSON payload
            if hasattr(response, 'candidates') and response.candidates:
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