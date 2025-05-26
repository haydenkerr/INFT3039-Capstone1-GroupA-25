import requests
import pandas as pd
import json

# load test data set
# host_port = "http://"+"3.106.58.24:8002"
# host_port = "https://"+"ielts-unisa-groupa.me"
# Docker
host_port = "http://"+"127.0.0.1:8001" #docker local
# host_port = "http://"+"127.0.0.1:8008" # fastapi local
# Define the GitHub raw CSV URL
csv_url_test = "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/main/datasets/processed_dataset2_test_data.csv"

# Load the CSV data
df_test = pd.read_csv(csv_url_test)

df_test = df_test[['prompt', 'essay', 'band', 'cleaned_evaluation','Task Achievement', 'Coherence', 'Lexical Resource', 'Grammar','Overall Band Score']]  

df_test.rename(columns={'prompt':'question'}, inplace=True)

# Example test case
question_id = 148
# word wrap the text output below  

API_KEY = "1234abcd"
essayGrade = {
    "email": "hayden.kerr@gmail.com",
    "question": """Some people believe that children should spend more time on school subjects, while others think they should have more free time. Discuss both views and give your opinion.""",
    "essay": """Introduction: The allocation of time for children between school subjects and leisure time is a subject of constant debate. Some argue that children should devote more time to school subjects, emphasizing academic excellence. In contrast, others endorse a balanced approach that allows children more free time. This task will discuss both perspectives and give my own opinion. Body paragraph 1:
    On the one hand, proponents of an academic-focused approach argue that more time for school subjects is necessary for a child's intellectual development. They argue that a strong educational foundation is critical in a competitive world, where academic achievements open doors to future opportunities. furthermore, a structured academic schedule instills discipline and time management proficiency, preparing children for the demands of the majority.
Body Paragraph 2:
On the other hand, proponents of the balanced approach argue that children need free time for their overall well-being. They believe that too much emphasis on academics can lead to stress and collapse. Giving children more free time enables them to explore their interests, develop hobbies, and engage in recreational activities. This formless time encourages creativity, social relations, and individual growth.
In my opinion, balancing school subjects and free time is the most effective approach. While academic excellence is important, free time is equally important for a child's holistic development. A well-rounded education should include not only formal education but also opportunities for relaxation, exploration, and self-discovery. Achieving this balance ensures that children can do better academically while enjoying a fulfilling and healthy childhood. In the end, the key is in moderation and honoring that both aspects play an important role in a child's development and happiness.""",
    "wordCount": 265,
    "submissionGroup":6,
    "taskType":"Academic Task 1"    
    
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

query = {"query_text": "What is the main idea of the text?"}
response = requests.post(
    host_port+"/query",
    headers={"x-api-key": API_KEY},
    json=query,
    verify=False
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
tracking_id = "7fda868d-8cb5-40e9-b02a-25d6fab89d33"
responseGet = requests.get(
    host_port+"/results/"+tracking_id,
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