# Educational Proof-of-Concept

This document describes a proof-of-concept technique for combining modern cryptography with steganography by embedding encrypted payloads within syntactically valid but innocuous-looking source code. The content is provided strictly for educational and security research purposes—to illustrate novel covert channel possibilities, encourage the development of better detection methods, and promote deeper understanding of data-hiding risks in software artifacts. The author does not condone or encourage the use of these techniques for any illegal, unethical, or malicious activity. Readers are reminded that hiding illicit material remains illegal regardless of the concealment method, and responsible disclosure practices should always be followed when exploring or publishing security-related concepts.

---

# PyCryptoArt v2.3 — Complete Overview

**Hide encrypted messages and files in beautiful retro-style ASCII art**

PyCryptoArt is a cryptographic steganography tool that conceals secret text or **any binary file** (images, PDFs, executables, etc.) inside authentic-looking geometric ASCII art created from Unicode box-drawing characters.

The resulting ".txt" file looks like pure vintage terminal art while securely protecting your data with modern authenticated encryption.

## Features

- **Strong authenticated encryption** using AES-256-GCM
- **Passphrase-based key derivation** via PBKDF2-HMAC-SHA256 (480,000 iterations)
- **Random 16-byte salt + 12-byte nonce** per encryption
- **Polyalphabetic diffusion layer** (Vigenère-style nibble shifting derived from salt+nonce) → eliminates visual patterns; identical inputs produce completely different art every time
- **Full binary support** — hide images, documents, archives, anything
- **Zero metadata leakage** in the visual output
- **High plausible deniability** — output resembles genuine retro ANSI/ASCII art
- **Safe file handling** — refuses to overwrite existing files during encryption
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
- Proper authenticated encryption — tampering is detected
- No plaintext or keys are written to disk
- Random salt + nonce prevent replay/rainbow attacks
- Diffusion layer removes visual correlations
- **Intended for educational, research, and artistic purposes only**

**Warning**: Strong encryption does not protect against weak passphrases, side-channel attacks, or compromised systems.


---
## Licensing

This suite is released under the [MIT License](LICENSE.md).<br><br><br><br><br>
---
