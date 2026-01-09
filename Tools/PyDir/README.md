
# File Auditing & Change Tracking Tools for Business Leaders

This suite of tools—**PyDir**, **PyLegal**, and **PyAnalyze**—offers a lightweight yet powerful solution for file system visibility, digital auditing, and change detection. Together, they help organizations answer three fundamental questions:

> **What files exist? What’s changed? Can we prove it?**

---

## Tool Summaries

### PyDir

- Scans a target directory and recursively lists every file.
- Captures detailed metadata:
  - File size
  - Permissions
  - Ownership
  - Timestamps
  - File Hash
- Supports multiple export formats:
  - Markdown
  - HTML
  - CSV
  - JSON
- Offers file filtering, output encryption, and comparison features.
- Ideal for:
  - Compliance reporting
  - Internal audits
  - Operational documentation

---

### PyLegal

- Captures a full forensic snapshot of a directory.
- Collects and logs metadata and SHA-256 hashes for every file.
- Generates reports in multiple formats:
  - JSON
  - CSV
  - Markdown
  - HTML
  - Raw CSV
- Packages all outputs into a single `.tar.gz` archive for integrity and portability.
- Designed for:
  - Legal holds
  - Digital compliance
  - Baseline snapshotting

---

### PyAnalyze

- Compares two `.tar.gz` archives created by PyLegal.
- Detects and lists:
  - Added files
  - Removed files
  - Modified files (via SHA-256 comparison)
- Outputs comparison results in:
  - Markdown
  - JSON
  - Plain text
- Useful for:
  - Unauthorized change detection
  - Breach investigation
  - Configuration drift analysis


## Business Value

Together, these tools provide a **low-cost, high-impact way to improve transparency, enforce compliance, and detect change across digital assets**. With no external dependencies and a simple interface, they are well-suited for IT teams, auditors, legal counsel, and security officers looking to maintain oversight without adding infrastructure.

---

## Licensing

This suite is released under the [MIT License](../../LICENSE.md).
