import os
from read_coded_string import Read
from analyst_details import AnalystDetails
from match_details import MatchDetails
from stepout.qc_functions import QualityChecks
from df_to_coded_string import Write

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
parent_dir = os.path.abspath(os.path.join(src_dir, os.pardir))
os.chdir(parent_dir)

if __name__ == "__main__":
    match_id = int(input('Match ID please... = '))

    # ============================================== Read coded string: ============================================== #
    read_obj = Read()
    df = read_obj.read()

    # ============================================== Analyst & match info: ============================================== #
    initial_input = input('Do you wish to add match details? (y/n)')

    if initial_input.lower() == 'y':
        analyst_obj = AnalystDetails()
        analyst_names = analyst_obj.analyst_names

        match_obj = MatchDetails(analyst_names, match_id)
        match_obj.calling_func()
    else:
        print("Proceeding without filling match details")

    # ============================================== Quality checks: ============================================== #
    initial_input = input('Do you wish to run QC for this match? (y/n)')

    if initial_input.lower() == 'y':
        qc_obj = QualityChecks(df, match_id)
        qc_obj.calling_func()

    else:
        print("Proceeding without running QC")

    # ============================================== DataFrame to coded string: ============================================== #
    initial_input = input('Do you wish to rewrite the df to coded string? (y/n)')

    if initial_input.lower() == 'y':
        write_obj = Write(df, match_id)
        write_obj.calling_func()
        print(df.to_string())

    else:
        print("Proceeding without running df to coded string")