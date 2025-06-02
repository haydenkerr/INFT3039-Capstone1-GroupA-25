import requests
import pandas as pd
import json
import os
import dotenv

# load test data set
# host_port = "http://"+"3.106.58.24:8002"
# host_port = "https://"+"ielts-unisa-groupa.me"
# Docker
# host_port = "http://"+"127.0.0.1:8002" #docker local
host_port = "http://"+"127.0.0.1:8008" # fastapi local

os.chdir('ela_rag_docker')
dotenv.load_dotenv()
API_KEY = dotenv.get_key(dotenv.find_dotenv(), "API_KEY")




# Define the GitHub raw CSV URL
# csv_url_test = "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/main/datasets/processed_dataset2_test_data.csv"

xlsx_url_test =  "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/staging/ela_rag_docker/test_scripts/question_list_with_all_essays.xlsx"

# Load the CSV data
xlsx_url_test = pd.read_excel(xlsx_url_test, sheet_name='Sheet1')


xlsx_url_test = xlsx_url_test[['task_id', 'question_text', 'complete_essay']]  

# add a column to the dataframe with the task type description. 
# 1 =     "General Task 1": with a minimum of 150 words
# 2 =     "General Task 2": with a minimum of 250 words
# 3 =     "Academic Task 1": with a minimum of 150 words 
# 4 =     "Academic Task 2": with a minimum of 250 words
xlsx_url_test['taskType'] = xlsx_url_test['task_id'].map({
    1: "General Task 1",
    2: "General Task 2",
    3: "Academic Task 1",
    4: "Academic Task 2"
})

xlsx_url_test




# Example test case
import random
# Randomly select a question ID from the test set
# For testing purposes, we can set a specific question_id

# question_id = 148
# word wrap the text output below  


essayGrade = {
    "email": "hayden.kerr@gmail.com",
    "question": """"Some people think that it is better for children to grow up in the countryside, while others believe that living in a city is more beneficial for their development.

Discuss both views and give your own opinion."
""",
    "essay": """
"The environment in which children grow up can have a significant impact on their development. While some believe that a rural upbringing offers a healthier and more peaceful lifestyle, others argue that growing up in a city provides more opportunities for learning and personal growth. Both perspectives have merit, but I believe that urban environments offer more advantages overall.

Supporters of countryside living often point to the cleaner air, closer connection to nature, and slower pace of life. Children in rural areas may enjoy more outdoor activities, experience less stress, and have stronger community ties. These factors can contribute to physical well-being and emotional security during early development.

However, growing up in a city exposes children to a wide range of educational and cultural opportunities. Urban areas typically offer better schools, libraries, and extracurricular programs. Children also benefit from access to museums, theatres, and diverse communities, which can broaden their understanding of the world. While city life can be fast-paced and sometimes overwhelming, it also prepares young people for modern life in a globalized society.

In my opinion, although the countryside provides a peaceful environment, the resources and exposure available in cities play a more critical role in a child’s intellectual and social development. With proper guidance and support, the challenges of urban living can be managed effectively.

In conclusion, both the countryside and the city have unique benefits, but I believe the city better equips children for the future by offering more varied and stimulating experiences."
""",
    "wordCount": 247,
    "submissionGroup":3,
    "taskType":"General Task 2"    
    
    }

# loop through the test data set and post each essay to the API
for index, row in xlsx_url_test.iterrows():
    essayGrade = {
        "email": "hayden.kerr@gmail.com",
        "question": row["question_text"],
        "essay": row["complete_essay"],
        "wordCount": len(row["complete_essay"].split()),
        "submissionGroup": 6,
        "taskType": row["taskType"]
    }
    response = requests.post(
        host_port+"/grade",
        headers={"x-api-key": API_KEY},
        json=essayGrade
    )
    print(response.json())


question_id = random.randint(0, len(xlsx_url_test) - 1)
essayGrade = {
    "email": "hayden.kerr@gmail.com",
    "question": xlsx_url_test.iloc[question_id]["question_text"],
    "essay": xlsx_url_test.iloc[question_id]["complete_essay"],
    "wordCount": len(row["complete_essay"].split()),
    "submissionGroup":6,
    "taskType": row["taskType"]    
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
    headers={"x-api-key": API_KEY},
    timeout=10
)

print("STATUS:", response.status_code)
print("LOCATION:", response.headers.get("Location"))
print("SERVER:", response.headers.get("Server"))
print("CF-RAY:", response.headers.get("CF-RAY"))