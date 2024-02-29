import os
from read_coded_string import Read

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
parent_dir = os.path.abspath(os.path.join(src_dir, os.pardir))
os.chdir(parent_dir)

if __name__ == "__main__":
    # ============================================== Read coded string: ============================================== #
    read_obj = Read()
    df = read_obj.read()

    # ============================================== Analyst & match info: ============================================== #
    initial_input = input('Do you wish to add match details? (y/n)')

    if initial_input.lower() == 'y':
        pass
    else:
        print("Proceeding without filling match details")