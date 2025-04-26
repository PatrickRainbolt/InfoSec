# PyDir.py - Recursive Directory Listing with Metadata

## Overview

**PyDir** is a Python-based script designed for recursively listing files in a directory, including detailed metadata about each file. It supports various output formats, including text, Markdown, HTML, JSON, CSV, and custom array formats. Additionally, it can compare the current directory's state against a previously saved state, highlighting added, deleted, and modified files. For security, it also supports encryption of output using the `cryptography` library.

## Features

- **Recursive Directory Listing**: Recursively lists all files in the provided directory.
- **File Metadata**: Retrieves detailed metadata such as permissions, owner, group, size, and last modified time.
- **File Hashing**: Supports generating SHA256 hashes for file integrity checks (optional).
- **Data Comparison**: Allows comparing the current directory to a previous output (in JSON, CSV, or encrypted format), and highlights added, deleted, or modified files.
- **Flexible Output Formats**: Outputs results in several formats, including:
  - **Text**: A simple text format for easy reading.
  - **Markdown**: A Markdown table format.
  - **HTML**: An HTML table format.
  - **JSON**: A structured JSON format.
  - **CSV**: A comma-separated value format.
  - **Array**: A nested array format similar to JSON.
- **Encryption Support**: Encrypts the output data into a `.crypt` file format using a timestamp-based key for secure data storage.
- **File Filtering**: Includes options to filter files based on extensions or patterns, and exclude specific directories from the listing.

## Installation

You need Python 3.6 or higher to run this script. Additionally, the script uses the `cryptography` library, which you can install using pip.

### Prerequisites

- Python 3.x
- `cryptography` library

Install the required dependencies using:

```bash
pip install cryptography
```

## Usage

### Command-Line Arguments

To run the script, use the following command structure:

```bash
python pydir.py <directory> [options]
```

#### Required Arguments:

- `directory`: The path to the directory you want to list. It should be a valid directory path on your system.

#### Optional Arguments:

- `-F`, `--format`: Specify the output format. Options include:
  - `text`
  - `markdown`
  - `html`
  - `json`
  - `csv`
  - `array`
  
- `-S`, `--save-output`: Save the output to a file using the specified `--format` argument (not supported for text output).
- `-X`, `--crypt`: Encrypt the output as a `.crypt` file using a timestamp-based key.
- `-H`, `--column-header`: Display column headers in the output.
- `-I`, `--include-hash`: Include SHA256 file hashes in the output for each file.
- `-M`, `--mute`: Suppress all output (quiet mode).
- `--include-ext`: Only include files with specified extensions (e.g., `.py`, `.txt`).
- `--exclude-dirs`: Exclude specific directories from the listing (e.g., `__pycache__`, `.git`).
- `--exclude-pattern`: Exclude files that match specific patterns (e.g., `*.log`, `*.tmp`).
- `-C`, `--compare`: Path to a previous output file (JSON, CSV) for comparison.
- `-v`, `--version`: Display the version of the program.

### Example Usage

1. **Simple directory listing** (text format):
    ```bash
    python pydir.py /path/to/directory --format text
    ```

2. **Directory listing with hashes** (JSON format):
    ```bash
    python pydir.py /path/to/directory --format json --include-hash
    ```

3. **Compare current directory with previous JSON output**:
    ```bash
    python pydir.py /path/to/directory --compare previous_output.json --format markdown
    ```

4. **Encrypt the output as `.crypt` file**:
    ```bash
    python pydir.py /path/to/directory --crypt
    ```

5. **Save the output as CSV**:
    ```bash
    python pydir.py /path/to/directory --save-output --format csv
    ```

6. **Recursive listing with specific file extensions**:
    ```bash
    python pydir.py /path/to/directory --include-ext .txt .py
    ```

### Supported Output Formats

- **Text**: Displays the file metadata in a human-readable format.
- **Markdown**: Outputs the file metadata in a Markdown table.
- **HTML**: Displays the file metadata in an HTML table.
- **JSON**: Outputs the file metadata in a structured JSON format.
- **CSV**: Lists the file metadata as CSV entries.
- **Array**: Outputs the data as a nested array.

### File Comparison

If a previous output file is provided (using the `--compare` argument), the script will compare the current directory state to the previous one, highlighting:
- **Added Files**: Files that are new.
- **Deleted Files**: Files that no longer exist.
- **Modified Files**: Files that have changed in terms of permissions, owner, group, size, or last modified timestamp (and file hash if specified).

### Encryption

When using the `--crypt` option, the script generates an encrypted `.crypt` file containing the directory metadata. The encryption is based on a timestamp-derived key, and the metadata is encrypted using the `cryptography` library's `Fernet` encryption scheme.

## Example Output (Markdown)

The Markdown output of the directory listing could look like this:

```markdown
## 📁 Directory Listing

| Permissions | Owner    | Group   | Size | Modified            | Path                    |
|-------------|----------|---------|------|---------------------|-------------------------|
| -rw-r--r--  | user     | users   | 1234 | 2025-04-25 12:34:56 | /path/to/file1.txt      |
| -rw-r--r--  | user     | users   | 5678 | 2025-04-25 12:35:00 | /path/to/file2.txt      |
```

## Logging

The script has built-in logging that provides feedback and troubleshooting information. You can adjust the log level with the `--debug` or `--mute` options. If you wish to store logs in a file, you can specify the log file using the `--log-file` argument.

### License
This project is licensed under the [MIT License](LICENSE).

Thank you for your interest in this project, and we appreciate any support you can provide during its development!
