#!/usr/bin/env python3
# PyBinaryNoise
# -------------------------------------------------------------------------------------------
# A secure, lightweight file obfuscation tool using password-based encryption,
# stream splitting, custom interleaving patterns, and optional noise insertion.

# Features:
# - AES-GCM authenticated encryption
# - Scrypt key derivation
# - Configurable stream splitting and interleaving
# - Optional single-byte noise insertion
# - Binary or ASCII hex text output/input
# - Forensic analysis mode with entropy and statistics

# STANDARD LIBRARY IMPORTS (preinstalled with Python — no pip needed)
# -------------------------------------------------------------------------------------------
import argparse          # Command-line argument parsing
import getpass           # Secure password input (no echo)
import os                # Operating system interface (os.urandom for crypto-random bytes)
import itertools         # Tools for iterators (itertools.cycle for pattern repeating)
import math              # Mathematical functions (math.log2 for entropy calculation)
import collections       # High-performance container datatypes (Counter for byte frequency)
import sys               # Python runtime system access (arguments, I/O streams, exit handling, platform info)
import os                # OS-level functionality (filesystem paths, environment variables, process & platform detection)


# THIRD-PARTY IMPORTS (requires: pip install cryptography)
# -------------------------------------------------------------------------------------------
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
# Scrypt: Memory-hard key derivation function — resistant to GPU/ASIC attacks
# Part of the 'cryptography' library (widely used, well-audited)

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# AES-GCM: Authenticated encryption with associated data
# Provides confidentiality + integrity (detects tampering)
# Industry standard for symmetric encryption

# CONSTANTS
# -------------------------------------------------------------------------------------------
VERSION = "2.4"          # Tool version
DEFAULT_STREAMS = 3      # Default number of streams if not specified

# FUNCTIONS
# -------------------------------------------------------------------------------------------
def derive_key(password: str, salt: bytes) -> bytes:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Derive a 32-byte encryption key from a password using Scrypt.
    # Scrypt is deliberately slow and memory-intensive to make brute-force attacks
    # much harder (even with powerful hardware).

    # Args:
    # - password: User-provided passphrase
    # - salt: 16-byte random salt (unique per file)

    # Returns: 32-byte cryptographic key
    # ───────────────────────────────────────────────────────────────────────────────────────
    kdf = Scrypt(
        salt=salt,      # salt: 16-byte random salt (unique per file)
        length=32,      # 256-bit key
        n=2**14,        # CPU/memory cost parameter (16384) — good modern balance
        r=8,            # Block size
        p=1             # Parallelism
    )
    return kdf.derive(password.encode('utf-8'))

def get_password(prompt="Password: "):
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Securely read a password from the terminal with masked input.
    #
    # Automatically detects the operating system and selects the safest
    # supported method:
    # - Windows: uses getpass (native secure input, no echo)
    # - Linux/macOS: uses raw terminal control to display '*' for each character
    #
    # This function prevents password leakage via terminal echo and ensures
    # compatibility across major platforms.
    #
    # Args:
    # - prompt: Text displayed to the user before password entry
    #
    # Returns:
    # - password: User-entered password as a string
    # ───────────────────────────────────────────────────────────────────────────────────────

    # Windows platform (os.name == "nt")
    if os.name == "nt":
        import getpass                       # Secure password input (no echo)
        return getpass.getpass(prompt)

    # Unix-like platforms (Linux / macOS)
    else:
        import termios                       # POSIX terminal control
        import tty                           # Terminal mode management

        sys.stdout.write(prompt)             # Display prompt without newline
        sys.stdout.flush()                   # Ensure prompt is shown immediately

        password = ""
        fd = sys.stdin.fileno()              # File descriptor for stdin
        old_settings = termios.tcgetattr(fd) # Save current terminal settings

        try:
            tty.setraw(fd)                   # Raw mode: read input one character at a time

            while True:
                ch = sys.stdin.read(1)

                # Enter / Return pressed → finish input
                if ch in ('\r', '\n'):
                    sys.stdout.write('\n')
                    break

                # Backspace / Delete → remove last character
                elif ch in ('\x08', '\x7f'):
                    if password:
                        password = password[:-1]
                        sys.stdout.write('\b \b')  # Erase last '*'
                        sys.stdout.flush()

                # Ctrl+C → allow user to abort safely
                elif ch == '\x03':
                    raise KeyboardInterrupt

                # Any other printable character → mask input
                else:
                    password += ch
                    sys.stdout.write('*')
                    sys.stdout.flush()

        finally:
            # Always restore original terminal state to avoid terminal corruption
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        print("")
        return password

def encrypt_data(data: bytes, password: str) -> bytes:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Encrypt data using AES-256-GCM with password-derived key.
    # Output format: salt (16) + nonce (12) + ciphertext + auth tag (16)
    # Total overhead: 44 bytes

    # Args:
    # - data: Plaintext bytes to encrypt
    # - password: User passphrase

    # Returns: Encrypted payload (can be safely stored/transmitted)
    # ───────────────────────────────────────────────────────────────────────────────────────
    salt = os.urandom(16)                    # Random salt for key derivation
    key = derive_key(password, salt)
    aes = AESGCM(key)
    nonce = os.urandom(12)                   # Unique nonce (never reuse!)
    ciphertext = aes.encrypt(nonce, data, associated_data=None)
    return salt + nonce + ciphertext         # Self-contained encrypted blob

def decrypt_data(payload: bytes, password: str, debug: bool = False) -> bytes:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Decrypt an AES-GCM encrypted payload.

    # Automatically verifies authenticity — raises exception on tampering or wrong key.

    # Args:
    # - payload: Encrypted data from encrypt_data()
    # - password: Correct passphrase
    # - debug: Print salt/nonce/ciphertext info

    # Returns: Original plaintext bytes
    # ───────────────────────────────────────────────────────────────────────────────────────
    if len(payload) < 28:
        raise ValueError("Payload too short — corrupted or invalid")

    salt = payload[:16]
    nonce = payload[16:28]
    ciphertext = payload[28:]

    key = derive_key(password, salt)
    aes = AESGCM(key)

    if debug:
        print(f"[DEBUG] Salt: {salt.hex()}")
        print(f"[DEBUG] Nonce: {nonce.hex()}")
        print(f"[DEBUG] Ciphertext len: {len(ciphertext)}")

    return aes.decrypt(nonce, ciphertext, associated_data=None)

def split_payload(payload: bytes, num_streams: int, debug: bool = False) -> list[bytes]:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Split encrypted payload into N nearly equal shares.

    # No padding added — shorter streams are just shorter.
    # This preserves exact byte count for perfect reconstruction.
    # ───────────────────────────────────────────────────────────────────────────────────────
    base_size = len(payload) // num_streams
    remainder = len(payload) % num_streams

    shares = []
    pos = 0
    for i in range(num_streams):
        size = base_size + (1 if i < remainder else 0)
        share = payload[pos:pos + size]
        shares.append(share)
        if debug:
            print(f"[DEBUG] Stream {i+1}: {len(share)} bytes (bytes {pos}:{pos+size})")
        pos += size

    if debug:
        total = sum(len(s) for s in shares)
        print(f"[DEBUG] Split complete: total {total} bytes (original {len(payload)})")

    return shares

def reassemble_payload(shares: list[bytes], original_len: int) -> bytes:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Recombine stream shares and truncate to original encrypted payload length.
    # ───────────────────────────────────────────────────────────────────────────────────────
    combined = b''.join(shares)
    return combined[:original_len]

def apply_pattern_and_noise(shares: list[bytes], pattern: str, noise_stream: int | None, debug: bool = False) -> bytes:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Interleave stream shares using a repeating numeric pattern.
    # Optionally insert one cryptographically random byte after every byte
    # from a chosen stream (noise_stream).

    # Example pattern "123321" → byte order: S1, S2, S3, S3, S2, S1, ...
    # ───────────────────────────────────────────────────────────────────────────────────────
    pattern_list = [int(c) - 1 for c in pattern if c.isdigit()]  # Convert to 0-based indices
    if not pattern_list:
        raise ValueError("Invalid pattern — must contain digits")

    if debug:
        print(f"[DEBUG] Using pattern: {pattern} → {pattern_list} (0-based)")

    cycle = itertools.cycle(pattern_list)
    output = bytearray()
    pointers = [0] * len(shares)

    bytes_emitted = 0
    noise_added = 0

    while True:
        stream_idx = next(cycle)

        # Skip if this stream is fully consumed
        if pointers[stream_idx] >= len(shares[stream_idx]):
            continue

        byte = shares[stream_idx][pointers[stream_idx]]
        output.append(byte)
        pointers[stream_idx] += 1
        bytes_emitted += 1

        # Insert noise byte if configured
        if noise_stream is not None and stream_idx + 1 == noise_stream:
            noise_byte = os.urandom(1)[0]
            output.append(noise_byte)
            noise_added += 1
            if debug and noise_added <= 5:
                print(f"[DEBUG] Added noise byte after stream {noise_stream}: 0x{noise_byte:02x}")

        # Exit when all real data has been written
        if all(pointers[i] >= len(shares[i]) for i in range(len(shares))):
            break

    if debug:
        print(f"[DEBUG] Interleave complete:")
        print(f"[DEBUG] - Real bytes emitted: {bytes_emitted}")
        print(f"[DEBUG] - Noise bytes added:  {noise_added}")
        print(f"[DEBUG] - Final output size:  {len(output)} bytes")

    return bytes(output)

def deinterleave_with_noise_removal(interleaved: bytes, pattern: str, num_streams: int, noise_stream: int | None, debug: bool = False) -> list[bytes]:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Reverse the interleaving process.
    # Automatically skips noise bytes if noise_stream is specified.
    # ───────────────────────────────────────────────────────────────────────────────────────
    pattern_list = [int(c) - 1 for c in pattern if c.isdigit()]
    cycle = itertools.cycle(pattern_list)
    shares = [bytearray() for _ in range(num_streams)]
    i = 0
    noise_skipped = 0

    if debug:
        print(f"[DEBUG] Deinterleaving {len(interleaved)} bytes with pattern {pattern}")

    while i < len(interleaved):
        current_stream = next(cycle)
        if i >= len(interleaved):
            break

        byte = interleaved[i]
        i += 1
        shares[current_stream].append(byte)

        # Skip the following byte if it was noise
        if noise_stream is not None and current_stream + 1 == noise_stream:
            if i < len(interleaved):
                skipped = interleaved[i]
                i += 1
                noise_skipped += 1
                if debug and noise_skipped <= 5:
                    print(f"[DEBUG] Skipped noise byte: 0x{skipped:02x}")

    if debug:
        for idx, s in enumerate(shares):
            print(f"[DEBUG] Extracted stream {idx+1}: {len(s)} bytes")
        print(f"[DEBUG] Total noise bytes skipped: {noise_skipped}")
        print(f"[DEBUG] Total bytes processed: {i}")

    return [bytes(s) for s in shares]

def bytes_to_hex_text(data: bytes, width: int = 80) -> str:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Convert binary data to uppercase hex string with line wrapping.
    # ───────────────────────────────────────────────────────────────────────────────────────
    hexstr = data.hex().upper()
    return '\n'.join(hexstr[i:i+width] for i in range(0, len(hexstr), width))

def hex_text_to_bytes(text: str) -> bytes:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Convert hex text (with or without spaces/newlines) back to bytes.
    # ───────────────────────────────────────────────────────────────────────────────────────
    cleaned = ''.join(text.split())  # Remove whitespace
    if len(cleaned) % 2 != 0:
        raise ValueError("Hex text has odd length — invalid")
    return bytes.fromhex(cleaned)

def calculate_entropy(data: bytes) -> float:
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Calculate Shannon entropy of byte distribution.
    # 0.0 = completely predictable, 8.0 = perfectly random.
    # ───────────────────────────────────────────────────────────────────────────────────────
    if not data:
        return 0.0
    counter = collections.Counter(data)
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in counter.values())

def analyze_file(interleaved: bytes, num_streams: int, pattern: str, noise_k: int | None, debug: bool = False):
    # ───────────────────────────────────────────────────────────────────────────────────────
    # Print a dramatic, detailed (and mostly useless) forensic analysis report.
    # ───────────────────────────────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("          PYBINARYNOISE FORENSIC ANALYSIS REPORT")
    print("="*60)
    print(f"- File size: {len(interleaved):,} bytes ({len(interleaved)/1024:.2f} KiB)")

    entropy = calculate_entropy(interleaved)
    print(f"- Byte Entropy: {entropy:.4f} bits/byte")
    print("-"*60)
    if entropy > 7.9:
        print("[####] ENTROPY LEVEL: EXTREME  — This file is basically pure chaos.")
    elif entropy > 7.5:
        print("[###_] ENTROPY LEVEL: HIGH     — Looks very random. Suspiciously random.")
    elif entropy > 6.0:
        print("[##__] ENTROPY LEVEL: MODERATE — Could be compressed or encrypted data.")
    else:
        print("[#___] ENTROPY LEVEL: LOW      — Probably plaintext or structured data.")

    counter = collections.Counter(interleaved)
    most_common = counter.most_common(5)
    print(f"\n- Top 5 most common bytes:\n    {most_common}")
    if counter[0] > len(interleaved) // 10:
        print("[WARN] Excessive null bytes detected. Possible padding or corruption?")
    if counter[0xff] > len(interleaved) // 20:
        print("[FFFF] Lots of 0xFF... are we looking at a flash dump or something?")

    print("\n- First 16 bytes (hex):", interleaved[:16].hex())
    if interleaved.startswith(b"PK\x03\x04"):
        print("[ZIP_] ZIP file magic detected! Someone hiding archives in noise?")
    elif interleaved.startswith(b"%PDF"):
        print("[PDF_] PDF header detected. Classic stego move.")
    elif interleaved.startswith(b"\x89PNG"):
        print("[PNG_] PNG image detected. Very sneaky.")
    elif interleaved.startswith(b"GIF8"):
        print("[GIF_] GIF detected. 90s called, they want their container back.")
    else:
        print("[OK__] No obvious file magic. Good obfuscation.")

    print(f"\n- Configured streams: {num_streams}")
    print(f"- Configured pattern: {pattern}")
    print(f"- Noise insertion: {'After stream ' + str(noise_k) if noise_k else 'Disabled'}")

    shares = deinterleave_with_noise_removal(interleaved, pattern, num_streams, noise_k, debug=False)
    print("\n- Deinterleaved stream lengths:")
    for i, s in enumerate(shares, 1):
        print(f"  + Stream {i}: {len(s):5d} bytes  ({len(s)/len(interleaved)*100:5.1f}%)")

    if noise_k:
        noise_bytes = len(interleaved) - sum(len(s) for s in shares)
        print(f"  + Noise  : ESTIMATED BYTES: {noise_bytes} ({noise_bytes/len(interleaved)*100:.1f}%)")

    print("\n=== USELESS BUT IMPRESSIVE STATISTICS ===")
    print(f"- Total unique bytes found: {len(counter)} of a possible 256 byte values.")
    print(f"- Byte 0x00 appears {counter[0]} times")
    print(f"- Byte 0x42 appears {counter[0x42]} times (the answer to everything?)")
    even = sum(1 for b in interleaved if b % 2 == 0)
    print(f"- Even bytes: {even} ({even/len(interleaved)*100:.1f}%) — slightly biased toward order?")

    print("\n" + "="*60)
    if entropy > 7.8 and noise_k:
        print("- VERDICT: This file is professionally deniable.")
        print("       Even a nation-state would shrug and walk away.")
    elif entropy > 7.0:
        print("- VERDICT: Strong obfuscation detected.")
        print("       Casual inspectors will give up immediately.")
    else:
        print("- VERDICT: Some structure visible.")
        print("       Advanced analysis might reveal patterns.")
    print("="*60 + "\n")


# MAIN PROGRAM
# -------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description=f"PyBinaryNoise v{VERSION} — Secure splitting + optional obfuscation"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-encode', action='store_true', help="Encode a file")
    group.add_argument('-decode', action='store_true', help="Decode a file")
    group.add_argument('-analyze', action='store_true', help="Forensic analysis mode — maximum useless detail")
    parser.add_argument('-text', action='store_true', help='Use ASCII hex text format instead of binary')
    parser.add_argument('-infile', help='Input file')
    parser.add_argument('-outfile', '-o', help='Output file (encode/decode)')
    parser.add_argument('-streams', '-s', type=int, default=DEFAULT_STREAMS, help=f'Number of streams (default: {DEFAULT_STREAMS})')
    parser.add_argument('-pattern', '-pat', help='Interleave pattern, e.g. "123321"')
    parser.add_argument('-noise', type=int, metavar='K', help='Insert random byte after every byte from stream K')
    parser.add_argument('-debug', '-d', action='store_true', help="Enable debug output")
    parser.add_argument('-version', '-v', action='version', version=f'%(prog)s {VERSION}')

    args = parser.parse_args()
    debug = args.debug

    num_streams = args.streams
    pattern = args.pattern or ''.join(str(i % num_streams + 1) for i in range(num_streams * 3))
    noise_k = args.noise

    # ANALYZE MODE
    # ───────────────────────────────────────────────────────────────────────────────────────
    if args.analyze:
        if not args.infile:
            parser.error("Analyze mode requires -infile")
        with open(args.infile, 'rb') as f:
            data = f.read()
        analyze_file(data, num_streams, pattern, noise_k, debug)
        return

    # ENCODE MODE
    # ───────────────────────────────────────────────────────────────────────────────────────
    if args.encode:
        if not args.infile or not args.outfile:
            parser.error("Encode requires -infile and -outfile")

        with open(args.infile, 'rb') as f:
            data = f.read()

        password = get_password("Enter your password: ")
        encrypted = encrypt_data(data, password)

        if debug:
            print(f"[DEBUG] Original data len: {len(data)}")
            print(f"[DEBUG] Encrypted payload len: {len(encrypted)}")

        shares = split_payload(encrypted, num_streams, debug=debug)
        interleaved = apply_pattern_and_noise(shares, pattern, noise_k, debug=debug)

        if args.text:
            out_name = args.outfile if args.outfile.endswith('.txt') else args.outfile + '.txt'
            hex_text = bytes_to_hex_text(interleaved)
            with open(out_name, 'w') as f:
                f.write(hex_text)
        else:
            out_name = args.outfile if args.outfile.endswith('.bin') else args.outfile + '.bin'
            with open(out_name, 'wb') as f:
                f.write(interleaved)

        overhead_pct = ((len(interleaved) - len(encrypted)) / len(encrypted) * 100) if noise_k else 0
        size_info = f" (+{overhead_pct:.1f}% overhead)" if noise_k else ""
        print(f"Encoded → {out_name} ({len(interleaved)} bytes{size_info})")

    # DECODE MODE
    # ───────────────────────────────────────────────────────────────────────────────────────
    elif args.decode:
        if not args.infile:
            parser.error("Decode requires -infile")

        if args.text:
            with open(args.infile, 'r') as f:
                text = f.read()
            interleaved = hex_text_to_bytes(text)
        else:
            with open(args.infile, 'rb') as f:
                interleaved = f.read()

        password = get_password("Enter your password: ")

        shares = deinterleave_with_noise_removal(interleaved, pattern, num_streams, noise_k, debug=debug)

        if debug:
            for i, s in enumerate(shares, 1):
                print(f"[DEBUG] Extracted stream {i}: {len(s)} bytes")

        if noise_k is not None:     # Determine expected payload length
            expected_payload_len = len(interleaved) - len(shares[noise_k - 1])
        else:
            expected_payload_len = len(interleaved)

        if debug:
            print(f"[DEBUG] Expected payload length: {expected_payload_len}")

        combined = b''.join(shares)
        payload = combined[:expected_payload_len]

        try:
            decrypted = decrypt_data(payload, password, debug)

            if args.outfile:
                with open(args.outfile, 'wb') as f:
                    f.write(decrypted)
                print(f"Decoded → {args.outfile}")
            else:
                print(f"Success! Recovered {len(decrypted)} bytes.")

            if debug:
                print(f"[DEBUG] Decryption successful — original file recovered.")

        except Exception as e:
            print("[ERROR] Decryption failed — wrong password, pattern, streams, or -noise setting")
            if debug:
                print(f"[DEBUG] Exception: {e}")
                print("[DEBUG] Likely causes: wrong password, missing/incorrect -noise, wrong -pattern, or wrong -s")

if __name__ == "__main__":
    main()
