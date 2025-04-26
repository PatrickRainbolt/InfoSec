import os
import sys
import tarfile
import json
from datetime import datetime

def extract_json_from_tar(tar_path):
    with tarfile.open(tar_path, "r:gz") as tar:
        json_file = next((m for m in tar.getmembers() if m.name.endswith('.json')), None)
        if not json_file:
            raise ValueError(f"No JSON file found in {tar_path}")
        f = tar.extractfile(json_file)
        if f:
            return json.load(f), json_file.name
        else:
            raise IOError(f"Could not extract JSON file from {tar_path}")

def compare_file_data(json1, json2):
    dict1 = {f['path']: f for f in json1}
    dict2 = {f['path']: f for f in json2}

    added = [dict2[p] for p in dict2 if p not in dict1]
    removed = [dict1[p] for p in dict1 if p not in dict2]
    modified = []

    for path in dict1:
        if path in dict2:
            if dict1[path]['file_hash'] != dict2[path]['file_hash']:
                modified.append((dict1[path], dict2[path]))

    return added, removed, modified

def generate_report(added, removed, modified, tar1, tar2):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base_name = f"Analysis-{timestamp}"
    os.makedirs(base_name, exist_ok=True)

    # Markdown report
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

    # JSON summary
    summary_path = os.path.join(base_name, f"{base_name}.json")
    with open(summary_path, 'w') as f:
        json.dump({
            "added": added,
            "removed": removed,
            "modified": [{"old": o, "new": n} for o, n in modified]
        }, f, indent=4)

    # Plain text report
    txt_path = os.path.join(base_name, f"{base_name}.txt")
    with open(txt_path, 'w') as f:
        f.write(f"Directory Comparison Report ({timestamp})\n")
        f.write(f"Compared: {tar1} ↔ {tar2}\n\n")
        f.write("Added Files:\n" + "\n".join(f"- {f['path']}" for f in added) + "\n\n")
        f.write("Removed Files:\n" + "\n".join(f"- {f['path']}" for f in removed) + "\n\n")
        f.write("Modified Files:\n" + "\n".join(f"- {o['path']}" for o, _ in modified) + "\n")

    print(f"\nReport generated in folder: {base_name}")

def main():
    if len(sys.argv) >= 3:
        tar1 = sys.argv[1]
        tar2 = sys.argv[2]
    else:
        tar1 = input("Enter path to first .tar.gz file: ").strip()
        tar2 = input("Enter path to second .tar.gz file: ").strip()

    if not os.path.isfile(tar1) or not tar1.endswith(".tar.gz"):
        print(f"Invalid file: {tar1}")
        return
    if not os.path.isfile(tar2) or not tar2.endswith(".tar.gz"):
        print(f"Invalid file: {tar2}")
        return

    print("Extracting JSON data...")
    data1, name1 = extract_json_from_tar(tar1)
    data2, name2 = extract_json_from_tar(tar2)

    print(f"Comparing files from {name1} and {name2}...")
    added, removed, modified = compare_file_data(data1, data2)

    print("Generating report...")
    generate_report(added, removed, modified, tar1, tar2)

if __name__ == "__main__":
    main()
