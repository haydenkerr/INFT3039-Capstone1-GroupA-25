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

response = chat_session.send_message("tell me about melbourne australia")

print(response.text)