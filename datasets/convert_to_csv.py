import pandas as pd
df = pd.read_parquet(r'C:\Users\hayde\OneDrive - Logical Aspect\Education\UniSA\INFT3039 - Capstone 1\datasets\ielts-evaluations-simple-ds.parquet')
df.to_csv(r'C:\Users\hayde\OneDrive - Logical Aspect\Education\UniSA\INFT3039 - Capstone 1\datasets\ielts-evaluations-simple-ds.csv')