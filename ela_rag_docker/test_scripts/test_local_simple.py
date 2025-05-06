import requests
import pandas as pd

# load test data set
host_port = "http://"+"3.27.223.201:8002"
# Docker
# host_port = "http://"+"192.168.1.17:8001"
# host_port = "http://"+"127.0.0.1:8001"
# Define the GitHub raw CSV URL
csv_url_test = "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/main/datasets/processed_dataset2_test_data.csv"

# Load the CSV data
df_test = pd.read_csv(csv_url_test)

df_test = df_test[['prompt', 'essay', 'band', 'cleaned_evaluation','Task Achievement', 'Coherence', 'Lexical Resource', 'Grammar','Overall Band Score']]  

df_test.rename(columns={'prompt':'question'}, inplace=True)

# Example test case
question_id = 152
# word wrap the text output below  



API_KEY = "1234abcd"
essayGrade = {
    "email": "hayden@google.com",
    "question": df_test.iloc[question_id]["question"],
    "essay": df_test.iloc[question_id]["essay"],
    "wordCount": 265,
    "submissionGroup":6,
    "taskType":"General Task 1"    
    }

response = requests.post(
    host_port+"/grade",
    headers={"x-api-key": API_KEY},
    json=essayGrade,
)
print(response.json())

query = {"query_text": "What is the main idea of the text?"}
response = requests.post(
    host_port+"/query",
    headers={"x-api-key": API_KEY},
    json=query,
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
tracking_id = "3e19f672-76aa-4fc5-ace6-f25a836713cd"
responseGet = requests.get(
    host_port+"/results/"+tracking_id,
    headers={"x-api-key": API_KEY}
    
)
print(responseGet.text)