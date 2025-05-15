I'll break down how the Enigma machine simulator works:
# 1. Overall Structure: #
Main Components:
  - Rotor class: Handles individual rotor mechanics
  - Plugboard class: Manages letter substitutions before and after encryption
  - Reflector class: Handles signal reflection
  - EnigmaMachine class: Coordinates all components
  - Interactive mode and Command-line interface
# 2. Detailed Operation: #
## A. Initialization: ##
When EnigmaMachine is created:
  1. Loads default rotors from rotor.json
  2. Loads plugboard configuration from plugboard.json
  3. Sets up default reflector
## B. Signal Path (when encrypting a single character): ##
  1. Character enters through plugboard
  2. Passes through rotors right-to-left
  3. Hits reflector
  4. Returns through rotors left-to-right
  5. Exits through plugboard again
# 3. Key Components in Detail: #
## A. Rotors: ##
class Rotor:
    # Each rotor has:
    - Wiring: Defines letter substitutions
    - Notch: Position that triggers next rotor rotation
    - Position: Current rotational position (0-25)
    - Ring setting: Additional offset (not fully implemented)

Main functions:
    - forward(): Processes signal right-to-left
    - backward(): Processes signal left-to-right
    - rotate(): Turns rotor one position
    
## B. Rotor Rotation Mechanism: ##
For each character:
1. Right rotor rotates every time
2. Middle rotor rotates when:
   - Right rotor reaches its notch
   - Middle rotor is at its notch (double-stepping)
3. Left rotor rotates when middle rotor reaches its notch
## C. Plugboard: ##
class Plugboard:
    # Swaps letters before and after main encryption
    - Loads configuration from JSON file
    - Can swap pairs of letters (e.g., A↔B)
    - Letters not in pairs remain unchanged
## D. Reflector: ##
class Reflector:
    # Reflects signal back through rotors
    - Has fixed wiring pattern
    - Must be symmetrical (if A→B then B→A)
    - No letter can reflect to itself
# 4. Text Processing: #
def process_text(self, text):
    For each character:
        1. Check if it's a letter (non-letters pass through unchanged)
        2. Convert to uppercase
        3. Rotate rotors
        4. Pass through plugboard
        5. Through rotors right-to-left
        6. Through reflector
        7. Through rotors left-to-right
        8. Through plugboard again
        9. Return encrypted character
    5. User Interface: 
## A. Interactive Mode: ##
Options:
1. Load custom rotors
2. Load custom plugboard
3. Load custom reflector
4. Enigma current settings
5. Toggle Encode Schema (Not Enigma Machine Logic)
6. Set rotor positions (AAA to ZZZ)
7. Encode/Decode text
Q. Exit

## B. Command Line Arguments: ##
--interactive: Run in interactive mode
--text: Text to encode/decode
--rotors: Choose three rotors (1-20)
--reflector: Reflector letter (A-Z)
--positions: Set three letter rotor positions
--plugboard: Plugboard name (1-5)
--reflector: Choose reflector
--setting: Shows a header of Enigma's current settings
--encode: Convert the characters to a custom encoding scheme
--debug: Show troubleshooting steps
--test-output: Resets and runs the output through as a test
--test: Run self-test routine
# 6. Example Usage: #
## Interactive mode: ##
python PyEnigma.py --interactive

## Direct encryption: ##
python PyEnigma.py --text "HELLO" --rotors 1 2 3 --positions AAA

## Custom configuration: ##
python PyEnigma.py --text "HELLO" --rotors 1 2 3 --positions AAA --plugboard custom.json --reflector B
# 7. Important Features: #
- Historically accurate rotor mechanics
- Double-stepping mechanism
- Plugboard customization
- Multiple reflector options
- Preserves non-alphabetic characters
- Case-insensitive processing
The beauty of the Enigma machine is that it's reciprocal - encrypting an encrypted message returns the original text, as long as the machine settings are identical. This is why the same process is used for both encoding and decoding.
