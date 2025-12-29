# Educational Proof-of-Concept

** This document describes a proof-of-concept technique for combining modern cryptography with steganography by embedding encrypted payloads within syntactically valid but innocuous-looking source code. The content is provided strictly for educational and security research purposes—to illustrate novel covert channel possibilities, encourage the development of better detection methods, and promote deeper understanding of data-hiding risks in software artifacts. The author does not condone or encourage the use of these techniques for any illegal, unethical, or malicious activity. Readers are reminded that hiding illicit material remains illegal regardless of the concealment method, and responsible disclosure practices should always be followed when exploring or publishing security-related concepts.

---

# PyCryptoArt v2.3 - Complete Overview

**Hide encrypted messages and files in beautiful retro-style ASCII art**

PyCryptoArt is a cryptographic steganography tool that conceals secret text or **any binary file** (images, PDFs, executables, etc.) inside authentic-looking geometric ASCII art created from Unicode box-drawing characters.

The resulting ".txt" file looks like pure vintage terminal art while securely protecting your data with modern authenticated encryption.

## Features

- **Strong authenticated encryption** using AES-256-GCM
- **Passphrase-based key derivation** via PBKDF2-HMAC-SHA256 (480,000 iterations)
- **Random 16-byte salt + 12-byte nonce** per encryption
- **Polyalphabetic diffusion layer** (Vigenère-style nibble shifting derived from salt+nonce) → eliminates visual patterns; identical inputs produce completely different art every time
- **Full binary support** - hide images, documents, archives, anything
- **Zero metadata leakage** in the visual output
- **High plausible deniability** - output resembles genuine retro ANSI/ASCII art
- **Safe file handling** - refuses to overwrite existing files during encryption
- **Debug mode** for learning and troubleshooting

## Example Output (hiding a photo)

```
---------------------------------------------------------------PyCryptoArt 2.3--
╧╟╥╩╟╓╚╩╥╧╟═╟╨╦╓╟╦╦╙╩╨╩╟╩╦╤╚╦╙╨╚╓──╓╥╒╘╧═╦╚╧╩╤╒╤╓═╠╥═╤╟╩╦╘╨╥╠╨╓╤╘╠╘╩╚╙╩╟╠╤╧═╥╠╙╦
╟╔═╟╓╠╧╨╒╙╟╙╨╚╘╨╩╚╓═╔─╔╓─╥╩╨╤╒╥╙─╦╥╤╤╔╙╨╧╩╒╟─╓╓╙╤╚╥╥╒╟╨╥─╩╨╒╔╔═╧═╤╚╔╒═╟╙╔╘╔╘╚╩╓╥
╓╥╘╧╨╤╠╠╚╙╘─╔╟╘╥─╥╩╦╦╠╤╧╤╦╘═╥╘╦╩╤╩╤╨╙╤══╟╒╙╘╩╚╘╟╒╠╦═╦─╥╓─╟╤╠╚╥╔╘─╚─╓╥╦╨╘╧╤─╘╚╦╨╒
...
--------------------------------------------------------------------------------
```

This massive art block securely hides an entire JPEG image.


## Usage

### Encrypt

**Text message:**
```bash
echo "Secret message from December 29, 2025" | python3 PyCryptoArt.py --stdin -m encrypt --outfile secret_art.txt
```

**Binary file (image, PDF, etc.):**
```bash
python3 PyCryptoArt.py -m encrypt --infile photo.jpg --binary --outfile photo_art.txt
```

### Decrypt

**Text:**
```bash
python3 PyCryptoArt.py -m decrypt --infile secret_art.txt
```

**Binary (recover original file):**
```bash
python3 PyCryptoArt.py -m decrypt --infile photo_art.txt --binary --outfile recovered.jpg
```

You will be prompted securely for your passphrase.

### Debug Mode
Add `--debug` to see the cryptographic steps (salt, nonce, shift sequence, lengths, etc.).

```bash
echo "Secret message from December 29, 2025" | python3 PyCryptoArt.py --stdin -m encrypt --debug
[DEBUG] Starting PyCryptoArt v2.3 in encrypt mode
Enter passphrase: 
[DEBUG] Input data length: 37 bytes
[DEBUG] Generated salt: 158d697735b3c9a571e749c9d6a0396b
[DEBUG] Generated nonce: 1bad2d3fb3b84cd963f02f75
[DEBUG] Ciphertext length: 37 bytes
[DEBUG] Authentication tag: 6f8947c55cdba2f35e6ecfec0d3a9e73
[DEBUG] Shift sequence (16 values): [5, 13, 9, 7, 5, 3, 9, 5, 1, 7, 9, 9, 6, 0, 9, 11]
[DEBUG] Final art length: 162 characters
[DEBUG] Number of 80-char lines: 3
---------------------------------------------------------------PyCryptoArt 2.2--

╚╠╨╒═╤╧╧╩╠╙╩╘╤╥╠╧╚╓╧╦╤╘╤╒═╥╟╩╤═╙╚╙╥╒╔╒╩─╙╩╙╨╦╘╒╤═╩─╟╔─╧╠╥═╓╔╘╔╩╟╘╒╠╤╠╙╧╠╓╧╓╚╟╔╙╚
╨╔╦═╠╔╧╚╒╨──╨╦─╟╙═╓─╒╠╙╧─╠╩╨╩╒═╩╩╨╠═╒╔╤╠╙╤╧╚╧╩╤╔╚╨─╨╓╤╒╔╚╔╓╩╔╓╩╧╟╥╓╧╘╓╠╥╩╤╤╦╨╒╔╩
╨╥

--------------------------------------------------------------------------------
```

## Command-line Options

```
-m, --mode          encrypt (default) or decrypt
--infile FILE       Input file (text or binary)
--outfile FILE      Output file (art in encrypt; recovered data in decrypt)
--stdin             Read input from stdin
--binary            Treat input/output as raw binary data (required for non-text files)
-k, --key           Passphrase (if omitted, prompted securely)
-d, --debug         Enable detailed debug output
-v, --version       Show version
```

## Security Notes

- Uses AES-256-GCM via the battle-tested `cryptography` library
- Proper authenticated encryption - tampering is detected
- No plaintext or keys are written to disk
- Random salt + nonce prevent replay/rainbow attacks
- Diffusion layer removes visual correlations
- **Intended for educational, research, and artistic purposes only**

**Warning**: Strong encryption does not protect against weak passphrases, side-channel attacks, or compromised systems.


---
## Licensing

This suite is released under the [MIT License](LICENSE.md).<br><br><br><br><br>
---

## Technical Deep Dive: Data Storage in PyCryptoArt

**How PyCryptoArt works: A step-by-step explanation of the cryptography, steganography, and visual diffusion**

This document provides a detailed, educational walkthrough of the inner workings of **PyCryptoArt v2.3**. It is intended for learners, security researchers, and curious developers who want to understand how modern authenticated encryption is combined with steganographic obfuscation and visual diffusion to hide arbitrary data inside retro-style ASCII art.

## Overview of the Process

### Encryption Flow
1. **Input** → any text or binary file (bytes)
2. Generate random **salt** (16 bytes) and **nonce** (12 bytes)
3. Derive encryption key from passphrase using **PBKDF2-HMAC-SHA256**
4. Encrypt data with **AES-256-GCM** → ciphertext + 16-byte authentication tag
5. Concatenate: `salt || nonce || ciphertext || tag`
6. Convert to hexadecimal string
7. Apply **polyalphabetic nibble shifting** (Vigenère-style) to the ciphertext + tag portion only
8. Map each hex digit to a Unicode box-drawing character
9. Format into 80-character lines with decorative header/footer

### Decryption Flow
The reverse of the above, with exact reconstruction of the shift sequence and verification of the GCM authentication tag.

## Step-by-Step Breakdown

### 1. Input Handling
- Text mode (`--binary` not used): input is treated as UTF-8 string → encoded to bytes
- Binary mode (`--binary`): input is read as raw bytes (images, PDFs, executables, etc.)
- Supports `--infile`, `--stdin`, or `--input`

### 2. Randomness Generation
```python
salt  = os.urandom(16)   # 128 bits of cryptographically secure randomness
nonce = os.urandom(12)   # Standard GCM nonce size
```
These values are **different every run**, ensuring unique output even for identical input + passphrase.

### 3. Key Derivation
```python
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,           # 256-bit key
    salt=salt,
    iterations=480000    # Very high - resistant to brute-force/dictionary attacks
)
key = kdf.derive(passphrase.encode())
```
- Turns a human passphrase into a strong 256-bit AES key
- Salt prevents precomputation (rainbow tables)

### 4. Authenticated Encryption (AES-256-GCM)
```python
aesgcm = AESGCM(key)
ct_with_tag = aesgcm.encrypt(nonce, data, None)
```
- **Confidentiality**: AES-256 encryption
- **Integrity & Authenticity**: 16-byte GCM tag (poly1305-based)
- Any modification to ciphertext or tag will be detected on decrypt

### 5. Data Structure
Final byte sequence before conversion:
```
[salt:16][nonce:12][ciphertext:variable][tag:16]
```
Total length = 28 fixed bytes + length of original data

### 6. Hex Conversion
```python
hex_str = binascii.hexlify(full_data).decode('ascii').lower()
```
Each byte → two lowercase hex characters (e.g., byte 0xA3 → "a3")

### 7. Polyalphabetic Diffusion Layer (The "Vigenère Shift")
This is the key innovation that eliminates visual patterns.

```python
shift_source = salt + nonce                              # 28 high-entropy bytes
shifts = [shift_source[i % 28] % 16 for i in range(16)]  # 16 shift values (0–15)
```

- We **do not shift** the first 56 hex characters (salt + nonce = 28 bytes × 2)
- Starting at position 56, we apply:
  ```python
  new_val = (original_nibble + shifts[i % 16]) % 16
  ```
- This is a classic **Vigenère cipher** applied at the nibble level
- Repeating 16-value key derived from high-entropy source
- Result: even identical ciphertexts produce completely different visual output

### 8. Steganographic Mapping
```python
art = ''.join(PALETTE[c] for c in shifted_hex_str)
```
Each hex digit (0–f) maps to one of 16 carefully chosen Unicode box-drawing characters:
- High visual density
- Natural connectivity (lines appear to join)
- Mimics authentic 1990s DOS/BBS ANSI art style

### 9. Formatting
- Fixed 80 characters per line
- Decorative header with version
- Footer of solid horizontal lines (`─`)
- Entire output is valid UTF-8 text

### Decryption: The Reverse Process
1. Parse and extract art lines (skip header/footer)
2. Convert symbols back to shifted hex
3. Recover salt (first 16 bytes) and nonce (next 12)
4. Reconstruct **exact same shift sequence**
5. Reverse the nibble shifts on ciphertext + tag portion
6. Derive key from passphrase + recovered salt
7. Decrypt with AES-256-GCM, verifying the tag
8. Return original bytes (binary mode) or decode as UTF-8 (text mode)

## Why This Design is Secure and Effective

- **Security**: AES-256-GCM is NIST-approved, widely trusted, provides confidentiality + authenticity
- **No visual fingerprint**: Random salt/nonce + diffusion layer → unique art every time
- **Plausible deniability**: Output indistinguishable from real vintage ASCII art
- **Binary safe**: No encoding assumptions - works on any file type
- **No side channels**: Nothing written to disk except final art file

## Limitations (Educational Note)

- Relies on passphrase strength
- Large files → very large art output (2× file size in characters)
- Not resistant to targeted forensic analysis if attacker knows the tool

## Summary

PyCryptoArt demonstrates a powerful fusion of:
- Modern **authenticated encryption** (AES-GCM)
- Classic **polyalphabetic cipher** concepts (for diffusion)
- **Steganography** via semantic mapping to visual symbols

The result is a tool that turns any file - text or binary - into what appears to be innocent retro computer art, while protecting it with state-of-the-art cryptography.
