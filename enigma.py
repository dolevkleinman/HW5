import json
import sys

ALPHABET_SIZE = 26
W1_MIN = 1
W1_MAX = 8
W3_ZERO = 0
W3_FIVE = 5
W3_TEN = 10

PARAMETER_ERROR = "Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>"
RUNTIME_ERROR = "The enigma script has encountered an error"

# custom exception for JSON file reading errors
class JSONFileException(Exception):
    pass


class Enigma:
    def __init__(self, hash_map, wheels, reflector_map):
        self.hash_map = hash_map
        self.wheels = wheels
        self.reflector_map = reflector_map

        # reverse hash map for number to letter conversion
        self.reverse_hash_map = {value: letter for letter, value in hash_map.items()}
        self.non_empty_count = 0

    def encrypt(self, message):
        starting_wheels = self.wheels.copy()
        starting_count = self.non_empty_count
        result = ""
        for char in message:
            # check if character is lowercase
            if 'a' <= char <= 'z':
                # encrypt character
                encrypted_char = self.encrypt_char(char)
                self.non_empty_count += 1
            else:
                # non-lowercase letter should pass through unchanged
                encrypted_char = char
            result += encrypted_char
            self.advance_wheels()
        # reset to initial state
        self.wheels = starting_wheels
        self.non_empty_count = starting_count
        return result

    def encrypt_char(self, character):
        w1, w2, w3 = self.wheels
        # step 1: initialize i with has value of char
        i = self.hash_map[character]
        # step 2: add wheel offset if not zero
        offset = ((2 * w1) - w2 + w3) % ALPHABET_SIZE
        if offset != 0:
            i += offset
        else:
            i += 1
        # step 3: take mod 26
        i = i % ALPHABET_SIZE
        # step 4: get letter c1 from i
        c1 = self.reverse_hash_map[i]
        # step 5: get letter c2 from reflector
        c2 = self.reflector_map[c1]
        # step 6: get number from c2
        i = self.hash_map[c2]
        # step 7: subtract wheel offset
        if offset != 0:
            i -= offset
        else:
            i -= 1
        # step 8: take mod 26
        i = i % ALPHABET_SIZE
        c3 = self.reverse_hash_map[i]

        return c3

    def advance_wheels(self):
            # wheel 1: advance by 1, wrap to 1 if bigger then 8
        self.wheels[0] += 1
        if self.wheels[0] > W1_MAX:
            self.wheels[0] = W1_MIN
        # wheel 2: double if even count, subtract 1 if odd
        if self.non_empty_count % 2 == 0:
            self.wheels[1] *= 2
        else:
            self.wheels[1] -= 1
        # wheel 3 : set to 10 if divisible by 10, 5 if divisible by 3, else to 0
        if self.non_empty_count % 10 == 0:
            self.wheels[2] = W3_TEN
        elif self.non_empty_count % 3 == 0:
            self.wheels[2] = W3_FIVE
        else :
            self.wheels[2] = W3_ZERO

def load_enigma_from_path(path):
    try:
        with open(path, 'r') as f:
            config = json.load(f)
        return Enigma(config['hash_map'], config['wheels'], config['reflector_map'])
    except Exception:
        raise JSONFileException("Failed to load Enigma JSON")

def main():
    try:
        # parse command line arguments
        args = sys.argv[1:]
        # initialize variables
        config_file = None
        input_file = None
        output_file = None
        # parse flags
        i = 0
        while i < len(args):
            if args[i] == '-c':
                config_file = argv[i + 1]
                i += 2
            elif args[i] == '-i':
                input_file = argv[i + 1]
                i += 2
            elif args[i] == '-o':
                output_file = argv[i + 1]
                i += 2
            else:
                print(PARAMETER_ERROR)
                sys.exit(1)
        # check required parameters
        if config_file is None or input_file is None:
            print(PARAMETER_ERROR)
            sys.exit(1)
        # load enigma configuration
        enigma = load_enigma_from_path(config_file)
        # read input messages
        with open(input_file, 'r') as f:
            messages = f.readlines()
        #encrypt messages
        encrypted_messages = []
        for message in messages:
            # remove newline and encrypt
            encrypted = enigma.encrypt(message.rstrip('\n'))
            encrypted_messages.append(encrypted)
        # output encrypted messages
        if output_file:
            with open(output_file, 'w') as f:
                for msg in encrypted_messages:
                    f.write(msg + '\n')
        else:
            for msg in encrypted_messages:
                print(msg)
    except Exception:
        print(RUNTIME_ERROR)
        sys.exit(1)

if __name__ == '__main__':
    main()