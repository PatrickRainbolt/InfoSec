import os
import pwd
import grp
import stat
import sys
import shutil
import json
import hashlib
import time
import csv
import tarfile
from datetime import datetime

def generate_file_info(path, base_directory):
    """Generate detailed file information relative to base_directory."""
    try:
        st = os.lstat(path)
        file_info = {
            'path': os.path.relpath(path, start=base_directory),
            'permissions': stat.filemode(st.st_mode),
            'owner': pwd.getpwuid(st.st_uid).pw_name,
            'group': grp.getgrgid(st.st_gid).gr_name,
            'size': st.st_size,
            'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(path)))
        }

        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        file_info['file_hash'] = hasher.hexdigest()

        return file_info
    except Exception as e:
        print(f"Error generating file info for {path}: {e}")
        return None

def generate_report(directory):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    folder_name = os.path.basename(os.path.abspath(directory))
    temp_folder = f"{folder_name}-{timestamp}"

    os.makedirs(temp_folder, exist_ok=True)

    file_list = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            file_info = generate_file_info(full_path, directory)
            if file_info:
                file_list.append(file_info)

    fieldnames = ['path', 'permissions', 'owner', 'group', 'size', 'modified', 'file_hash']

    # JSON
    with open(os.path.join(temp_folder, f"{folder_name}.json"), 'w') as f:
        json.dump(file_list, f, indent=4)

    # CSV
    with open(os.path.join(temp_folder, f"{folder_name}.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(file_list)

    # Markdown
    with open(os.path.join(temp_folder, f"{folder_name}.md"), 'w') as f:
        f.write(f"# File Report for {folder_name}\nGenerated on {timestamp}\n\n")
        f.write("| Path | Permissions | Owner | Group | Size | Modified | File Hash |\n")
        f.write("|------|-------------|-------|-------|------|----------|-----------|\n")
        for info in file_list:
            f.write(f"| {info['path']} | {info['permissions']} | {info['owner']} | {info['group']} | "
                    f"{info['size']} | {info['modified']} | {info['file_hash']} |\n")

    # HTML
    with open(os.path.join(temp_folder, f"{folder_name}.html"), 'w') as f:
        f.write(f"<html><body><h1>File Report for {folder_name}</h1>\n<p>Generated on {timestamp}</p>\n")
        f.write("<table border='1'>\n   <tr><th>Path</th><th>Permissions</th><th>Owner</th><th>Group</th>"
                "<th>Size</th><th>Modified</th><th>File Hash</th></tr>\n")
        for info in file_list:
            f.write(f"   <tr><td>{info['path']}</td><td>{info['permissions']}</td><td>{info['owner']}</td>"
                    f"<td>{info['group']}</td><td>{info['size']}</td><td>{info['modified']}</td>"
                    f"<td>{info['file_hash']}</td></tr>\n")
        f.write("</table></body></html>")

    # .raw CSV
    with open(os.path.join(temp_folder, f"{folder_name}.raw"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(file_list)

    # Tar + gzip
    tar_file = f"{temp_folder}.tar.gz"
    with tarfile.open(tar_file, "w:gz") as tar:
        tar.add(temp_folder, arcname=os.path.basename(temp_folder))

    shutil.rmtree(temp_folder)
    print(f"\nReports created and saved to: {tar_file}")

def main():
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = input("Enter the directory path to process: ").strip()

    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.")
        return

    generate_report(directory)

if __name__ == "__main__":
    main()
