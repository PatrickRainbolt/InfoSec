import json             # Provides functionality for reading and writing JSON files
import sys              # Provides access to system-specific parameters and functions
import re               # loads Python's regular expression module for pattern matching and text searching.
import argparse         # Enables parsing command-line arguments

# DEBUG Mode Global
DEBUG = False           # Set to True to enable debug output

# Default rotor configuration (3 rotors)
DEFAULT_ROTOR_CONFIG = {"rotors": [
        {"name": "1", "wiring": "EKMFLGDQVZNTOWYHXUSPAIBRCJ", "notch": "Q"},
        {"name": "2", "wiring": "AJDKSIRUXBLHWTMCQGZNPYFVOE", "notch": "E"},
        {"name": "3", "wiring": "BDFHJLCPRTXVZNYEIWGAKMUSQO", "notch": "V"}]}

# Default reflector configuration (Reflector B)
DEFAULT_REFLECTOR_CONFIG = {"reflectors": [{"name": "A", "wiring": "YRUHQSLDPXNGOKMIEBFZCWVJAT"}]}

# Default plugboard configuration (identity mapping)
DEFAULT_PLUGBOARD_CONFIG = {"plugboards": [{"name": "1", "connections": {
    "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F", "G": "G", "H": "H", "I": "I", "J": "J",
    "K": "K", "L": "L", "M": "M", "N": "N", "O": "O", "P": "P", "Q": "Q", "R": "R", "S": "S", "T": "T",
    "U": "U", "V": "V", "W": "W", "X": "X", "Y": "Y", "Z": "Z"}}]}

# Symbol Mapping Data (Not Part of Enigma Machine Logic)
SYMBOL_MAP = {" ": "ZSP", ".": "ZPD", ",": "ZCM", "?": "ZQM", "!": "ZEX", ":": "ZCL", "#": "ZHS", "-": "ZHP",
    "_": "ZUN", "$": "ZDL", "%": "ZPC", "'": "ZSQ", '"': "ZDQ", "=": "ZEQ", "+": "ZPL", "&": "ZAN",
    "\n": "ZNL", "0": "ZNA", "1": "ZNB", "2": "ZNC", "3": "ZND", "4": "ZNE", "5": "ZNF", "6": "ZNG", 
    "7": "ZNH", "8": "ZNI", "9": "ZNJ"}

# Add lowercase letters with updated mapping: 'a' to 'z' → 'ZUA' to 'ZUZ' (Not Part of Enigma Machine Logic)
SYMBOL_MAP.update({chr(i): f"ZU{chr(i).upper()}" for i in range(ord('a'), ord('z') + 1)})

# Create reverse map (Not Part of Enigma Machine Logic)
REVERSE_SYMBOL_MAP = {v: k for k, v in SYMBOL_MAP.items()}

# Terminal Color Codes
BLUE = '\033[94m'
CYAN = "\033[96m"
YELLOW = '\033[93m'
RESET = '\033[0m'


# Represents a rotor component of the Enigma machine
class Rotor:
    def __init__(self, wiring, notch, name=""):
        self.name = name
        self.wiring = wiring
        self.notch = notch
        self.position = 0
        self.ring_setting = 0

    # Forward encryption through rotor
    def forward(self, char):
        pos = (ord(char) - ord('A') + self.position) % 26
        char = self.wiring[pos]
        return chr(((ord(char) - ord('A') - self.position) % 26) + ord('A'))

    # Backward decryption through rotor
    def backward(self, char):
        pos = (ord(char) - ord('A') + self.position) % 26
        char_pos = self.wiring.index(chr(pos + ord('A')))
        return chr(((char_pos - self.position) % 26) + ord('A'))

    # Rotate rotor and return whether it reaches notch
    def rotate(self):
        self.position = (self.position + 1) % 26
        return self.position == ord(self.notch) - ord('A')

# Represents the plugboard component for letter substitution
class Plugboard:
    def __init__(self, connections, name=""):
        for k, v in connections.items():
            if connections.get(v) != k:
                raise ValueError(f"Inconsistent plugboard mapping: {k} <-> {v} not bidirectional")
        self.connections = connections
        self.name = name

    def process(self, char):
        return self.connections.get(char, char)

    # Substitutes letter through plugboard connections
    def process(self, char):
        return self.connections.get(char, char)

# Represents the reflector component of the Enigma machine
class Reflector:
    def __init__(self, wiring, name=""):
        self.wiring = wiring
        self.name = name
        for i in range(26):
            j = ord(wiring[i]) - ord('A')
            if ord(wiring[j]) - ord('A') != i:
                raise ValueError("Invalid reflector wiring: not symmetric")

    # Reflect signal
    def process(self, signal):
        return ord(self.wiring[signal]) - ord('A')

# Represents the Enigma machine with rotors, plugboard, and reflector
class EnigmaMachine:
    def __init__(self):
        self.rotors = []
        self.plugboard = None
        self.reflector = None
        self.load_default_config()

    # Loads default or fallback configurations for components
    def load_default_config(self):
        # Load rotors
        try:
            with open('rotor.json', 'r') as f:
                rotor_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            rotor_data = DEFAULT_ROTOR_CONFIG
        default_rotors = rotor_data['rotors'][:3]
        self.rotors = [Rotor(r['wiring'], r['notch'], r['name']) for r in default_rotors]

        # Load plugboard
        try:
            with open('plugboard.json', 'r') as f:
                plugboard_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            plugboard_data = DEFAULT_PLUGBOARD_CONFIG
        default_plugboard = next(pb for pb in plugboard_data['plugboards'] if pb['name'] == '1')
        self.plugboard = Plugboard(default_plugboard['connections'], default_plugboard.get('name', ''))

        # Load reflector
        try:
            with open('reflector.json', 'r') as f:
                reflector_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            reflector_data = DEFAULT_REFLECTOR_CONFIG
        self.reflector = Reflector(reflector_data['reflectors'][0]['wiring'], reflector_data['reflectors'][0].get('name', ''))


    # Sets initial rotor positions based on characters
    def set_rotor_positions(self, positions):
        if DEBUG: print(f"DEBUG: Setting rotor positions to {positions}")
        for rotor, pos in zip(self.rotors, positions):
            rotor.position = ord(pos.upper()) - ord('A')
            if DEBUG: print(f"DEBUG: Rotor {rotor.name} set to position {pos.upper()} ({rotor.position})")


    # Loads specific rotors by index from JSON file
    def load_custom_rotors(self, rotor_indices):
        if DEBUG: print(f"DEBUG: Loading custom rotors with indices: {rotor_indices}")
        with open('rotor.json', 'r') as f:
            rotor_data = json.load(f)
            self.rotors = []
            for i in rotor_indices:
                rotor = rotor_data['rotors'][i-1]
                self.rotors.append(Rotor(rotor['wiring'], rotor['notch'], rotor['name']))
                if DEBUG: print(f"DEBUG: Loaded rotor {rotor['name']} with wiring {rotor['wiring']} and notch {rotor['notch']}")
        if DEBUG: print(f"DEBUG: Loaded {len(self.rotors)} rotors.")

    # Loads a named plugboard from JSON file
    def load_custom_plugboard(self, name):
        if DEBUG: print(f"DEBUG: Loading plugboard with name: {name}")
        try:
            with open('plugboard.json', 'r') as f:
                plugboard_data = json.load(f)
                for pb in plugboard_data['plugboards']:
                    if pb['name'] == name:
                        self.plugboard = Plugboard(pb['connections'], pb.get('name', ''))
                        if DEBUG: print(f"DEBUG: Loaded plugboard {name} with connections: {pb['connections']}")
                        return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if DEBUG: print(f"DEBUG: Error loading plugboard: {e}")
            return False
        return False

    # Sets the reflector using a wiring string
    def set_reflector(self, wiring):
        if DEBUG: print(f"DEBUG: Setting reflector with wiring: {wiring}")
        self.reflector = Reflector(wiring)
        if DEBUG: print(f"DEBUG: Reflector set with wiring: {self.reflector.wiring}")

    # Displays all the current settings of Enigma Cipher
    def show_current_setting(self):
        print(f"\n" + "-" * 75)
        
        print(" [ACTIVE ROTORS]")
        for rotor in self.rotors:
            print(f" + Rotor {rotor.name}: Wiring: {rotor.wiring}  Notch: {rotor.notch}  Position: {chr(rotor.position + ord('A'))} ({rotor.position})")

        print("\n [ACTIVE PLUGBOARD CONNECTIONS]")
        print(f" + Plugboard Name: {self.plugboard.name if self.plugboard.name else 'Unknown'}")
        swapped = [(k, v) for k, v in self.plugboard.connections.items() if k != v]
        if not swapped:
            print(" + Plugboard is in straight-through mode (null plugboard, no swaps)")
        else:
            shown = set()
            for k, v in swapped:
                if (v, k) not in shown:
                    print(f" + {k} <-> {v}")
                    shown.add((k, v))

        print("\n [ACTIVE REFLECTOR]")
        print(f" + Reflector Name: {self.reflector.name if self.reflector.name else 'Unknown'}  Wiring: {self.reflector.wiring}")
        print(f"-" * 75 + "\n\n")


    # Processes entire input text through the Enigma machine
    def process_text(self, text):
        if DEBUG: print("[DEBUG] Starting text processing:", text)
        result = ''.join(self.process_char(c) for c in text)
        if DEBUG: print("[DEBUG] Final result:", result)
        return result

    # Processes one character through the Enigma machine
    def process_char(self, char):
        if not char.isalpha():
            return char

        char = char.upper()
        if DEBUG: print(f"\n[DEBUG] Processing char: {char}")

        # Step rotors before processing
        if len(self.rotors) >= 3:
            if self.rotors[1].position == ord(self.rotors[1].notch) - ord('A'):
                if DEBUG: print("[DEBUG] Middle rotor at notch, rotating middle and left rotor")
                self.rotors[1].rotate()
                self.rotors[0].rotate()
            elif self.rotors[2].position == ord(self.rotors[2].notch) - ord('A'):
                if DEBUG: print("[DEBUG] Right rotor at notch, rotating middle rotor")
                self.rotors[1].rotate()
            if DEBUG: print("[DEBUG] Rotating right rotor")
            self.rotors[2].rotate()

        if DEBUG: print("[DEBUG] Rotor positions:", [r.position for r in self.rotors])

        # Plugboard substitution
        pre_plug = char
        char = self.plugboard.process(char)
        if DEBUG: print(f"[DEBUG] Plugboard in: {pre_plug} -> out: {char}")

        # Convert to signal (0–25)
        signal = ord(char) - ord('A')

        # Right to left through rotors
        for i, rotor in enumerate(reversed(self.rotors), 1):
            offset_signal = (signal + rotor.position) % 26
            rotor_output = ord(rotor.wiring[offset_signal]) - ord('A')
            signal = (rotor_output - rotor.position) % 26
            if DEBUG: print(f"[DEBUG] Rotor {len(self.rotors)-i+1} forward: signal={offset_signal} -> {rotor_output} -> {signal}")

        # Reflector
        reflect_in = signal
        signal = self.reflector.process(signal)
        if DEBUG: print(f"[DEBUG] Reflector: in={reflect_in} -> out={signal}")

        # Left to right through rotors (inverse)
        for i, rotor in enumerate(self.rotors, 1):
            offset_signal = (signal + rotor.position) % 26
            rotor_output = rotor.wiring.index(chr(offset_signal + ord('A')))
            signal = (rotor_output - rotor.position) % 26
            if DEBUG: print(f"[DEBUG] Rotor {i} reverse: signal={offset_signal} -> {rotor_output} -> {signal}")

        # Convert back to char
        result_char = chr(signal + ord('A'))

        # Final plugboard substitution
        pre_final = result_char
        result_char = self.plugboard.process(result_char)
        if DEBUG: print(f"[DEBUG] Final plugboard in: {pre_final} -> out: {result_char}")

        return result_char

    # -------------------------------------------------------------------
    # Symbol Mapping Data (Not Part of Enigma Machine Logic)
    #
    # This symbol encoding system is a custom layer added to support 
    # characters that are not normally handled by the traditional 
    # Enigma machine, such as punctuation, digits, and lowercase letters.
    #
    # Each symbol is replaced by a unique 3-letter code starting with 'Z'
    # (e.g., space -> "ZSP", comma -> "ZCM", lowercase 'a' -> "ZUA", etc.)
    #
    # This allows the Enigma machine (which normally only processes 
    # uppercase A–Z letters) to indirectly handle extended characters 
    # by encoding them beforehand and decoding them afterward.
    #
    # IMPORTANT: uppercase_letters_only, encode_text and decode_text are a 
    # *pre-processing and post-processing* layer for compatibility and is 
    # NOT part of the historical Enigma machine.
    # -------------------------------------------------------------------
    def uppercase_letters_only(self, text):
        return any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in text)

    def encode_text(self, text):
        if DEBUG: print("[DEBUG] Encoding String Data:")
        result = ""
        for char in text:
            if char in SYMBOL_MAP:
                result += SYMBOL_MAP[char]
                if DEBUG: print(f"[DEBUG] - Found: character [{char}] was converted to {SYMBOL_MAP[char]}")
            elif char.isupper():
                result += char  
            else:
                result += char
        return result
    
    def decode_text(self, encoded):
        if DEBUG: print("[DEBUG] Decoding String Data:")

        # Ensure longest matches are handled first (e.g., ZUPA before ZUP)
        pattern = re.compile('|'.join(re.escape(k) for k in sorted(REVERSE_SYMBOL_MAP, key=len, reverse=True)))

        def replace_match(match):
            symbol = match.group(0)
            decoded_char = REVERSE_SYMBOL_MAP[symbol]
            if DEBUG:
                print(f"[DEBUG] - Found symbol: {symbol} -> Decoded to: [{decoded_char}]")
            return decoded_char

        decoded = pattern.sub(replace_match, encoded)
        return decoded

# Provides a command-line interactive mode for user configuration and encoding
def interactive_mode(enigma, preset_args=None):
    encode_schema = False

    while True:
        positions = ' '.join(chr(r.position + ord('A')) for r in enigma.rotors)
        print("\nEnigma Machine Interactive Mode")
        print("-----------------------------------------------------")
        print(" 1. Load custom rotors")
        print(" 2. Load custom plugboard")
        print(" 3. Load custom reflector")
        print("-----------------------------------------------------")
        print(" 4. Enigma current settings")
        print("-----------------------------------------------------")
        print(" 5. Toggle Encode Schema (Not Enigma Machine Logic)")
        print(f" 6. Set rotor positions: Currently: [{positions}]")
        print(" 7. Encode/Decode text")
        print("\n Q. Exit")
      
        choice = input("\nEnter your choice (1-6) or Q to Quit: ")

        if choice == '1':
            indices = input("Enter three rotor numbers (1-10, space-separated): ")
            try:
                rotor_indices = [int(x) for x in indices.split()]
                if all(1 <= x <= 10 for x in rotor_indices):
                    enigma.load_custom_rotors(rotor_indices)
                    print("Custom rotors loaded")
            except ValueError:
                print("Invalid input. Please enter numbers between 1 and 10")

        elif choice == '2':
            pb_name = input("Enter plugboard name (1-5): ").upper()
            if enigma.load_custom_plugboard(pb_name):
                print(f"Plugboard {pb_name} loaded")
            else:
                print("Invalid plugboard name or file not found")

        elif choice == '3':
            with open('reflector.json', 'r') as f:
                reflector_data = json.load(f)
                print("\nAvailable reflectors:")
                for reflector in reflector_data['reflectors']:
                    print(f"{reflector['name']}: {reflector['wiring']}")
            reflector_choice = input("Enter reflector letter (A-Z): ").upper()
            for reflector in reflector_data['reflectors']:
                if reflector['name'] == reflector_choice:
                    enigma.set_reflector(reflector['wiring'])
                    print(f"Reflector {reflector_choice} loaded")
                    break

        elif choice == '4':
            enigma.show_current_setting()

        elif choice == '5':
            if encode_schema:
                encode_schema = False
            else: 
                encode_schema = True
            print(f"Encode Schema is set to {encode_schema}.")

        elif choice == '6':
            positions = input("Enter three letters for rotor positions (e.g., AAA): ")
            if len(positions) >= 3:
                enigma.set_rotor_positions(positions[:3])
                print(f"Rotor positions set to: {positions[:3]}")

        elif choice == '7':
            text = input("Enter text to encode/decode: ")
            if encode_schema:
                if enigma.uppercase_letters_only(text):
                    encoded_text = enigma.encode_text(text)
                    result = enigma.process_text(encoded_text)
                else: 
                    decode_text = enigma.process_text(text)
                    result = enigma.decode_text(decode_text)
            else:
                result = enigma.process_text(text)
            print(f"Result: [{result}]")

        elif choice.lower() == 'q':
            break

# Simple test to encode and decode a message and verify round-trip correctness
def test_enigma():
    print(" Running test_enigma()")
    enigma = EnigmaMachine()
    enigma.set_rotor_positions("AAA")
    message = "HELLO WORLD"
    encoded = enigma.process_text(message)
    print(f" +{YELLOW}       Original{RESET}: {message}")
    print(f" +{CYAN}        Encoded{RESET}: {encoded}")
    
    enigma = EnigmaMachine()
    enigma.set_rotor_positions("AAA")
    decoded = enigma.process_text(encoded)
    print(f" +{BLUE}        Decoded{RESET}: {decoded}\n")
    if decoded == message: print(" Test passed: round-trip encoding/decoding successful")
    else: print(" Test failed: decoded text does not match original")

    # Runing Enigma cipher with Encoding schema. 
    print("\n\n Running test_enigma() with Encoding Schema")
    enigma = EnigmaMachine()
    enigma.set_rotor_positions("AAA")
    message = "Hello World!"
    encode_message = enigma.encode_text(message)
    encoded = enigma.process_text(encode_message)
    print(f" +{YELLOW}       Original{RESET}: {message}")
    print(f" +{CYAN} Encoded Schema{RESET}: {encode_message}")
    print(f" +{CYAN} Encoded Enigma{RESET}: {encoded}")

    enigma = EnigmaMachine()
    enigma.set_rotor_positions("AAA")
    decoded = enigma.process_text(encoded)
    decode_message = enigma.decode_text(decoded)
    print(f" +{BLUE} Decoded Enigma{RESET}: {decoded}")
    print(f" +{BLUE} Decoded Schema{RESET}: {decode_message}\n")
    if decode_message == message: print(" Test passed: round-trip encoding/decoding successful")
    else: print(" Test failed: decoded text does not match original")

# Entry point of the program, handles CLI arguments
def main():
    parser = argparse.ArgumentParser(description='Enigma Machine Simulator')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--text', help='Text to encode/decode')
    parser.add_argument('--rotors', nargs=3, type=int, help='Three rotor numbers (1-20)')
    parser.add_argument('--reflector', help='Reflector letter (A-Z)')
    parser.add_argument('--positions', help='Three letter rotor positions')
    parser.add_argument('--plugboard', help='Plugboard name (1-5)', default='1')
    parser.add_argument('--setting', action='store_true', help='Shows a header of Enigma\'s current settings')
    parser.add_argument('--encode', action='store_true', help='Convert the characters to a custom encoding scheme')
    parser.add_argument('--debug', action='store_true', help='Show troubleshooting steps')
    parser.add_argument('--test-output', action='store_true', help='Resets and runs the output through as a test')
    parser.add_argument('--test', action='store_true', help='Self Test Routine')
    args = parser.parse_args()

    enigma = EnigmaMachine()

    if args.debug:
        global DEBUG
        DEBUG = True
        print("[DEBUG] Debug mode is ON")

    # Load configurations
    if args.rotors:
        enigma.load_custom_rotors(args.rotors)

    if args.positions:
        enigma.set_rotor_positions(args.positions)

    if args.plugboard:
        enigma.load_custom_plugboard(args.plugboard)

    # For test-output mode, we will save the settings before processing
    if args.test_output:
        # Save current settings before running the first test
        original_rotors = enigma.rotors.copy()  # Save a snapshot of the current rotors
        original_rotor_positions = [rotor.position for rotor in enigma.rotors]  # Save the initial rotor positions
        original_plugboard = enigma.plugboard  # Save the current plugboard
        original_reflector = enigma.reflector  # Save the current reflector

    if args.interactive or len(sys.argv) == 1:
        interactive_mode(enigma, args)

    elif args.text:
        if args.setting:
            enigma.show_current_setting()

        if args.encode:
            # Save initial rotor positions before encoding
            initial_positions = [rotor.position for rotor in enigma.rotors]
            
            if enigma.uppercase_letters_only(args.text):
                encoded_text = enigma.encode_text(args.text)
                result = enigma.process_text(encoded_text)
            else:
                enigma_text = enigma.process_text(args.text)
                result = enigma.decode_text(enigma_text)

            # Reset rotor positions after encoding
            for rotor, pos in zip(enigma.rotors, initial_positions):
                rotor.position = pos

        else:
            result = enigma.process_text(args.text)

        if args.test_output:
            print("\n Encoding the input text, then resetting the machine to verify correct decryption of the output:")
            print(f" >{YELLOW}   Input Text{RESET}: {args.text}")
            print(f" >{CYAN} Encoded text{RESET}: {result}")
        else:
            print(result)

        if args.test_output:
            # Reset the settings to the original ones before running the test again
            enigma.rotors = original_rotors
            enigma.plugboard = original_plugboard
            enigma.reflector = original_reflector

            # Reset rotor positions to the original ones before decoding
            for rotor, pos in zip(enigma.rotors, original_rotor_positions):
                rotor.position = pos

            # Run the encoded text through the Enigma machine again for decoding
            if args.setting:
                enigma.show_current_setting()

            if args.encode:
                # Save initial rotor positions before encoding
                initial_positions = [rotor.position for rotor in enigma.rotors]
                
                if enigma.uppercase_letters_only(result):
                    encoded_text = enigma.encode_text(result)
                    decoded_result = enigma.process_text(encoded_text)
                else:
                    enigma_text = enigma.process_text(result)
                    decoded_result = enigma.decode_text(enigma_text)

            else:
                decoded_result = enigma.process_text(result)

            print(f" >{BLUE} Decoded text{RESET}: {decoded_result}\n")

    elif args.test:
        enigma.show_current_setting()
        test_enigma()

    else:
        parser.print_help()

# Main execution guard
if __name__ == "__main__":
    main()
