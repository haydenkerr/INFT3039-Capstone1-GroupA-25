import requests
import pandas as pd
import json

# load test data set
# host_port = "http://"+"3.106.58.24:8002"
# host_port = "https://"+"ielts-unisa-groupa.me"
# Docker
host_port = "http://"+"127.0.0.1:8002" #docker local
# host_port = "http://"+"127.0.0.1:8008" # fastapi local
# Define the GitHub raw CSV URL
# csv_url_test = "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/main/datasets/processed_dataset2_test_data.csv"

xlsx_url_test =  "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/UI2SP-565-Resolve-overall-score-increase-on-same-submission/ela_rag_docker/test_scripts/Teacher%20Validation%20Report%203.5.25.xlsx"

# Load the CSV data
df_test = pd.read_excel(xlsx_url_test, sheet_name='in')

print(df_test)
df_test = df_test[['task_name', 'question_text', 'task_name', 'essay_response']]  

# df_test.rename(columns={'prompt':'question'}, inplace=True)

# Example test case
question_id = 148
# word wrap the text output below  

API_KEY = "1234abcd"
essayGrade = {
    "email": "hayden.kerr@gmail.com",
    "question": """Reporting of crimes and other kinds of violent news on television and in newspapers can have adverse consquences. This kind of information should be restricted from being shown in the media. 
To what extent do you agree or disagree with this statement?
Give reasons for your answer and include any relevant examples from your own knowledge or experience.""",
    "essay": """
In today's media-saturated world, crime and violence dominate headlines across television and print platforms. While it is argued that such content can cause harmful effects on public perception and mental health, I believe that completely restricting this information would be an overreach. Instead, the media should adopt a more responsible approach to reporting without fully censoring such news.

On one hand, the continuous exposure to violent content can lead to desensitization, anxiety, and fear among the public. For instance, frequent reporting of crimes such as murder or terrorism may cause individuals to feel unsafe in their own communities, even when the actual risk is minimal. Moreover, young viewers who are repeatedly exposed to aggressive behaviour may develop a distorted understanding of acceptable social conduct. Studies in child psychology have shown correlations between exposure to violent media and increased aggression in youth.

However, despite these concerns, restricting crime reporting altogether could suppress vital public awareness. News about criminal activities often serves a critical role in alerting citizens to potential dangers and holding authorities accountable. For example, media coverage of corruption or police misconduct has, in numerous cases, led to public pressure and subsequent institutional reform. Furthermore, in democratic societies, the freedom of the press is a fundamental right. Imposing broad restrictions on content could set a dangerous precedent for censorship and the erosion of transparency.

Rather than enforcing outright bans, the emphasis should be placed on how crime and violence are portrayed. Media outlets should avoid sensationalism and instead focus on facts, context, and potential solutions. Educational framing—such as including expert commentary or highlighting community resilience—can mitigate negative psychological effects while still informing the public.

In conclusion, although violent news can indeed have adverse effects, I disagree with the idea of fully restricting such content in the media. A balanced and ethical approach to reporting, rather than censorship, is a more effective and democratic solution.""",
    "wordCount": 265,
    "submissionGroup":6,
    "taskType":"Academic Task 2"    
    
    }

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

# query = {"query_text": "What is the main idea of the text?"}
# response = requests.post(
#     host_port+"/query",
#     headers={"x-api-key": API_KEY},
#     json=query,
#     verify=False
# )


# print(response.json())


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
tracking_id = "7fda868d-8cb5-40e9-b02a-25d6fab89d33"
responseGet = requests.get(
    host_port+"/results/"+tracking_id,
    headers={"x-api-key": API_KEY}
    
)
print(responseGet.text)


# test results return from submissions
email = "hayden.kerr@gmail.com"
 
responseGet = requests.get(
    host_port+"/submissions/"+email,
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