import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests

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

def load_system_prompt(task_id):
    """Load the system prompt from GitHub"""
    
    prompt_urls = {
        # 2: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25/refs/heads/staging/ela_rag_docker/task2_academic_system_prompt.md",
        3: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25/refs/heads/staging/ela_rag_docker/task1_general_system_prompt.md",
        4: "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25/refs/heads/staging/ela_rag_docker/task2_general_system_prompt.md"
    }

    url = prompt_urls.get(task_id, "https://raw.githubusercontent.com/haydenkerr/INFT3039-Capstone1-GroupA-25/refs/heads/staging/ela_rag_docker/default_system_prompt.md")
    
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

        response = chat_session.send_message(full_prompt)

        if response:
            print("✅ Gemini API Response Received")
            
            
            # Capture streamed response
            full_response = []
            for chunk in response:
                if hasattr(chunk, "text"):
                    full_response.append(chunk.text)

            response_text = " ".join(full_response).strip()

            if response_text:
                # print(response_text)
                return response_text
            else:
                print("⚠️ No valid text in response")
                return "⚠️ No valid response from Gemini."
        else:
            print("⚠️ Gemini API returned None")
            return "⚠️ Gemini API Error: No response received."

    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")
        return f"⚠️ Gemini API Error: {str(e)}"