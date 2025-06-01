"""
Script to extract approved prompt refinements from a Google Sheet,
append them to a local markdown file, and push the update to a new branch
in the remote GitHub repository for review.

Requirements:
- gspread
- oauth2client
- git (installed and configured)
- Python 3.7+
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import subprocess
import datetime
import shutil

# --- Google Sheets Setup ---

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
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

# --- Markdown File Update ---

md_path = "prompt_refinement.md"
with open(md_path, "a", encoding="utf-8") as f:
    for i, row in enumerate(data):
        row_index = i + first_data_row
        is_approved = row.get("Approved for Integration", "").strip().lower() == "yes"
        is_processed = row.get("Processed", "").strip().lower() == "true"

        if is_approved and not is_processed:
            f.write("\n---\n")
            f.write(f"**Feedback Type**: {row.get('Feedback Type')}\n")
            f.write(f"**Suggested Change**: {row.get('Suggested Change')}\n\n")
            # Mark as processed in the sheet
            sheet.update_cell(row_index, processed_col, "TRUE")

print("✅ Feedback written to markdown and marked as processed.")

# --- GitHub Branch, Commit, and Push ---

REPO_PATH = "INFT3039-Capstone1-GroupA-25-System-Prompts"
MD_FILENAME = "prompt_refinement.md"
REMOTE_NAME = "origin"
BASE_BRANCH = "main"

def git_run(args, cwd):
    """Run a git command in the given directory and return output."""
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Git error: {result.stderr}")
        raise RuntimeError(f"Git command failed: {' '.join(args)}")
    return result.stdout.strip()

def update_and_push_prompt_refinement():
    """
    Copy the updated markdown file to the repo, create a branch, commit, and push for review.
    """
    # Ensure repo exists (clone if needed)
    if not os.path.exists(REPO_PATH):
        git_run([
            "clone",
            "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25-System-Prompts.git"
        ], cwd=".")

    # Copy the updated markdown file into the repo
    shutil.copyfile(MD_FILENAME, os.path.join(REPO_PATH, MD_FILENAME))

    # Create a new branch name with timestamp
    branch_name = f"prompt-refinement-update-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Git operations
    git_run(["checkout", BASE_BRANCH], cwd=REPO_PATH)
    git_run(["pull", REMOTE_NAME, BASE_BRANCH], cwd=REPO_PATH)
    git_run(["checkout", "-b", branch_name], cwd=REPO_PATH)
    git_run(["add", MD_FILENAME], cwd=REPO_PATH)
    git_run(["commit", "-m", "Update prompt_refinement.md via automation"], cwd=REPO_PATH)
    git_run(["push", REMOTE_NAME, branch_name], cwd=REPO_PATH)

    print(f"✅ Changes pushed to branch '{branch_name}' for review.")

# Call the update and push function after markdown update
update_and_push_prompt_refinement()