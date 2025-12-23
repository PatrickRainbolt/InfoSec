# PyWhiteNoise v1.4 — Complete Overview

PyWhiteNoise is a command-line steganography tool that hides arbitrary encrypted data inside WAV audio files using **least significant bit (LSB) embedding**. It generates white or pink noise as a carrier by default, or can embed into an existing real-world audio file for greater plausible deniability. Data is always encrypted with **AES-GCM** using a key derived from a user-provided password via **Scrypt**, ensuring confidentiality even if the embedding is detected.

The tool offers two modes:
- **Normal mode** - sequential embedding (faster, easier to detect).
- **Stealth mode** (`-stealth`) - scattered embedding with password-seeded PRNGs, encrypted header, and randomization of unused LSBs (highly resistant to detection).

It includes a built-in analyzer (`-analyze`) that attempts legacy detection and explains why ultra-stealth files are difficult to spot without the password.

## Key Features

- Strong cryptography: Scrypt + AES-GCM.
- Flexible carriers: generated noise or real audio via `-input-wav`.
- Noise types: white or pink (`-noise-type pink`).
- Ultra-stealth mode: scatters header and payload, encrypts header, randomizes unused LSBs.
- Self-contained analysis tool.
- Supports hiding any binary data (files, text, etc.) from stdin or a file.

## Command-Line Usage

```
./PyWhiteNoise.py [options]
```

### Main Operation Modes (mutually exclusive)

| Flag          | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| `-encode`     | Encode (hide) data into a WAV file.                                         |
| `-decode`     | Decode (extract) hidden data from a WAV file.                               |
| `-analyze`    | Analyze a WAV file for signs of hidden data (legacy + basic stealth checks).|
| `-version`    | Print version (`1.4`) and exit.                               |

### Required Arguments

| Flag     | Description                                      |
|----------|--------------------------------------------------|
| `-wav`   | Path to the output WAV (encode) or input WAV (decode/analyze). Required for `-encode`, `-decode`, or `-analyze`. |

### Input Data Options (for `-encode`)

| Flag         | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| `-infile`    | Path to a file containing the data to hide (binary-safe).                   |
| `-stdin`     | Read data from standard input (e.g., `cat secret.bin | ./PyWhiteNoise.py ...`). Use with `-encode`. |
| **Note**     | You must provide **either** `-infile` **or** `-stdin`.                      |

### Stealth & Carrier Options

| Flag               | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `-stealth`         | Enable ultra-stealth mode: scatter header & payload, encrypt header, randomize unused LSBs. |
| `-noise-type <option>` | Choose generated carrier noise type between `white` or `pink`. Only used when no `-input-wav` is given. |
| `-input-wav <path>`| Instead of generating noise, embed into an existing WAV file (greatly increases plausible deniability). |

### Help

If no valid combination of flags is given, the tool prints the help message automatically.

## Example Commands

```bash
# Basic encode (normal mode) - hide a file in generated white noise
./PyWhiteNoise.py -encode -wav cover.wav -infile secret.pdf

# Stealth encode with pink noise
./PyWhiteNoise.py -encode -wav cover.wav -infile secret.pdf -stealth -noise-type pink

# Stealth encode into real audio (highest deniability)
./PyWhiteNoise.py -encode -wav stego_music.wav -input-wav original_music.wav -infile payload.exe -stealth

# Decode (prompts for password)
./PyWhiteNoise.py -decode -wav stego_music.wav -stealth

# Analyze a suspicious file
./PyWhiteNoise.py -analyze -wav suspicious.wav
```

---

## Licensing

This suite is released under the [MIT License](LICENSE.md).

