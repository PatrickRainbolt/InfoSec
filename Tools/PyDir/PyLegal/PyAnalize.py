# PyAnalyze.py
# 
# A utility to compare two .tar.gz archives containing JSON representations
# of directory/file structures. It identifies files that have been added,
# removed, or modified between the two archives and generates reports in
# Markdown, JSON, and plain text formats.
#
# Usage:
#     python PyAnalyze.py archive1.tar.gz archive2.tar.gz
#
# If no arguments are provided, the script will prompt the user to enter
# paths to the .tar.gz files.
#
# Reports are saved in a timestamped folder named 'Analysis-YYYY-MM-DD-HH-MM-SS'.

import os
import sys
import tarfile
import json
from datetime import datetime

# Function to extract the first JSON file from a .tar.gz archive
def extract_json_from_tar(tar_path):
    # Extracts JSON content from a .tar.gz archive
    # Parameters:
    #     tar_path (str): Path to the .tar.gz archive
    # Returns:
    #     tuple: (data, json_file_name)
    #         - data (list/dict): Parsed JSON content
    #         - json_file_name (str): Name of the extracted JSON file
    # Raises:
    #     ValueError: If no JSON file is found in the archive
    #     IOError: If the JSON file cannot be extracted

    # Open the .tar.gz file in read mode
    with tarfile.open(tar_path, "r:gz") as tar:
        # Find the first member whose name ends with '.json'
        json_file = next((m for m in tar.getmembers() if m.name.endswith('.json')), None)
        if not json_file:
            raise ValueError(f"No JSON file found in {tar_path}")
        
        # Extract the JSON file object
        f = tar.extractfile(json_file)
        if f:
            return json.load(f), json_file.name
        else:
            raise IOError(f"Could not extract JSON file from {tar_path}")

# Function to compare two lists of file metadata
def compare_file_data(json1, json2):
    # Compares two JSON file lists to find added, removed, and modified files
    # Parameters:
    #     json1 (list): File data from the first archive
    #     json2 (list): File data from the second archive
    # Returns:
    #     tuple: (added, removed, modified)
    #         - added (list): Files present in json2 but not in json1
    #         - removed (list): Files present in json1 but not in json2
    #         - modified (list): Files present in both but with different file hashes (old, new)

    # Convert lists of files into dictionaries keyed by file path for faster lookup
    dict1 = {f['path']: f for f in json1}
    dict2 = {f['path']: f for f in json2}

    # Identify added files
    added = [dict2[p] for p in dict2 if p not in dict1]

    # Identify removed files
    removed = [dict1[p] for p in dict1 if p not in dict2]

    # Identify modified files
    modified = []
    for path in dict1:
        if path in dict2:
            if dict1[path]['file_hash'] != dict2[path]['file_hash']:
                modified.append((dict1[path], dict2[path]))

    return added, removed, modified

# Function to generate Markdown, JSON, and plain text reports
def generate_report(added, removed, modified, tar1, tar2):
    # Generates a comparison report
    # Parameters:
    #     added (list): List of files added in the second archive
    #     removed (list): List of files removed in the second archive
    #     modified (list of tuples): List of tuples (old_file, new_file) for modified files
    #     tar1 (str): Path to the first archive
    #     tar2 (str): Path to the second archive

    # Create a timestamped folder for report outputs
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base_name = f"Analysis-{timestamp}"
    os.makedirs(base_name, exist_ok=True)

    # --- Markdown Report ---
    md_path = os.path.join(base_name, f"{base_name}.md")
    with open(md_path, 'w') as f:
        f.write(f"# Directory Comparison Report\n\n")
        f.write(f"Compared archives:\n- {tar1}\n- {tar2}\n\n")
        f.write(f"Generated on: {timestamp}\n\n")

        f.write("## Added Files\n")
        for item in added:
            f.write(f"- {item['path']}\n")

        f.write("\n## Removed Files\n")
        for item in removed:
            f.write(f"- {item['path']}\n")

        f.write("\n## Modified Files\n")
        for old, new in modified:
            f.write(f"- {old['path']}\n")

    # --- JSON Summary ---
    summary_path = os.path.join(base_name, f"{base_name}.json")
    with open(summary_path, 'w') as f:
        json.dump({
            "added": added,
            "removed": removed,
            "modified": [{"old": o, "new": n} for o, n in modified]
        }, f, indent=4)

    # --- Plain Text Report ---
    txt_path = os.path.join(base_name, f"{base_name}.txt")
    with open(txt_path, 'w') as f:
        f.write(f"Directory Comparison Report ({timestamp})\n")
        f.write(f"Compared: {tar1} ↔ {tar2}\n\n")
        f.write("Added Files:\n" + "\n".join(f"- {f['path']}" for f in added) + "\n\n")
        f.write("Removed Files:\n" + "\n".join(f"- {f['path']}" for f in removed) + "\n\n")
        f.write("Modified Files:\n" + "\n".join(f"- {o['path']}" for o, _ in modified) + "\n")

    print(f"\nReport generated in folder: {base_name}")

# Main function orchestrating the workflow
def main():
    # Get archive paths from command line or user input
    if len(sys.argv) >= 3:
        tar1 = sys.argv[1]
        tar2 = sys.argv[2]
    else:
        tar1 = input("Enter path to first .tar.gz file: ").strip()
        tar2 = input("Enter path to second .tar.gz file: ").strip()

    # Validate files exist and are .tar.gz
    if not os.path.isfile(tar1) or not tar1.endswith(".tar.gz"):
        print(f"Invalid file: {tar1}")
        return
    if not os.path.isfile(tar2) or not tar2.endswith(".tar.gz"):
        print(f"Invalid file: {tar2}")
        return

    # Extract JSON data
    print("Extracting JSON data...")
    data1, name1 = extract_json_from_tar(tar1)
    data2, name2 = extract_json_from_tar(tar2)

    # Compare file data
    print(f"Comparing files from {name1} and {name2}...")
    added, removed, modified = compare_file_data(data1, data2)

    # Generate report
    print("Generating report...")
    generate_report(added, removed, modified, tar1, tar2)

# Entry point of the script
if __name__ == "__main__":
    main()
