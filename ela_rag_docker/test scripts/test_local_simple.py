import requests



API_KEY = "1234abcd"
essayGrade = {
    "question": """Interviews form the basic selection criteria for most large companies. However some people think that interview is not a reliable method of choosing whom to employ.
To what extent do you agree or disagree??""",
    "essay": """ Job Interviews are commonly undertaken by companies of all sizes seeking candidates to fill a role. They often consist of dialogues between a Human Resources representative of these companies and the professional interested in the position. During the conversation, the applicant's profile in terms of qualifications, skills and work experience is assessed against the job description and the company's expectations. However, some people argue this approach is insufficient for capturing the right employee. In my opinion, to ensure a more accurate hiring process, other methodologies should be explored along with interviews, such as group activities and personality quizzes.

The importance of job interviews when it comes to hiring new individuals to integrate a team cannot be dinned. It has proved to be the most traditional and practical method largely adopted by companies worldwide. They can offer vital insights about an applicant and lead to more informed decisions. However, people often act like robots by answering the questions in a way they know it may be expected by the hiring person. In this sense, other approaches should be introduced to a more holistic understading of the candidate capabilities. 

Many companies are already introducing new methods to find the best matches for their positions. These contemporary approaches evaluate profissionals during dynamic activites designed to capture the candidate's behaviour in complex situations, where pressure and conflicts are common.  In this case, applicants tend to express their realselves, values and logic thinking. The findings are often combined to the interview results as profile matching exercise. 

Another way to further assess the job seekers profiles is by assigning them some personality quizzes. Quizzes are powerful tools that can be used for gathering more information about of a  professional strenghts and weakness. They also can help the company to allocate the professional into the right team and role. Some professionals can naturally act like mediators, while other need to be led by others, for instance.

In conclusion, interviews will always have its importance as they are still insightful, simple, straigthforward and demand minimum resources to be undertaken. However, when combined with other approaches the hiring process become more precise. In this case, companies need to invest time and money to introduce these complemantary approaches. Finally, this may make sense for some companies and positions, but not for the majority."""
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