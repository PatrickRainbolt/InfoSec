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

---

## Technical Deep Dive
## Data Storage in PyWhiteNoise: Normal vs Stealth Mode

PyWhiteNoise hides encrypted data in WAV audio files by modifying the **least significant bit (LSB)** of 16-bit audio samples. It supports two modes: **normal mode** (default) and **stealth mode** (`-stealth` flag). Both modes use strong encryption (AES-GCM with Scrypt key derivation), but differ significantly in how bits are placed in the audio to resist detection.

## Shared Concepts (Both Modes)

- **Audio Format**: Mono, 16-bit samples (values 0–65535 after conversion from signed).
- **Embedding Method**: Only the LSB is changed (`samples[i] = (samples[i] & 0xFFFE) | bit`).
- **Capacity**: 1 bit per sample.
- **Header**: 160 bits total
  - 32 bits: payload length (in bits)
  - 128 bits: encryption salt
- **Payload**: AES-GCM nonce (12 bytes) + ciphertext.
- **Carrier**: Either generated noise (white or pink) or an existing WAV (`-input-wav`).
- **Post-Processing (Stealth only)**: Unused LSBs are randomized for statistical uniformity.

## Normal Mode (No `-stealth`)

Embedding is **sequential and contiguous**, making it simple and fast but easier to detect.

### Encoding Process

1. **Encrypt data** → get payload bits.
2. **Build header** → length (4 bytes) + salt (16 bytes) → 160 bits.
3. **Generate or load samples**.
4. **Sequential embedding**:
   - Samples 0–159: Header bits (starting at index 0).
   - Samples 160 onward: Payload bits (immediately after header).
5. **Write WAV** (no further changes).

### Storage Layout Example

For a payload requiring 800 bits:

| Sample Index | Content                  |
|--------------|--------------------------|
| 0–159        | Header bits (sequential) |
| 160–959      | Payload bits (sequential)|
| 960+         | Original/unmodified      |

### Detectability

- High: Tools can extract the first 160 LSBs and check for high-entropy salt + plausible length.
- Your built-in `analyze_wav` detects this easily (legacy sequential candidate).

### Advantages / Disadvantages

- Fast encoding/decoding.
- Vulnerable to simple steganalysis.
- Obvious if someone inspects the beginning of the file.

## Stealth Mode (`-stealth`)

All bits are **scattered pseudo-randomly** using password-seeded PRNGs, the header is encrypted, and unused LSBs are randomized. This provides strong resistance to detection.

### Encoding Process

1. **Encrypt data** → same as normal.
2. **Encrypt header**:
   - Header bytes XORed with a repeating key derived from `SHA256(password + b"header_key")`.
   - Makes the header look completely random even if extracted.
3. **Generate/load samples** (with extra padding).
4. **Scattered embedding**:
   - **Header**:
     - PRNG seeded with `SHA256(password + b"header")`.
     - Generate 160 unique random indices across all samples.
     - Embed encrypted header bits at those positions.
   - **Payload**:
     - PRNG seeded with `SHA256(password + b"payload")` (different context → different indices).
     - Generate indices for all payload bits.
     - If any overlap with header indices → regenerate payload indices (up to 100 attempts).
     - Embed payload bits at the final positions.
5. **Randomize unused LSBs**:
   - PRNG seeded with `SHA256(password + b"lsb_noise")`.
   - Every sample not used for header or payload gets a random LSB (0 or 1).
   - Ensures ~50/50 distribution across the entire file.

### Storage Layout Example

Same 800-bit payload, 600,000 samples:

| Sample Index | Content                                      |
|--------------|----------------------------------------------|
| Random 160 positions | Encrypted header bits                        |
| Random ~800 other positions | Payload bits                                 |
| All remaining positions | Randomized LSBs (password-seeded noise)      |

No fixed starting point — positions depend entirely on the password.

### Detectability

- Very low without the password.
- Sequential scans find nothing meaningful.
- Header appears random (due to XOR encryption).
- LSB statistics look perfectly uniform.
- Even advanced steganalysis (chi-square, RS, sample-pair) struggles, especially in noise carriers or real audio.

### Advantages / Disadvantages

- Excellent plausible deniability.
- Slightly slower (multiple shuffles + collision checks).
- More robust against cropping (as long as enough samples remain).

## Summary Comparison

| Feature                  | Normal Mode                     | Stealth Mode                              |
|--------------------------|---------------------------------|-------------------------------------------|
| Embedding Style          | Sequential (fixed positions)    | Scattered (password-dependent PRNG)       |
| Header Protection        | Plain (high entropy → detectable) | Encrypted + scattered                    |
| Unused LSBs               | Left as-is                      | Randomly set (uniform distribution)      |
| Collision Handling       | N/A                             | Regenerate indices if overlap            |
| Detection Difficulty     | Medium (easy header spotting)   | High (requires password)                 |
| Speed                    | Faster                          | Slightly slower                          |
| Best For                 | Testing, low-risk use           | Real covert scenarios                    |

Both modes provide **confidentiality** through strong encryption.  
**Stealth mode** adds true **steganographic security** — hiding the very existence of the data.

