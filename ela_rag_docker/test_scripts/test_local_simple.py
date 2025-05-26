import requests
import pandas as pd
import json

# load test data set
# host_port = "http://"+"3.106.58.24:8002"
host_port = "https://"+"ielts-unisa-groupa.me"
# Docker
# host_port = "http://"+"192.168.1.17:8001"
# host_port = "http://"+"127.0.0.1:8008" # local fastapi
# host_port = "http://"+"127.0.0.1:8002" # local docker 

# Define the GitHub raw CSV URL
csv_url_test = "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/main/datasets/processed_dataset2_test_data.csv"

# Load the CSV data
df_test = pd.read_csv(csv_url_test)

df_test = df_test[['prompt', 'essay', 'band', 'cleaned_evaluation','Task Achievement', 'Coherence', 'Lexical Resource', 'Grammar','Overall Band Score']]  

df_test.rename(columns={'prompt':'question'}, inplace=True)

# Example test case
question_id = 172
# word wrap the text output below  

API_KEY = "1234abcd"
# essayGrade = {
#     "email": "hayden@google.com",
#     "question": """You are experiencing financial problems and want to ask your landlord if you can pay your rent late. Write a letter to your landlord. In your letter explain:  
# - Why you are writing to him.
# - Why you cannot pay the rent.
# - When you will pay the rent.""",
#     "essay": """Dear Mr. Bloke, 
# I hope this message finds you well. I am writing to inform you that I am facing some financial difficulties this month due to an unexpected family emergency. As a result, I will not be able to pay my rent on time. I will ensure the full rent is paid by the 20th of this month. I appreciate your understanding and patience.
# Yours sincerely,
# Jane Doe""",
#     "wordCount": 265,
#     "submissionGroup":6,
#     "taskType":"General Task 1"    
    
#     }

essayGrade = {
    "email": "hayden.kerr@gmail.com",
    "question": df_test.iloc[question_id]["question"],
    "essay": df_test.iloc[question_id]["essay"],
    "wordCount": 265,
    "submissionGroup":6,
    "taskType":"General Task 1"    
    }
response = requests.post(
    host_port+"/grade",
    headers={"x-api-key": API_KEY},
    json=essayGrade
    
)
print(response.json())

# test the query endpoint Remove from the main.py, need to
query = {"query_text": "What is the main idea of the text?"}
response = requests.post(
    host_port+"/query",
    headers={"x-api-key": API_KEY},
    json=query
 
)


print(response.json())


responseGet = requests.get(
    host_port+"/debug/documents",
    headers={"x-api-key": API_KEY}
    
)

print(responseGet.json())



responseGet = requests.get(
    host_port+"/debug/test",
    headers={"x-api-key": API_KEY}
    )

print(responseGet.json())



# test results return from database
tracking_id = "3ba6c355-8a95-4045-aeb4-3c2476644e01"
responseGet = requests.get(
    host_port+"/results/"+tracking_id,
    headers={"x-api-key": API_KEY}
    
)
print(responseGet.text)

# test all results return from 
email_address = "hayden.kerr@gmail.com"
responseGet = requests.get(
    host_port+"/submissions/"+email_address,
    headers={"x-api-key": API_KEY}
    
)
print(responseGet.text)



response = requests.get(
    "https://ielts-unisa-groupa.me/debug/test",
    headers={"x-api-key": "1234abcd"},
    timeout=10
)

print("STATUS:", response.status_code)
print("LOCATION:", response.headers.get("Location"))
print("SERVER:", response.headers.get("Server"))
print("CF-RAY:", response.headers.get("CF-RAY"))