# PyEnigma

**PyEnigma** is a Python-based simulator of the historic Enigma machine, complete with customizable rotors, plugboard, reflector, and support for extended characters through a symbolic encoding scheme. It offers command-line, interactive, and test-driven modes for encryption and decryption.

---

## Features

- Emulates the classic Enigma machine with 3 rotors and a reflector.
- Plugboard and reflector customization via JSON configuration files.
- Extended character support (symbols, numbers, and lowercase letters) using a symbolic encoding scheme.
- Interactive mode for real-time configuration and testing.
- Command-line interface with test and debug options.
- Supports reproducible round-trip encoding/decoding verification.

---

## Requirements

- Python 3.6+
- No external dependencies required.

---

## File Structure

- `PyEnigma.py` - Main Python script (entry point).
- `rotor.json` - Rotor configurations.
- `plugboard.json` - Plugboard mappings.
- `reflector.json` - Reflector wiring.

---

## Usage

You can run PyEnigma in multiple modes:

### 1. **Interactive Mode**

```bash
python3 PyEnigma.py --interactive
````

Interactively load rotors, plugboards, set positions, encode/decode text, and more.

---

### 2. **Command-line Mode**

#### Encode/Decode Text

```bash
> python3 PyEnigma.py --text "HELLO WORLD" --positions AAA --setting

---------------------------------------------------------------------------
 [ACTIVE ROTORS]
 + Rotor 1: Wiring: EKMFLGDQVZNTOWYHXUSPAIBRCJ  Notch: Q  Position: A (0)
 + Rotor 2: Wiring: AJDKSIRUXBLHWTMCQGZNPYFVOE  Notch: E  Position: A (0)
 + Rotor 3: Wiring: BDFHJLCPRTXVZNYEIWGAKMUSQO  Notch: V  Position: A (0)

 [ACTIVE PLUGBOARD CONNECTIONS]
 + Plugboard Name: 1
 + Plugboard is in straight-through mode (null plugboard, no swaps)

 [ACTIVE REFLECTOR]
 + Reflector Name: A  Wiring: YRUHQSLDPXNGOKMIEBFZCWVJAT
---------------------------------------------------------------------------


ILBDA AMTAZ

```

#### With Symbolic Encoding (for non-A–Z characters)

```bash
> python3 PyEnigma.py --text "Hello, World!" --positions AAA --encode --setting

---------------------------------------------------------------------------
 [ACTIVE ROTORS]
 + Rotor 1: Wiring: EKMFLGDQVZNTOWYHXUSPAIBRCJ  Notch: Q  Position: A (0)
 + Rotor 2: Wiring: AJDKSIRUXBLHWTMCQGZNPYFVOE  Notch: E  Position: A (0)
 + Rotor 3: Wiring: BDFHJLCPRTXVZNYEIWGAKMUSQO  Notch: V  Position: A (0)

 [ACTIVE PLUGBOARD CONNECTIONS]
 + Plugboard Name: 1
 + Plugboard is in straight-through mode (null plugboard, no swaps)

 [ACTIVE REFLECTOR]
 + Reflector Name: A  Wiring: YRUHQSLDPXNGOKMIEBFZCWVJAT
---------------------------------------------------------------------------


ITFWYPUKPPYDPGYZONAKJAHEJJNZGHEKDXT

```

#### Verify round-trip (encode → reset → decode)

```bash
> python3 PyEnigma.py --text "Hello, World!" --positions AAA --encode --setting --test-output

---------------------------------------------------------------------------
 [ACTIVE ROTORS]
 + Rotor 1: Wiring: EKMFLGDQVZNTOWYHXUSPAIBRCJ  Notch: Q  Position: A (0)
 + Rotor 2: Wiring: AJDKSIRUXBLHWTMCQGZNPYFVOE  Notch: E  Position: A (0)
 + Rotor 3: Wiring: BDFHJLCPRTXVZNYEIWGAKMUSQO  Notch: V  Position: A (0)

 [ACTIVE PLUGBOARD CONNECTIONS]
 + Plugboard Name: 1
 + Plugboard is in straight-through mode (null plugboard, no swaps)

 [ACTIVE REFLECTOR]
 + Reflector Name: A  Wiring: YRUHQSLDPXNGOKMIEBFZCWVJAT
---------------------------------------------------------------------------



 Encoding the input text, then resetting the machine to verify correct decryption of the output:
 >   Input Text: Hello, World!
 > Encoded text: ITFWYPUKPPYDPGYZONAKJAHEJJNZGHEKDXT

---------------------------------------------------------------------------
 [ACTIVE ROTORS]
 + Rotor 1: Wiring: EKMFLGDQVZNTOWYHXUSPAIBRCJ  Notch: Q  Position: A (0)
 + Rotor 2: Wiring: AJDKSIRUXBLHWTMCQGZNPYFVOE  Notch: E  Position: A (0)
 + Rotor 3: Wiring: BDFHJLCPRTXVZNYEIWGAKMUSQO  Notch: V  Position: A (0)

 [ACTIVE PLUGBOARD CONNECTIONS]
 + Plugboard Name: 1
 + Plugboard is in straight-through mode (null plugboard, no swaps)

 [ACTIVE REFLECTOR]
 + Reflector Name: A  Wiring: YRUHQSLDPXNGOKMIEBFZCWVJAT
---------------------------------------------------------------------------


 > Decoded text: Hello, World!

```

---

### 3. **Test Mode**

Run a basic built-in test:

```bash
> python3 PyEnigma.py --test

---------------------------------------------------------------------------
 [ACTIVE ROTORS]
 + Rotor 1: Wiring: EKMFLGDQVZNTOWYHXUSPAIBRCJ  Notch: Q  Position: A (0)
 + Rotor 2: Wiring: AJDKSIRUXBLHWTMCQGZNPYFVOE  Notch: E  Position: A (0)
 + Rotor 3: Wiring: BDFHJLCPRTXVZNYEIWGAKMUSQO  Notch: V  Position: A (0)

 [ACTIVE PLUGBOARD CONNECTIONS]
 + Plugboard Name: 1
 + Plugboard is in straight-through mode (null plugboard, no swaps)

 [ACTIVE REFLECTOR]
 + Reflector Name: A  Wiring: YRUHQSLDPXNGOKMIEBFZCWVJAT
---------------------------------------------------------------------------


 Running test_enigma()
 +       Original: HELLO WORLD
 +        Encoded: ILBDA AMTAZ
 +        Decoded: HELLO WORLD

 Test passed: round-trip encoding/decoding successful


 Running test_enigma() with Encoding Schema
 +       Original: Hello World!
 + Encoded Schema: HZUEZULZULZUOZSPWZUOZURZULZUDZEX
 + Encoded Enigma: ITFWYPUKPPYDPGEBHEBJJAKEJYNZNHUI
 + Decoded Enigma: HZUEZULZULZUOZSPWZUOZURZULZUDZEX
 + Decoded Schema: Hello World!

 Test passed: round-trip encoding/decoding successful
```

---

## Configuration Files

Customize the machine components by editing or extending the following JSON files:

### rotors.json

```json
{
    "rotors": [
      {"name": "1",  "wiring": "EKMFLGDQVZNTOWYHXUSPAIBRCJ", "notch": "Q"},
      {"name": "2",  "wiring": "AJDKSIRUXBLHWTMCQGZNPYFVOE", "notch": "E"},
      {"name": "3",  "wiring": "BDFHJLCPRTXVZNYEIWGAKMUSQO", "notch": "V"},
      {"name": "4",  "wiring": "ESOVPZJAYQUIRHXLNFTGKDCMWB", "notch": "J"},
      {"name": "5",  "wiring": "VZBRGITYUPSDNHLXAWMJQOFECK", "notch": "Z"},
```

### plugboard.json

```json
{
    "plugboards": [
        {
            "name": "1",
            "connections": {
                "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", 
                "F": "F", "G": "G", "H": "H", "I": "I", "J": "J",
                "K": "K", "L": "L", "M": "M", "N": "N", "O": "O",
                "P": "P", "Q": "Q", "R": "R", "S": "S", "T": "T",
                "U": "U", "V": "V", "W": "W", "X": "X", "Y": "Y",
                "Z": "Z"
            }
        },
        {
            "name": "2",
            "connections": {
                "A": "E", "B": "B", "C": "M", "D": "D", "E": "A", 
                "F": "F", "G": "H", "H": "G", "I": "I", "J": "J",
                "K": "N", "L": "L", "M": "C", "N": "K", "O": "O",
                "P": "P", "Q": "Q", "R": "S", "S": "R", "T": "T",
                "U": "U", "V": "W", "W": "V", "X": "X", "Y": "Z",
                "Z": "Y"
            }
        },
```

### reflector.json

```json
{
    "reflectors": [
        {"name": "A", "wiring": "YRUHQSLDPXNGOKMIEBFZCWVJAT"},
        {"name": "B", "wiring": "FVPJIAOYEDRZXWGCTKUQSBNMHL"},
        {"name": "C", "wiring": "ENKQAUYWJICOPBLMDXZVFTHRGS"},
        {"name": "D", "wiring": "RDOBJNTKVEHMLFCWZAXGYIPSUQ"},
        {"name": "E", "wiring": "MFLNTHBQKCROGSZWIDVAXYUPJE"},
```

---

## Symbolic Encoding

Characters outside the standard A–Z range (e.g., spaces, punctuation, digits, lowercase letters) are pre-encoded using 3-character tokens such as:

| Character | Encoded Token |
| --------: | ------------- |
|     Space | `ZSP`         |
|       `!` | `ZEX`         |
|       `a` | `ZUA`         |
|       `1` | `ZNB`         |

This enables full-text messages to be encrypted using Enigma logic.

---

## Example

```bash
> python3 PyEnigma.py --text "Secret123!" --positions AAA --encode --test-output

 Encoding the input text, then resetting the machine to verify correct decryption of the output:
 >   Input Text: Secret123!
 > Encoded text: JTFWYPAKPXYDLGTWOSUNBFNQVEXR
 > Decoded text: Secret123!
```

---

## Debugging

Enable verbose output for internal state tracing:

```bash
python3 PyEnigma.py --text "Test" --positions AAA --debug
```

---

## Licensing

This suite is released under the [MIT License](LICENSE.md).
