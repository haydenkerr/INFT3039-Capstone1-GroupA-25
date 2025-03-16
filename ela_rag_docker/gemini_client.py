import google.generativeai as genai
import os
from dotenv import load_dotenv

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
# Function to handle streamed responses
def handle_streamed_response(response):
    for chunk in response:
        print(chunk.text, end='', flush=True)

def load_context():
    # Here you can load context from a file, database, API, etc.
    # For demonstration, we'll use a simple string as context
    context = open(r"C:\Users\hayde\OneDrive - Logical Aspect\Education\UniSA\INFT3039 - Capstone 1\pattern\improve_ielts_essay\system.md", "r").read()
    
    return context

chat_session = model.start_chat(
  history=[
  ]
)

# Load context
context = load_context()
question = """
The diagram below shows how rain water is collected and then treated to be used as drinking water in an Australian town. Summarise the information by selecting and reporting the main features and make comparisons where relevant.You should write at least 150 words.
"""
essay = """
Whether people should be encouraged more to study vocational courses due to the lack of workforce in that area or be encouraged to study at the university remains a big discussion. I believe both of these areas of study should be promoted equally, countries need academics as well as qualified workers.
One of the reasons that supports the encouragement to study either area, academic or vocational, is the worldwide need for the two types of professionals. For example, Australian government is currently offering work visas and permanent residencies to overseas qualified workers such as, carpenters, cooks, bar managers as well as doctors, nurses and psychologists. Essentially, this demonstrates that the two areas are equally needed and this happens in Canada and England too.
Another point to be considered is the increase in the people's needs due to the population growth, which, therefore, affects the need for more experts in all sectors. This includes professional from different fields, such as science, construction and even thinkers. If people is encouraged to study more in one field than others, this might be detrimental to societies, leaving one sector significantly more affected. Eventually, countries need a balance in the areas choosen for people to growth a career.
In conclusion, I support the idea of encouraging both, university and vocational studies. Many countries worldwide have expressed their need for the two types of workers. Besides, as the population is rapidly increasing, the need for experts in multiples areas is increasing too, so promoting both is the only way to maintain a balance."""

# Construct the prompt with context
prompt = f"{context}\n\n{question}\n\n{essay}\n\n"



def query_gemini(prompt: str) -> str:
    
# Send a message and handle the streamed response
    response = chat_session.send_message(prompt)
       
    return handle_streamed_response(response) if response else "No response from Gemini."
