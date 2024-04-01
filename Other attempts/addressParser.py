import subprocess
import json
import os
import logging


class AddressParser:
    def __init__(self, address_parser_path, libpostal_path):
        self.address_parser_path = self._validate_file(address_parser_path, "Address parser")
        self.libpostal_path = self._validate_file(libpostal_path, "Libpostal")
        try:
            self.process = subprocess.Popen(self.address_parser_path, shell=False, universal_newlines=True,
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Address Parser is starting...")
            while True:
                line = self.process.stdout.readline().strip()
                if line == '.exit to quit the program':
                    print("Address Parser is ready")
                    break
          
        except subprocess.CalledProcessError as e:
            logging.exception("Error occurred during command execution: %s", e)
            raise
    
    @staticmethod
    def _validate_file(file_path, name):
        if not os.path.isfile(file_path) or not os.access(file_path, os.X_OK):
            raise ValueError(f"{name} path is not a valid executable file: {file_path}")
        return file_path

    @staticmethod
    def _validate_address(address):
        if not isinstance(address, str) or not address.strip():
            raise ValueError("Address must be a non-empty string")

    @staticmethod
    def _remove_special_chars(address):
        special_chars = r"≈≠><+≥≤±*÷√°⊥~Δπ≡≜∝∞≪≫⌈⌉⌋⌊∑∏γφ⊃⋂⋃μσρλχ⊄⊆⊂⊇⊅⊖∈∉⊕⇒⇔↔∀∃∄∴∵ε∫∮∯∰δψΘθαβζηικξτω∇’"
        translator = str.maketrans("", "", special_chars)
        return address.translate(translator)

    def _run_command(self, input_data=None):
        self.process.stdin.write(input_data)
        self.process.stdin.flush()
        output = []
        while True:
            line = self.process.stdout.readline().strip()
            # print("line: ", line)
            output.append(line)
            if line == '}':
               break
        # print("output: ", output)
        stderr = ""
        # stderr = self.process.stderr.readline().strip()
        # print("stderr: ", stderr)
        
        return '\n'.join(output)

    def parse_address(self, address):
        try:
            self._validate_address(address)
            address = self._remove_special_chars(address)
            address = address + '\n'
            result = self._run_command(input_data=address)
            # print("result: ", result)
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            json_data = result[json_start:json_end]
            return json.loads(json_data)
        except Exception as e:
            print("Error: ", e)

    def __del__(self):
        self.process.terminate()
        pass

# if __name__ == '__main__':
#     address_parser_path = r'C:\Workbench\libpostal\src\address_parser.exe'
#     libpostal_path = r'C:\Workbench\libpostal\src\libpostal.exe'

#     logging.basicConfig(level=logging.INFO)

#     parser = AddressParser(address_parser_path, libpostal_path)

#     for _ in range(5):
#         address = input("Enter an address: ")
#         try:
#             parsed_address = parser.parse_address(address)
#             print("Parsed Address: ", parsed_address)
#         except (FileNotFoundError, RuntimeError) as e:
#             logging.exception("Failed to parse address: ", e)