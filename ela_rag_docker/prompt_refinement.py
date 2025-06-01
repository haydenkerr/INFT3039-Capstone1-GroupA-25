#import gspread
#from oauth2client.service_account import ServiceAccountCredentials

#json_path = os.path.join("ela_rag_docker", "refinement.json")


# Step 1: Authenticate
#scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
#client = gspread.authorize(creds)

# Step 2: Open the sheet
#sheet = client.open("Prompt Refinement").sheet1

# Step 3: Fetch and print a few rows
#data = sheet.get_all_records()
#for row in data[:5]:  # Print first 5 entries
#    print(row)



import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Setup credentials and scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
##json_path = os.path.join("ela_rag_docker", "refinement.json")
json_path = "refinement.json"
creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)

# Open Sheet
sheet = client.open("Prompt Refinement").sheet1
data = sheet.get_all_records()
all_rows = sheet.get_all_values()  # For raw cell-level access

# Headers and column positions
headers = all_rows[0]
processed_col = headers.index("Processed") + 1  # gspread is 1-indexed
first_data_row = 2  # Sheet data starts from row 2

# Open markdown file for appending
#md_path = os.path.join("ela_rag_docker", "prompt_refinement.md")
md_path = "prompt_refinement.md"
with open(md_path, "a", encoding="utf-8") as f:
    for i, row in enumerate(data):
        row_index = i + first_data_row
        is_approved = row.get("Approved for Integration", "").strip().lower() == "yes"
        is_processed = row.get("Processed", "").strip().lower() == "true"

        if is_approved and not is_processed:
            f.write("\n---\n")
            #f.write(f"### Task ID: {row.get('Task ID', '[None]')}\n")
            f.write(f"**Feedback Type**: {row.get('Feedback Type')}\n")
            f.write(f"**Suggested Change**: {row.get('Suggested Change')}\n\n")
            #f.write(f"**Reviewer**: {row.get('Reviewer')}\n")
            #f.write(f"**Timestamp**: {row.get('Submission Time')}\n")
            #f.write("---\n")

            # ✅ Mark as processed
            sheet.update_cell(row_index, processed_col, "TRUE")

print("✅ Feedback written to markdown and marked as processed.")

