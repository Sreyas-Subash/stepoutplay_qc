import os

# Path to the directory
directory = 'D:\stepout\qc\stepoutplay_qc\stepout_qc_code\excel_logs'

# List all files in the directory
files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

# Count the number of files
file_count = len(files)

print(f"Number of files in '{directory}': {file_count}")