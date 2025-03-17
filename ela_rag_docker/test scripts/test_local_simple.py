import requests
import pandas as pd

# load test data set

# Define the GitHub raw CSV URL
csv_url_test = "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/main/datasets/processed_dataset2_test_data.csv"

# Load the CSV data
df_test = pd.read_csv(csv_url_test)

df_test = df_test[['prompt', 'essay', 'band', 'cleaned_evaluation','Task Achievement', 'Coherence', 'Lexical Resource', 'Grammar','Overall Band Score']]  

df_test.rename(columns={'prompt':'question'}, inplace=True)

# Example test case
question_id = 13
# word wrap the text output below  



API_KEY = "1234abcd"
essayGrade = {
    "question": df_test.iloc[question_id]["question"],
    "essay": df_test.iloc[question_id]["essay"]
    }

response = requests.post(
    "http://192.168.1.15:8001/grade",
    headers={"x-api-key": API_KEY},
    json=essayGrade,
)
print(response.json())

query = {""}
response = requests.post(
    "http://192.168.1.15:8001/query",
    headers={"x-api-key": API_KEY},
    json=query,
)


print(response.json())


responseGet = requests.get(
    "http://192.168.1.15:8001/debug/documents",
    headers={"x-api-key": API_KEY}
    
)

print(responseGet.json())



responseGet = requests.get(
    "http://192.168.1.15:8001/debug/test",
    headers={"x-api-key": API_KEY}
    
)

print(responseGet.json())