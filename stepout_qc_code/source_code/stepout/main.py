import os
import time
from read_coded_string import Read
from analyst_details import AnalystDetails
from match_details import MatchDetails
from stepout.qc_functions import QualityChecks
from df_to_coded_string import Write
from match_report import MatchReport
import json
import pandas as pd
import sys
import options

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
parent_dir = os.path.abspath(os.path.join(src_dir, os.pardir))
os.chdir(parent_dir)

if __name__ == "__main__":

    if options.option.lower() == 'm':

        df_full = pd.read_csv("json_file/nsw.csv")
        df_cleaned = df_full.dropna(subset=['match_string'])
        qc_path_xlsx = "excel_logs/All_QC_Time_" + time.strftime("%H-%M-%S") + ".xlsx"
        error_matches = {}

        for index, row in df_cleaned.iterrows():
            match_id = int(row['match_id'])
            coded_string = row['match_string']

        # with open("json_file/match_dict_mini.json", 'r') as file:
        #     # Step 2: Load the JSON data
        #     data = json.load(file)
        #
        #     for match_id in data:
        #         coded_string = data[match_id]["match_string"]

            coded_string_list = coded_string.split(',')
            df = pd.DataFrame(coded_string_list, columns=['strings'])
            new_df = df['strings'].str.split('-', expand=True)

            # checks if 2 rows stuck together without comma
            if new_df.columns.stop > 10:
                print('Seems like a comma is missing!')
                print(f'match id = {match_id}')
                print(new_df[new_df[10].notna()].to_string())
                error_matches[match_id] = new_df[new_df.iloc[:, 10].notna()][6].to_list()
                continue

            if new_df.shape[1] == 10:
                df[['team', 'jersey_number', 'action', 'notation', 'start_grid', 'end_grid', 'timestamp', 'foot',
                    'special_attribute', 'half']] = new_df
            else:
                df[['team', 'jersey_number', 'action', 'notation', 'start_grid', 'end_grid', 'timestamp', 'foot',
                    'special_attribute']] = new_df

            df = df.drop(columns=['strings'])
            df['special_attribute'] = df['special_attribute'].str.strip()

            qc_obj = QualityChecks(df, match_id, qc_path_xlsx)
            qc_obj.calling_func()

        error_matches_df = pd.DataFrame(list(error_matches.items()), columns=['match_id', 'string'])
        if error_matches_df.shape[0] != 0:
            error_matches_df.to_csv("json_file/error_matches_list.csv", index=False)

    else:

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
            data = match_obj.calling_func()

            initial_input = input('Do you wish to create match report? (y/n)')
            if initial_input.lower() == 'y':
                match_report_obj = MatchReport(data, df)
                match_report_obj.calling_func()
            else:
                print("Proceeding without creating match report")
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

        else:
            print("Proceeding without running df to coded string")