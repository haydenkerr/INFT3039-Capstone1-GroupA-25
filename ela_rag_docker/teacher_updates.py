"""
teacher_updates.py

This script processes a CSV file containing teacher feedback on the model generated results.
It is separate to the main process, and run manually to update the results in the database
based on teacher validations.

Typical use case:
- Human markers review model outputs and flag scores or feedback as valid/invalid in Excel
- The returned feedback is added to the validation_file.csv template, containing updated scores and/or feedback
- This script reads the CSV and updates the database accordingly

Dependencies:
- database.py for database connection and operations

"""

import pandas as pd
from database import *

# Read in the csv file
df = pd.read_csv('teacher_feedback/validation_file.csv')

# Remove nulls (rows that haven't been validated)
df_filtered = df.dropna(subset=['Valid (Yes/No)'])

# Remove all unnecessary columns & rename to shorten
feedback_df = df_filtered[['submission_id', 'Valid (Yes/No)', 'Task Response Score CORRECTED', 
                           'Lexical Resource Score CORRECTED', 'Coherence and Cohesion Score CORRECTED', 
                           'Grammatical Range and Accuracy Feedback CORRECTED', 'Task Response Feedback CORRECTED', 
                           'Lexical Resource Feedback CORRECTED', 'Coherence and Cohesion Feedback CORRECTED', 
                           'Grammatical Range and Accuracy Score CORRECTED']]

feedback_df.rename(columns = {'Valid (Yes/No)':'valid', 
                              'Task Response Score CORRECTED':'tr_score_new', 
                              'Lexical Resource Score CORRECTED':'lr_score_new', 
                              'Coherence and Cohesion Score CORRECTED': 'cc_score_new', 
                              'Grammatical Range and Accuracy Feedback CORRECTED':'gr_score_new', 
                              'Task Response Feedback CORRECTED':'tr_feedback_new', 
                              'Lexical Resource Feedback CORRECTED':'lr_feedback_new', 
                              'Coherence and Cohesion Feedback CORRECTED':'cc_feedback_new', 
                              'Grammatical Range and Accuracy Score CORRECTED':'gr_feedback_new'}, inplace=True)

feedback = feedback_df.to_dict(orient="records")

for response in feedback: 

    submission_id = response["submission_id"]
    valid = response["valid"]

    # Get the current validated value from the submissions table (to check if it's already been validated)
    validated_value = get_validated_value(submission_id)

    try:
        if validated_value is not None:

            # If already validated, display error and move to the next record
            raise ValueError(f"Submission {submission_id} already validated")

        # If teacher agreed with model results
        if valid == "Yes":

            validated = True

            # Call the function to update the validated field of the submissions table to true
            update_validated(submission_id, validated) 

        # If teacher made changes to scores and/or feedback
        elif valid == "No":     

            validated = False 

            # Update the validated field in submissions table to false
            update_validated(submission_id, validated)

            # Fetch the original results data for this submission
            original_results = get_results(submission_id) 

            # Identify which fields have changed (which columns are not null) & log the changes
            results_logs = {}

            competency_map = {
                "tr": "Task Response",
                "lr": "Lexical Resource",
                "cc": "Coherence and Cohesion",
                "gr": "Grammatical Range and Accuracy"
            }

            for code, name in competency_map.items():

                score_field = f"{code}_score_new"
                feedback_field = f"{code}_feedback_new"

                score_changed = pd.notna(response.get(score_field))
                feedback_changed = pd.notna(response.get(feedback_field))

                # Build the dictionary for the logs
                if score_changed or feedback_changed:
                    results_logs[f"competency_{code}"] = {
                        "competency_name": name,
                        "original_score": original_results[name]["score"] if score_changed else None,
                        "new_score": response.get(score_field) if score_changed else None,
                        "original_feedback": original_results[name]["feedback"] if feedback_changed else None,
                        "new_feedback": response.get(feedback_field) if feedback_changed else None,
                    }

            # Call the database function for results log
            create_result_logs(submission_id, results_logs)

            # Prepare the changed data to pass to the update_results function
            new_data = []

            for entry in results_logs.values():

                updated_entry = {
                    "competency_name": entry["competency_name"],
                    "score": entry["new_score"], 
                    "feedback_summary": entry["new_feedback"] 
                }

                new_data.append(updated_entry)

            # Call the update results function and store the returned, latest results
            latest_scores = update_results(submission_id, new_data) 

            # Recalculate the overall score and update in the submissions table
            new_overall_score = calculate_overall_score(latest_scores)
            update_overall_score(submission_id, new_overall_score)

        # Else (if valid has something other than yes, no or blank)
        else:
            raise ValueError(f"Submission {submission_id} has unexpected valid value in file.")
        
    except Exception as e:
        print(f"Error processing submission {submission_id}: {e}")
