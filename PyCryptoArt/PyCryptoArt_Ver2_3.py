#!/usr/bin/env python3
# PyCryptoArt v2.2
# A cryptographic steganography tool that hides encrypted messages inside
# beautiful retro-style ASCII art using box-drawing characters.
#
# Features:
# - Strong passphrase-based encryption via Fernet (AES-128-GCM in CBC mode with HMAC)
# - Random 16-byte salt for key derivation (PBKDF2-HMAC-SHA256, 480k iterations)
# - Poly-alphabetic diffusion layer using Vigenère-style nibble shifts
#   derived from the salt — eliminates visual patterns even with identical inputs
# - Output appears as authentic-looking DOS/terminal geometric art
# - Fully reversible — decryption recovers the exact original message
# - Now supports BINARY files via --binary flag (images, PDFs, executables, etc.)
#
# Educational purpose: Demonstrates combining modern cryptography with
# steganographic obfuscation in a visually compelling way.

# Built-in Python Standard Library Modules
import argparse      # Parses command-line arguments and options
import getpass       # Securely prompts for passphrase without echoing input
import sys           # Access to system parameters and functions (e.g., stderr, exit)
import binascii      # Converts between binary data and hexadecimal representation
import base64        # Used internally by Fernet for key/token encoding
import os            # Operating system interface: generates secure random salt and checks file existence

# cryptography — Industry-standard, battle-tested cryptographic primitives
# Provides Fernet (symmetric authenticated encryption) and secure key derivation
# Install with: pip install cryptography
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Current version of the tool
VERSION = "2.3"

# Mapping: hex digit (0-f) → box-drawing Unicode character
# Chosen for visual density, connectivity, and retro terminal aesthetic
PALETTE = {
    '0': '╟', '1': '╚', '2': '╔', '3': '╩', '4': '╦',
    '5': '╠', '6': '═', '7': '╧', '8': '╨', '9': '╤',
    'a': '╥', 'b': '╙', 'c': '╘', 'd': '╒', 'e': '╓', 'f': '─'
}

# Reverse mapping for decryption: art symbol → original hex digit
REVERSE_PALETTE = {v: k for k, v in PALETTE.items()}


def encrypt_data(data: bytes, passphrase: str, debug: bool = False) -> str:
    if debug:
        print(f"[DEBUG] Input data length: {len(data)} bytes", file=sys.stderr)

    # Generate random 16-byte salt and 12-byte nonce (standard for GCM)
    salt = os.urandom(16)
    nonce = os.urandom(12)

    if debug:
        print(f"[DEBUG] Generated salt: {binascii.hexlify(salt).decode()}", file=sys.stderr)
        print(f"[DEBUG] Generated nonce: {binascii.hexlify(nonce).decode()}", file=sys.stderr)

    # Derive 256-bit key from passphrase
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = kdf.derive(passphrase.encode())

    # Encrypt with AES-256-GCM (authenticated encryption)
    aesgcm = AESGCM(key)
    ct_with_tag = aesgcm.encrypt(nonce, data, None)  # No associated data
    ciphertext = ct_with_tag[:-16]  # Last 16 bytes are the authentication tag
    tag = ct_with_tag[-16:]

    if debug:
        print(f"[DEBUG] Ciphertext length: {len(ciphertext)} bytes", file=sys.stderr)
        print(f"[DEBUG] Authentication tag: {binascii.hexlify(tag).decode()}", file=sys.stderr)

    # Structure: salt (16) + nonce (12) + ciphertext + tag (16)
    full_data = salt + nonce + ciphertext + tag

    # Convert to hex for shifting
    hex_str = binascii.hexlify(full_data).decode('ascii').lower()

    # Derive repeating shift sequence from salt + nonce (28 bytes → strong entropy)
    shift_source = salt + nonce
    shifts = [shift_source[i % len(shift_source)] % 16 for i in range(16)]
    if debug:
        print(f"[DEBUG] Shift sequence (16 values): {shifts}", file=sys.stderr)

    # Apply polyalphabetic shift ONLY to ciphertext + tag portion
    # First 28 bytes (salt + nonce) = 56 hex chars → left unshifted
    shift_start_hex_index = 56  # 28 bytes * 2
    shifted_hex_list = []
    for i, c in enumerate(hex_str):
        if i < shift_start_hex_index:
            # Preserve salt + nonce exactly
            shifted_hex_list.append(c)
        else:
            val = int(c, 16)
            shift_idx = (i - shift_start_hex_index) % 16
            new_val = (val + shifts[shift_idx]) % 16
            shifted_hex_list.append(f"{new_val:x}")

    shifted_hex_str = ''.join(shifted_hex_list)

    # Map to box-drawing art
    art = ''.join(PALETTE[c] for c in shifted_hex_str)
    if debug:
        print(f"[DEBUG] Final art length: {len(art)} characters", file=sys.stderr)
        lines_count = len([art[i:i+80] for i in range(0, len(art), 80)])
        print(f"[DEBUG] Number of 80-char lines: {lines_count}", file=sys.stderr)

    # Format output
    lines = [art[i:i+80] for i in range(0, len(art), 80)]
    title = "PyCryptoArt " + VERSION
    header = ("-" * (78 - len(title))) + title + "--\n\n"
    footer = "\n\n" + ("-" * 80) + "\n"

    return header + '\n'.join(lines) + footer


def decrypt_art(ascii_art: str, passphrase: str, debug: bool = False) -> bytes:
    if debug:
        print(f"[DEBUG] Input art total lines: {len(ascii_art.strip().splitlines())}", file=sys.stderr)

    # Parse input and extract only the lines containing encrypted art
    lines = ascii_art.strip().splitlines()
    art_lines = []
    started = False

    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            continue  # Skip blank lines

        # Detect footer: full line of '─' characters
        if started and all(c == '─' for c in stripped):
            if debug:
                print("[DEBUG] Detected footer — stopping parse", file=sys.stderr)
            break

        # A valid art line contains only symbols from our palette
        if all(c in REVERSE_PALETTE for c in stripped):
            started = True
            art_lines.append(stripped)
        elif started:
            # Unexpected content after art began → stop parsing
            break

    if not art_lines:
        raise ValueError("No valid encrypted art data found in input")

    if debug:
        print(f"[DEBUG] Extracted {len(art_lines)} art lines", file=sys.stderr)
        print(f"[DEBUG] Total art characters: {len(''.join(art_lines))}", file=sys.stderr)

    # Reconstruct continuous string of art symbols
    art = ''.join(art_lines)

    # Convert art symbols back to shifted hex digits
    shifted_hex_str = ''.join(REVERSE_PALETTE[c] for c in art)

    # Convert shifted hex back to bytes
    shifted_bytes = binascii.unhexlify(shifted_hex_str)

    # Extract the original unshifted salt (first 16 bytes) and nonce (next 12 bytes)
    salt = shifted_bytes[:16]
    nonce = shifted_bytes[16:28]

    if debug:
        print(f"[DEBUG] Recovered salt: {binascii.hexlify(salt).decode()}", file=sys.stderr)
        print(f"[DEBUG] Recovered nonce: {binascii.hexlify(nonce).decode()}", file=sys.stderr)

    # Re-derive the exact same shift sequence used during encryption
    shift_source = salt + nonce
    shifts = [shift_source[i % len(shift_source)] % 16 for i in range(16)]
    if debug:
        print(f"[DEBUG] Reconstructed shift sequence: {shifts}", file=sys.stderr)

    # Reverse the polyalphabetic shift on the ciphertext + tag portion only
    # First 56 hex chars = salt (32) + nonce (24) → leave unshifted
    shift_start_hex_index = 56
    original_hex_list = []
    for i in range(len(shifted_hex_str)):
        c = shifted_hex_str[i]
        if i < shift_start_hex_index:
            original_hex_list.append(c)  # Salt + nonce unchanged
        else:
            val = int(c, 16)
            shift_idx = (i - shift_start_hex_index) % 16
            new_val = (val - shifts[shift_idx]) % 16  # Subtract shift, wrap around
            original_hex_list.append(f"{new_val:x}")

    original_hex_str = ''.join(original_hex_list)
    full_data = binascii.unhexlify(original_hex_str)

    # Extract ciphertext body and authentication tag
    ciphertext_body = full_data[28:-16]  # Skip salt (16) + nonce (12)
    tag = full_data[-16:]

    # Derive key using recovered salt and provided passphrase
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = kdf.derive(passphrase.encode())

    # Decrypt with AES-256-GCM
    aesgcm = AESGCM(key)
    try:
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_body + tag, None)
    except InvalidToken:
        raise ValueError("Decryption failed: wrong passphrase or corrupted data")

    if debug:
        print(f"[DEBUG] Successfully decrypted data (length: {len(plaintext_bytes)} bytes)", file=sys.stderr)

    return plaintext_bytes

def main():
    parser = argparse.ArgumentParser(description="PyCryptoArt: Hide messages in ASCII art")
    parser.add_argument("-m", "--mode", choices=["encrypt", "decrypt"], default="encrypt",
                        help="Mode: encrypt (default) or decrypt")
    parser.add_argument("-i", "--input", type=str, help="Input text message (encrypt text mode only)")
    parser.add_argument("--stdin", action="store_true", help="Read input from stdin (text or binary depending on --binary)")
    parser.add_argument("--infile", type=str, help="Input file (text or binary)")
    parser.add_argument("--outfile", type=str, help="Output file (art in encrypt; recovered data in decrypt)")
    parser.add_argument("--binary", action="store_true", help="Treat input/output as raw binary data (no UTF-8 encoding/decoding)")
    parser.add_argument("-k", "--key", type=str, help="Passphrase (if omitted, prompted securely)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-v", "--version", action="version", version=f"PyCryptoArt {VERSION}")

    args = parser.parse_args()

    if args.debug:
        print(f"[DEBUG] Starting PyCryptoArt v{VERSION} in {args.mode} mode", file=sys.stderr)

    passphrase = args.key or getpass.getpass("Enter passphrase: ")
    if not passphrase:
        print("Error: passphrase cannot be empty", file=sys.stderr)
        sys.exit(1)

    if args.mode == "encrypt":
        # Determine input source and read data
        if args.infile:
            mode = 'rb' if args.binary else 'r'
            encoding = None if args.binary else 'utf-8'
            with open(args.infile, mode, encoding=encoding) as f:
                data = f.read() if args.binary else f.read()
        elif args.stdin:
            if args.binary:
                data = sys.stdin.buffer.read()
            else:
                data = sys.stdin.read().strip()
        elif args.input:
            if args.binary:
                print("Error: --input cannot be used with --binary", file=sys.stderr)
                sys.exit(1)
            data = args.input
        else:
            print("Error: Must provide input via --input, --stdin, or --infile", file=sys.stderr)
            sys.exit(1)

        # Convert text to bytes if not binary
        input_bytes = data if args.binary else data.encode('utf-8')

        result_art = encrypt_data(input_bytes, passphrase, debug=args.debug)

        # Output handling
        if args.outfile:
            if os.path.exists(args.outfile):
                print(f"Error: File '{args.outfile}' already exists. Refusing to overwrite.", file=sys.stderr)
                sys.exit(1)
            with open(args.outfile, 'w', encoding='utf-8') as f:
                f.write(result_art)
            if args.debug:
                print(f"[DEBUG] Encrypted art saved to '{args.outfile}'", file=sys.stderr)
        else:
            print(result_art)

    else:  # decrypt mode
        # Read art input
        if args.infile:
            with open(args.infile, 'r', encoding='utf-8') as f:
                art_data = f.read()
        elif args.stdin:
            art_data = sys.stdin.read()
        else:
            print("Error: Must provide art input via --infile or --stdin in decrypt mode", file=sys.stderr)
            sys.exit(1)

        recovered_bytes = decrypt_art(art_data, passphrase, debug=args.debug)

        # Output handling
        if args.outfile:
            mode = 'wb' if args.binary else 'w'
            encoding = None if args.binary else 'utf-8'
            with open(args.outfile, mode, encoding=encoding) as f:
                f.write(recovered_bytes) if args.binary else f.write(recovered_bytes.decode('utf-8'))
            if args.debug:
                print(f"[DEBUG] Decrypted data saved to '{args.outfile}'", file=sys.stderr)
        else:
            if args.binary:
                sys.stdout.buffer.write(recovered_bytes)
            else:
                print(recovered_bytes.decode('utf-8'))


if __name__ == "__main__":
    main()