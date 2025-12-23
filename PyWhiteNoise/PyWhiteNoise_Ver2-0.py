#!/usr/bin/env python3

# Python Standard Library
import argparse      # Command-line argument parsing
import getpass       # Secure password input (no echo)
import wave          # Read/write WAV audio files
import struct        # Pack/unpack binary data
import secrets       # Cryptographically secure random values
import sys           # System-specific parameters and functions
import hashlib       # Secure hashing algorithms (SHA, etc.)
import random        # Pseudo-random number generation
import math          # Mathematical functions and constants

# Third-Party Libraries
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt  # Password-based key derivation
from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # Authenticated encryption (AES-GCM)

VERSION = "2.0"
SAMPLE_RATE = 44100
SAMPLE_WIDTH = 2
CHANNELS = 1
HEADER_BITS = 32 + 128  # payload length (32 bits) + salt (128 bits)
LSB_MASK = 0xFFFE
MAX_PAYLOAD_BITS = 500_000  # Reasonable upper limit

# ------------------ Crypto ------------------
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    return kdf.derive(password.encode())

def encrypt_message(message: bytes, password: str):
    salt = secrets.token_bytes(16)
    key = derive_key(password, salt)
    aes = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ciphertext = aes.encrypt(nonce, message, None)
    return salt, nonce + ciphertext

def decrypt_message(payload: bytes, password: str, salt: bytes):
    key = derive_key(password, salt)
    aes = AESGCM(key)
    nonce = payload[:12]
    ciphertext = payload[12:]
    return aes.decrypt(nonce, ciphertext, None)

def prng_from_password(password: str, context: bytes = b""):
    seed = hashlib.sha256(password.encode() + context).digest()
    return random.Random(int.from_bytes(seed, "big"))

def prng_indices(rng, total_samples, needed) -> list[int]:
    if needed > total_samples:
        raise ValueError("Not enough samples")
    indices = list(range(total_samples))
    rng.shuffle(indices)
    return indices[:needed]

# ------------------ Audio ------------------
def generate_white_noise(num_samples: int):
    return [secrets.randbelow(65536) for _ in range(num_samples)]

def generate_pink_noise(num_samples: int):
    """Simple pink noise approximation using cumulative sum."""
    white = [secrets.randbelow(65536) - 32768 for _ in range(num_samples)]
    pink = [0] * num_samples
    pink[0] = white[0]
    for i in range(1, num_samples):
        pink[i] = pink[i-1] + white[i] / math.sqrt(i)
    # Normalize to 0-65535
    min_val = min(pink)
    max_val = max(pink)
    if max_val == min_val:
        return [32768] * num_samples
    scale = 65535 / (max_val - min_val)
    return [int((v - min_val) * scale) for v in pink]

def write_wav(filename, samples):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        data = b''.join(struct.pack('<h', s - 32768) for s in samples)
        wf.writeframes(data)

def read_wav(filename):
    with wave.open(filename, 'rb') as wf:
        if wf.getnframes() < HEADER_BITS:
            raise ValueError("WAV too short for header")
        frames = wf.readframes(wf.getnframes())
        signed = struct.unpack('<' + 'h' * wf.getnframes(), frames)
        samples = [s + 32768 for s in signed]
        return samples

# ------------------ Bit helpers ------------------
def bits_from_bytes(data: bytes):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1

def bytes_from_bits(bits):
    out = bytearray()
    byte = 0
    count = 0
    for bit in bits:
        byte = (byte << 1) | bit
        count += 1
        if count == 8:
            out.append(byte)
            byte = 0
            count = 0
    if count > 0:
        byte <<= (8 - count)
        out.append(byte)
    return bytes(out)

# Scattered embedding/extraction (used in stealth mode)
def embed_bits_scattered(samples, bits, password, context=b"payload"):
    rng = prng_from_password(password, context)
    indices = prng_indices(rng, len(samples), len(bits))
    for bit, idx in zip(bits, indices):
        samples[idx] = (samples[idx] & LSB_MASK) | bit

def extract_bits_scattered(samples, count, password, context=b"payload"):
    rng = prng_from_password(password, context)
    indices = prng_indices(rng, len(samples), count)
    return [samples[idx] & 1 for idx in indices]

# Sequential embedding/extraction (kept for non-stealth mode and legacy analysis)
def embed_bits_sequential(samples, bits, start_idx=0):
    for i, bit in enumerate(bits):
        idx = start_idx + i
        if idx >= len(samples):
            raise ValueError("Not enough samples")
        samples[idx] = (samples[idx] & LSB_MASK) | bit

def extract_bits_sequential(samples, count, start_idx=0):
    return [samples[start_idx + i] & 1 for i in range(min(count, len(samples) - start_idx))]

# Header encryption
def encrypt_header(header_bytes: bytes, password: str) -> bytes:
    key = hashlib.sha256(password.encode() + b"header_key").digest()[:len(header_bytes)]
    repeated_key = (key * (len(header_bytes) // len(key) + 1))[:len(header_bytes)]
    return bytes(b ^ k for b, k in zip(header_bytes, repeated_key))

def decrypt_header(encrypted_header: bytes, password: str) -> bytes:
    return encrypt_header(encrypted_header, password)  # XOR is its own inverse

# Post-embedding LSB randomization
def randomize_unused_lsbs(samples, password, used_indices_header, used_indices_payload):
    used = set(used_indices_header + used_indices_payload)
    rng = prng_from_password(password, b"lsb_noise")
    for i in range(len(samples)):
        if i not in used:
            samples[i] = (samples[i] & LSB_MASK) | rng.randint(0, 1)

# ------------------ Core operations ------------------
def encode_data(data: bytes, wavfile: str, stealth=False, noise_type="white", input_wav=None):
    password = getpass.getpass("Password: ")
    salt, encrypted = encrypt_message(data, password)
    payload_bits = list(bits_from_bytes(encrypted))
    length_bytes = len(payload_bits).to_bytes(4, "big")
    header_bytes = length_bytes + salt
    encrypted_header_bytes = encrypt_header(header_bytes, password)
    header_bits = list(bits_from_bytes(encrypted_header_bytes))

    total_bits_needed = HEADER_BITS + len(payload_bits)
    total_samples = max(total_bits_needed + 10000, 600000)  # Padding

    if input_wav:
        samples = read_wav(input_wav)
        if len(samples) < total_bits_needed + 2000:
            raise ValueError("Input WAV too short for payload")
    else:
        samples = generate_pink_noise(total_samples) if noise_type == "pink" else generate_white_noise(total_samples)

    used_header = []
    used_payload = []

    # Embed header
    if stealth:
        rng_header = prng_from_password(password, b"header")
        header_indices = prng_indices(rng_header, len(samples), HEADER_BITS)
        used_header = header_indices
        for bit, idx in zip(header_bits, header_indices):
            samples[idx] = (samples[idx] & LSB_MASK) | bit
    else:
        embed_bits_sequential(samples, header_bits, start_idx=0)
        used_header = list(range(HEADER_BITS))

    # Embed payload
    if stealth:
        rng_payload = prng_from_password(password, b"payload")
        payload_indices = prng_indices(rng_payload, len(samples), len(payload_bits))
        # Simple collision avoidance
        attempts = 0
        while set(payload_indices) & set(used_header) and attempts < 100:
            payload_indices = prng_indices(rng_payload, len(samples), len(payload_bits))
            attempts += 1
        used_payload = payload_indices
        for bit, idx in zip(payload_bits, payload_indices):
            samples[idx] = (samples[idx] & LSB_MASK) | bit
    else:
        embed_bits_sequential(samples, payload_bits, start_idx=HEADER_BITS)
        used_payload = list(range(HEADER_BITS, HEADER_BITS + len(payload_bits)))

    # Randomize unused LSBs
    randomize_unused_lsbs(samples, password, used_header, used_payload)

    write_wav(wavfile, samples)
    print(f"[+] Wrote {wavfile}")

def decode_data(wavfile: str, stealth=False):
    samples = read_wav(wavfile)
    password = getpass.getpass("Password: ")

    # Extract header
    if stealth:
        header_bits = extract_bits_scattered(samples, HEADER_BITS, password, context=b"header")
    else:
        header_bits = extract_bits_sequential(samples, HEADER_BITS, start_idx=0)

    encrypted_header = bytes_from_bits(header_bits)
    header_bytes = decrypt_header(encrypted_header, password)
    length = int.from_bytes(header_bytes[:4], "big")
    salt = header_bytes[4:]

    if length <= 0 or length > len(samples):
        print("[-] Invalid or implausible payload length")
        return

    # Extract payload
    if stealth:
        payload_bits = extract_bits_scattered(samples, length, password, context=b"payload")
    else:
        payload_bits = extract_bits_sequential(samples, length, start_idx=HEADER_BITS)

    payload = bytes_from_bits(payload_bits)
    try:
        message = decrypt_message(payload, password, salt)
        print("[+] Decrypted message:")
        sys.stdout.buffer.write(message)
        print()
    except Exception:
        print("[-] Decryption failed")

def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    entropy = 0
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    length = len(data)
    for count in counts:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return entropy

def analyze_wav(wavfile: str):
    try:
        samples = read_wav(wavfile)
        total_samples = len(samples)
        if total_samples < HEADER_BITS:
            print("[*] WAV file too short even for header.")
            return
    except Exception as e:
        print(f"[-] Error reading WAV: {e}")
        return

    print("[*] PyWhiteNoise Analysis")
    print(f" Total samples : {total_samples:,}")
    print(f" Theoretical max payload bits : {total_samples:,}")
    print(f" Theoretical max payload bytes : {total_samples // 8:,}")
    print()
    print(" Note: In stealth mode (-stealth):")
    print("   • Header is encrypted and scattered (unknown positions)")
    print("   • Unused LSBs are randomized")
    print("   • Can be embedded in real audio (not just generated noise)")
    print("   → Traditional sequential/header-based detection WILL fail")
    print()

    candidates = []

    # Candidate 1: Legacy sequential (non-stealth)
    header_bits_seq = extract_bits_sequential(samples, HEADER_BITS, start_idx=0)
    length_seq = int.from_bytes(bytes_from_bits(header_bits_seq[:32]), "big")
    salt_seq = bytes_from_bits(header_bits_seq[32:])
    entropy_seq = shannon_entropy(salt_seq)
    plausible_seq = (0 < length_seq <= total_samples - HEADER_BITS)
    confidence_seq = "High (legacy)" if plausible_seq and entropy_seq > 7.9 else "Medium" if plausible_seq else "Low"
    candidates.append({
        "mode": "Legacy sequential (non-stealth)",
        "length_bits": length_seq,
        "salt_entropy": entropy_seq,
        "plausible": plausible_seq,
        "confidence": confidence_seq
    })

    # Candidate 2: Guessed stealth context
    try:
        header_bits_guess = extract_bits_scattered(samples, HEADER_BITS, "dummy", context=b"header")
        encrypted_header = bytes_from_bits(header_bits_guess)
        length_guess_raw = int.from_bytes(encrypted_header[:4], "big")
        plausible_guess = (0 < length_guess_raw < total_samples)
        confidence_guess = "Very Low (guessed context, header encrypted)" if plausible_guess else "None"
        candidates.append({
            "mode": "Guessed stealth context (unlikely)",
            "length_bits": length_guess_raw,
            "salt_entropy": "N/A",
            "plausible": plausible_guess,
            "confidence": confidence_guess
        })
    except:
        pass

    # Sort and display
    def score(c):
        scores = {"High (legacy)": 5, "Medium": 3, "Low": 2, "Very Low": 1, "None": 0}
        return scores.get(c["confidence"].split()[0], 0)
    candidates.sort(key=score, reverse=True)
    best = candidates[0]

    print(" Most likely interpretation:")
    print(f" Mode : {best['mode']}")
    print(f" Confidence : {best['confidence']}")
    if best.get("salt_entropy") != "N/A":
        print(f" Salt entropy : {best['salt_entropy']:.3f} bits/byte")
    print(f" Apparent payload : {best['length_bits']//8:,} bytes")
    print()

    if "High" in best["confidence"] or "Medium" in best["confidence"]:
        print(" → Possible legacy/non-stealth embedding detected!")
        print(" → Try decoding WITHOUT -stealth flag.")
    else:
        print(" → No reliable signs of legacy embedding.")
        print(" → If stealth was used, detection without password is extremely difficult.")

    if len(candidates) > 1:
        print("\n Other candidates:")
        for c in candidates[1:]:
            print(f" • {c['mode']} | Conf: {c['confidence']}")

# ------------------ CLI ------------------
def main():
    parser = argparse.ArgumentParser(description="PyWhiteNoise.py hides encrypted data in audio (stealth edition).")
    parser.add_argument("-encode", action="store_true")
    parser.add_argument("-decode", action="store_true")
    parser.add_argument("-analyze", action="store_true")
    parser.add_argument("-version", action="store_true")
    parser.add_argument("-wav", help="Output/input WAV file")
    parser.add_argument("-infile", help="Input file (encode)")
    parser.add_argument("-stdin", action="store_true", help="Read from stdin (encode)")
    parser.add_argument("-stealth", action="store_true", help="Stealth mode: scatter header & payload, encrypt header, randomize LSBs")
    parser.add_argument("-noise-type", choices=["white", "pink"], default="white", help="Noise type for generated carrier (default: white)")
    parser.add_argument("-input-wav", help="Embed into existing WAV instead of generating noise")
    args = parser.parse_args()

    if args.version:
        print(f"PyWhiteNoise {VERSION}")
        return

    if args.encode:
        if not args.wav:
            sys.exit("[-] -wav required")
        if args.stdin:
            data = sys.stdin.buffer.read()
        elif args.infile:
            with open(args.infile, 'rb') as f:
                data = f.read()
        else:
            sys.exit("[-] Need -stdin or -infile")
        encode_data(data, args.wav, stealth=args.stealth, noise_type=args.noise_type, input_wav=args.input_wav)
    elif args.decode:
        if not args.wav:
            sys.exit("[-] -wav required")
        decode_data(args.wav, stealth=args.stealth)
    elif args.analyze:
        if not args.wav:
            sys.exit("[-] -wav required")
        analyze_wav(args.wav)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
