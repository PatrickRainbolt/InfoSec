# Included with Python
import os                           # Provides functions to interact with the operating system, such as file manipulation, environment variables, etc.
import stat                         # Defines constants and functions for interpreting file modes (permissions, type, etc.) returned by os.lstat() and os.stat().
import pwd                          # Used for retrieving user account information like the username associated with a user ID.
import grp                          # Used for retrieving group account information like the group name associated with a group ID.
import time                         # Provides time-related functions, such as converting timestamps to readable formats and sleeping for a certain duration.
import json                         # Provides functions for parsing and creating JSON (JavaScript Object Notation) data.
import csv                          # Provides tools for reading from and writing to CSV (Comma-Separated Values) files.
import shutil                       # Offers high-level file operations such as copying, removing directories, and archiving files.
import fnmatch                      # Provides functions for matching filenames using Unix shell-style wildcards (useful for filtering files).
import hashlib                      # Provides algorithms for hashing data (e.g., MD5, SHA-256) commonly used for integrity checks or securely storing passwords.
import base64                       # Provides functions for encoding and decoding binary data into base64, often used for text-based representation of binary data.
import logging                      # Provides a flexible framework for logging messages, useful for debugging and monitoring application behavior.
from copy import deepcopy           # Allows you to create a deep copy of objects, ensuring that nested objects are also copied rather than referenced.
from datetime import datetime       # Provides classes and functions for working with dates and times, including formatting and parsing datetime objects.

# Need to Install
from cryptography.fernet import Fernet  # A module from the 'cryptography' package for symmetric encryption. Fernet makes it easy to encrypt and decrypt data securely.
                                        # Installation: You can install it via pip: `pip install cryptography`


# Define the version of the script
VERSION = "1.1.0"

# Setup logger
logger = logging.getLogger("PyDir")
logger.setLevel(logging.INFO)  # Default to INFO

# Output to both terminal and optional log file
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Safe terminal width detection with fallback
WIDTH = shutil.get_terminal_size(fallback=(80, 24)).columns - 2

RED = '\033[91m'
RESET = '\033[0m'

def is_excluded(name, patterns):
    return any(fnmatch.fnmatch(name, pattern) for pattern in (patterns or []))

def has_valid_ext(filename, extensions):
    return any(filename.endswith(ext) for ext in (extensions or []))

def get_file_info(path, root_dir, do_hash=False):
    try:
        st = os.lstat(path)
        permissions = stat.filemode(st.st_mode)
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        size = st.st_size
        modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))

        rel_path = os.path.relpath(path, root_dir)
        root_name = os.path.basename(os.path.abspath(root_dir))
        full_rel_path = os.path.join(root_name, rel_path)

        info = {
            'permissions': permissions,
            'owner': owner,
            'group': group,
            'size': size,
            'modified': modified_time,
            'path': full_rel_path
        }

        if do_hash and os.path.isfile(path):
            try:
                hasher = hashlib.sha256()
                with open(path, "rb") as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                info['file_hash'] = hasher.hexdigest()
            except Exception as e:
                logger.warning(f"Failed to hash file {path}: {e}")
                info['file_hash'] = "ERROR"

        return info

    except Exception as e:
        print(f"Error getting info for {path}: {e}")
        return None

def derive_key_from_string(password_string):
    hashed = hashlib.sha256(password_string.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

def recursive_listing(start_path, include_ext=None, exclude_dirs=None, exclude_patterns=None, do_hash=False):
    file_list = []

    for dirpath, dirnames, filenames in os.walk(start_path):
        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if not is_excluded(d, exclude_dirs)]

        for name in filenames + dirnames:
            full_path = os.path.join(dirpath, name)

            # Skip files or dirs based on exclude patterns
            if is_excluded(name, exclude_patterns):
                continue

            # Filter by file extension
            if include_ext and not has_valid_ext(full_path, include_ext):
                continue

            info = get_file_info(full_path, start_path, do_hash=do_hash)
            if info:
                file_list.append(info)

    return file_list

def load_encrypted_data(file_path):
    import os

    prefix = "filedata_checksum:"

    # Try to read xattr key first
    try:
        base_key = os.getxattr(file_path, b"user.filedata_checksum").decode()
        with open(file_path, "r") as f:
            encrypted_lines = [line.strip() for line in f.readlines()]
    except (OSError, IOError):
        # Fallback to reading from file header
        with open(file_path, "r") as f:
            metadata = f.readline().strip()
            if not metadata.startswith(prefix):
                raise ValueError("Missing filedata_checksum in file")
            base_key = metadata[len(prefix):]
            encrypted_lines = [line.strip() for line in f.readlines()]

    decrypted = []
    for i, enc_line in enumerate(encrypted_lines):
        line_key = derive_key_from_string(f"{base_key}-{i}")
        fernet = Fernet(line_key)
        decrypted_line = fernet.decrypt(enc_line.encode()).decode()
        decrypted.append(json.loads(decrypted_line))

    return decrypted


def load_previous_data(file_path, require_hash=False):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".crypt":
        data = load_encrypted_data(file_path)
    elif ext == ".json":
        with open(file_path) as f:
            data = json.load(f)
    elif ext == ".csv":
        with open(file_path) as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
    else:
        logger.error(f"Unsupported compare file format: {ext}")
        return []

    # Validate file hash presence based on --HASH flag
    if require_hash:
        if any('file_hash' not in item for item in data):
            print("Error: One or more entries in the compare file are missing 'file_hash'.")
            print("    You must generate the file with --HASH to compare using hashes.")
            exit(1)
    else:
        if any('file_hash' in item for item in data):
            print("Error: Compare file contains hash data, but --HASH was not specified.")
            print("    To compare with hashes, rerun with --HASH.")
            exit(1)

    return data


def save_output(output, filename, output_format):
    # Save the output to a file in the requested format (text, json, csv)
    with open(filename, "w") as f:
        f.write(output)

def save_encrypted_output(data, folder_path):
    import os

    folder_name = os.path.basename(os.path.abspath(folder_path))
    output_file = f"{folder_name}.crypt"

    # Generate timestamp and key
    timestamp = datetime.now().strftime("File Created on %Y-%m-%d at %H:%M:%S")
    base_key = hashlib.sha256(timestamp.encode()).hexdigest()

    # Store base_key in extended file attribute (instead of file content)
    try:
        os.remove(output_file)  # Remove if exists to avoid xattr issues
    except FileNotFoundError:
        pass

    # Save placeholder file so we can apply xattr
    with open(output_file, "w") as f:
        f.write("")  # placeholder content

    try:
        os.setxattr(output_file, b"user.filedata_checksum", base_key.encode())
    except Exception as e:
        print(f"Failed to set xattr: {e}")
        print("Falling back to header method...")
        with open(output_file, "w") as f:
            f.write(f"filedata_checksum:{base_key}\n")

    # Encrypt each line with its line-specific key
    if not isinstance(data, list):
        data = [data]
    lines = [json.dumps(item) for item in data]

    encrypted_lines = []
    for i, line in enumerate(lines):
        line_key = derive_key_from_string(f"{base_key}-{i}")
        fernet = Fernet(line_key)
        encrypted = fernet.encrypt(line.encode()).decode()
        encrypted_lines.append(encrypted)

    # Append encrypted lines to the file
    with open(output_file, "a") as f:
        for line in encrypted_lines:
            f.write(line + "\n")

    print(f"Encrypted output saved to {output_file}")


def print_comparison(new_data, old_data, mute, column_header, output_format, compare, do_hash, save_file=False):
    if mute:
        return

    old_dict = {item['path']: item for item in old_data}
    new_dict = {item['path']: item for item in new_data}

    modified = []
    added = []
    deleted = []

    for path, current in new_dict.items():
        if path in old_dict:
            original = old_dict[path]
            changed_fields = []
            fields_to_compare = ['permissions', 'owner', 'group', 'size', 'modified']
            fields_to_compare += ['file_hash'] if do_hash else []

            for field in fields_to_compare:
                if str(original.get(field, '')) != str(current.get(field, '')):
                    changed_fields.append(field)

            if changed_fields:
                modified.append((current.copy(), changed_fields))
            del old_dict[path]
        else:
            added.append(current)

    deleted = list(old_dict.values())

    def format_line(entry, changed_fields=None):
        perms = f"{RED}{entry['permissions']}{RESET}" if changed_fields and 'permissions' in changed_fields else f"{entry['permissions']}"
        owner = f"{RED}{entry['owner']}{RESET}" if changed_fields and 'owner' in changed_fields else f"{entry['owner']}"
        group = f"{RED}{entry['group']}{RESET}" if changed_fields and 'group' in changed_fields else f"{entry['group']}"
        size = f"{RED}{int(entry['size']):>{10}}{RESET}" if changed_fields and 'size' in changed_fields else f"{int(entry['size']):>{10}}"
        modified = f"{RED}{entry['modified']}{RESET}" if changed_fields and 'modified' in changed_fields else f"{entry['modified']}"
        
        result = f"{perms:<14} {owner:<14} {group:<14} {size} {modified} {entry['path']}"

        # Add hash line, in red if it changed
        if 'file_hash' in entry:
            hash_display = f"{RED}{entry['file_hash']}{RESET}" if changed_fields and 'file_hash' in changed_fields else entry['file_hash']
            result += f"\n    File_Hash: {hash_display}"

        return result

    def generate_markdown(compare):
        def make_table(data, changed=False):
            widths = {
                'permissions': 12,
                'owner': 10,
                'group': 10,
                'size': 10,
                'modified': 20,
                'path': WIDTH - 80
            }

            header = f"| {'Permissions':<{widths['permissions']}} | {'Owner':<{widths['owner']}} | {'Group':<{widths['group']}} | {'Size':>{widths['size']}} | {'Modified':<{widths['modified']}} | {'Path':<{widths['path']}} |\n"
            separator = f"|{'-' * (widths['permissions'] + 2)}|{'-' * (widths['owner'] + 2)}|{'-' * (widths['group'] + 2)}|{'-' * (widths['size'] + 2)}|{'-' * (widths['modified'] + 2)}|{'-' * (widths['path'] + 2)}|\n"
            output = header + separator

            for row in data:
                if changed:
                    entry, changed_fields = row
                    def fmt(field, value):
                        return f"**{value}**" if field in changed_fields else str(value)
                else:
                    entry = row
                    fmt = lambda field, value: str(value)

                output += f"| {fmt('permissions', entry['permissions']):<{widths['permissions']}} " \
                        f"| {fmt('owner', entry['owner']):<{widths['owner']}} " \
                        f"| {fmt('group', entry['group']):<{widths['group']}} " \
                        f"| {fmt('size', entry['size']):>{widths['size']}} " \
                        f"| {fmt('modified', entry['modified']):<{widths['modified']}} " \
                        f"| {fmt('path', entry['path']):<{widths['path']}} |\n"

                if 'file_hash' in entry:
                    hash_line = f"File_Hash: {fmt('file_hash', entry['file_hash'])}"
                    line_len = WIDTH - 5
                    output += f"|    {hash_line:<{line_len}}|\n"

            output += f"|{'-' * (WIDTH - 1)}|\n"
            return output + "\n"

        output = ""

        if compare:
            if modified:
                output += "## 🔴 Modified Files\n\n"
                output += make_table(modified, changed=True)
            if added:
                output += "## 🟢 New Files\n\n"
                output += make_table(added)
            if deleted:
                output += "## 🗑️ Deleted Files\n\n"
                output += make_table(deleted)
        else:
            output += "## 📁 Directory Listing\n\n"
            output += make_table(modified + added + deleted)

        return output



    def generate_html(compare):
        def make_table(data, changed=None):
            table = "<table border='1' cellpadding='5' cellspacing='0'>"
            table += "<thead>\n   <tr>\n"
            table += "      <th>Permissions</th>\n"
            table += "      <th>Owner</th>\n"
            table += "      <th>Group</th>\n"
            table += "      <th>Size</th>\n"
            table += "      <th>Modified</th>\n"
            table += "      <th>Path</th>\n"
            table += "   </tr>\n</thead>\n<tbody>\n"
            for row in data:
                if changed:
                    entry, changed_fields = row
                else:
                    entry = row
                    changed_fields = []

                def highlight(field, value):
                    return f"<span style='color:red; font-weight:bold'>{value}</span>" if field in changed_fields else value

                table += "   <tr>\n"
                table += f"      <td>{highlight('permissions', entry['permissions'])}</td>\n"
                table += f"      <td>{highlight('owner', entry['owner'])}</td>\n"
                table += f"      <td>{highlight('group', entry['group'])}</td>\n"
                table += f"      <td style='text-align:right'>{highlight('size', entry['size'])}</td>\n"
                table += f"      <td>{highlight('modified', entry['modified'])}</td>\n"
                table += f"      <td>{entry['path']}</td>\n"
                table += "   </tr>\n"

            table += "</tbody>\n</table><br>\n"
            return table

        output = "<html><body style='font-family:sans-serif'>\n"

        if compare:
            if modified:
                output += "<h2>🔴 Modified Files</h2>\n"
                output += make_table(modified, changed=True)
            if added:
                output += "<h2>🟢 New Files</h2>\n"
                output += make_table(added)
            if deleted:
                output += "<h2>🗑️ Deleted Files</h2>\n"
                output += make_table(deleted)
        else:
            output += "<h2>📁 Directory Listing</h2>\n"
            output += make_table(modified + added + deleted)

        output += "</body></html>\n"
        return output

    def print_as_text():
        print("")
        if modified:
            if compare: 
                print("🔴 Modified Files:\n")
            if column_header:
                print(f"{'Permissions':<14} {'Owner':<14} {'Group':<14} {'Size':<10} {'Modified':<20} Path")
                print("-" * WIDTH)
            for entry, changed_fields in modified:
                print(format_line(entry, changed_fields))

        if added:
            if compare: 
                print("\n🟢 New Files:\n")
            if column_header:
                print(f"{'Permissions':<14} {'Owner':<14} {'Group':<14} {'Size':<10} {'Modified':<20} Path")
                print("-" * WIDTH)
            for entry in added:
                print(format_line(entry))

        if deleted:
            if compare: 
                print("\n🗑️  Deleted Files:\n")
            if column_header:
                print(f"{'Permissions':<14} {'Owner':<14} {'Group':<14} {'Size':<10} {'Modified':<20} Path")
                print("-" * WIDTH)
            for entry in deleted:
                print(format_line(entry))

    # Handle output format selection
    output = ""

    if output_format == "markdown":
        output = generate_markdown(compare)
    elif output_format == "html":
        output = generate_html(compare)
    elif output_format == "text":
        print_as_text()
        return  # Exit after printing text output
    elif output_format == "json":
        output = json.dumps({
            "modified": modified,
            "added": added,
            "deleted": deleted
        }, indent=4)
    elif output_format == "array":
        # Print in array format, like a nested JSON array
        output = json.dumps([
            [entry['permissions'], entry['owner'], entry['group'], entry['size'], entry['modified'], entry['path']] 
            for entry in modified + added + deleted
        ], indent=2)
    elif output_format == "csv":
        output = "permissions,owner,group,size,modified,path\n"
        for entry in modified + added + deleted:
            output += f"{entry['permissions']},{entry['owner']},{entry['group']},{entry['size']},{entry['modified']},{entry['path']}\n"

    # Save to file if requested
    if save_file:

        folder_name = os.path.basename(os.path.abspath(args.directory))
        output_filename = folder_name + "." + output_format
        save_output(output, output_filename, output_format)
        print(f"\nOutput saved to {output_filename}")

    # If not saving, but output was generated (non-text formats), print to stdout
    elif output:
        print(output)

    # Exit code signaling difference if applicable
    if modified or added or deleted:
        exit(2)

def main():
    parser = argparse.ArgumentParser(description="Recursive directory listing with metadata.")

    # Required positional argument
    parser.add_argument("directory", help="Path to the directory to list.")

    # Output configuration
    parser.add_argument("-F", "--format", dest="output_format",
                    choices=["text", "markdown", "html", "json", "csv", "array"],
                    help="Specify the output format. Required if saving output.")
    parser.add_argument("-S", "--save-output", action="store_true",
                        help="Save output to a file using the specified --output-format (not supported for text).")
    parser.add_argument("-X", "--crypt", action="store_true",
                    help="Encrypt output as a .crypt file (uses timestamp-based key")
    parser.add_argument("-H", "--column-header", action="store_true",
                        help="Display column headers in output")
    parser.add_argument("-I", "--include-hash", dest="do_hash", action="store_true",
                    help="Calculate SHA256 for each file and include it in the output.")
    parser.add_argument("-M", "--mute", action="store_true",
                        help="Suppress all output (quiet mode)")

    # Filtering options
    parser.add_argument("--include-ext", nargs="*", 
                        help="Only include specific file extensions (e.g. .py, .txt).")
    parser.add_argument("--exclude-dirs", nargs="*", 
                        help="Exclude specific directories (e.g. __pycache__, .git).")
    parser.add_argument("--exclude-pattern", nargs="*", 
                        help="Exclude files matching patterns (e.g. *.log, *.tmp).")

    # Comparison
    parser.add_argument("-C", "--compare", type=str, 
                        help="Path to a previous output file (json, csv) for comparison.")

    # Version info
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}",
                        help="Show the version of the program.")

    # Trouble Shooting
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--log-file", type=str, help="Write logs to a file instead of just the terminal.")

    if len(os.sys.argv) == 1:
        parser.print_help()
        os.sys.exit(0)

    args = parser.parse_args()

    # Adjust logging based on user flags
    if args.mute:
        logger.setLevel(logging.CRITICAL)
    elif args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if not os.path.isdir(args.directory):
        logger.error(f"{args.directory} is not a valid directory.")
        exit(1)


    results = recursive_listing(
        args.directory,
        include_ext=args.include_ext,
        exclude_dirs=args.exclude_dirs,
        exclude_patterns=args.exclude_pattern,
        do_hash=args.do_hash
    )

    if args.save_output and args.crypt:
        # Bypass regular format checks if encrypting
        save_encrypted_output(results, args.directory)
        exit(0)

    elif args.save_output:
        if not args.output_format:
            logger.error("--save-output requires --output-format to be specified.")
            exit(1)
        if args.output_format == "text":
            print("Error: Saving to file is not supported for 'text' format. Use markdown, json, csv, html, or array.")
            exit(1)

    if args.compare:
        old_data = load_previous_data(args.compare, require_hash=args.do_hash)
        print_comparison(
            results, old_data, args.mute, args.column_header,
            args.output_format or "text", args.compare, args.save_output
        )
    else:
        print_comparison(
            results, [], args.mute, args.column_header,
            args.output_format or "text", args.compare, args.save_output
        )


if __name__ == "__main__":
    main()
