import os
import google.generativeai as genai

#  enter this in windows powershell to set the environment variable
# Winodws + x a -> Windows Powershell (Admin)

# [System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'google_api_key_from_au-studio', [System.EnvironmentVariableTarget]::Machine)
# use https://thecategorizer.com/windows/how-to-refresh-environment-variables-in-windows/ to refresh the environment variables

#  refreshenv

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

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



chat_session = model.start_chat(
  history=[
  ]
)
# Function to handle streamed responses
def handle_streamed_response(response):
    for chunk in response:
        print(chunk.text, end='', flush=True)

# Example function to load context from a relevant source
def load_context():
    # Here you can load context from a file, database, API, etc.
    # For demonstration, we'll use a simple string as context
    context = open(r"C:\Users\hayde\OneDrive - Logical Aspect\Education\UniSA\INFT3039 - Capstone 1\pattern\improve_ielts_essay\system.md", "r").read()
    
    return context

# Load context
context = load_context()

essay = """
Between 1995 and 2010, a study was conducted representing the percentages of people born in Australia, versus people born outside Australia, living in urban, rural, and town. First, in 1995, cities represented the major percentage of habitat by roughly 50 percent, followed by rural areas and towns came in last, among people born in Australia. On the other hand, people born outside Australia, cities showed the most percentages of 6o percent, followed by rural areas and towns. In 2010, among people born in Australia, cities had an increase more than 20 percent increase in the total representation and a major decrease in towns and rural areas. Conversely, people born outside Australia, cities had the most percentage among both studies, followed by rural areas and towns."""

# Construct the prompt with context
prompt = f"{context}\n\n{essay}\n\n"

# Send a message and handle the streamed response
response = chat_session.send_message(prompt)
handle_streamed_response(response)