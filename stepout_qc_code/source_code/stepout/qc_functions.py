import os
import time

import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Alignment
from openpyxl.utils.cell import coordinate_from_string
from package_necessity import star_count

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
parent_dir = os.path.abspath(os.path.join(src_dir, os.pardir))
os.chdir(parent_dir)

class QualityChecks:
    path = r'excel_logs'
    if not os.path.exists(path):
        os.makedirs(path)

    def __init__(self, df, match_id):
        self.df = df
        self.match_id = match_id
        self.qc_path_xlsx = "excel_logs/Match_ID_" + str(match_id) + "_Time_" + time.strftime("%H-%M-%S") + ".xlsx"

    def qc_excel_log(self, df, message, size, sheet_name):
        """
        Records all the errors to an excel file
        :param df: pd.DataFrame
        :param message: str
        :param size: int
        :param sheet_name: str
        :return: None
        """

        if os.path.exists(self.qc_path_xlsx):
            wb = load_workbook(self.qc_path_xlsx)
            ws = wb.create_sheet(f'{sheet_name}')

        else:
            wb = Workbook()
            ws = wb.active
            ws.title = f'{sheet_name}'

        a1 = ws['A1']
        a1.value = f'{message}'

        a1.font = Font(size=12, underline='single')
        a1.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        for row in dataframe_to_rows(df, index=False, header=True):
            ws.append(row)

        for cell in ws[2]:
            cell.style = 'Pandas'

        for row in ws.iter_rows():
            for cell in row:
                if cell.value:
                    max_cell = cell

        coordinate = coordinate_from_string(max_cell.coordinate)
        max_col = coordinate[0]
        max_row = coordinate[1]

        ws.move_range(f"A2:{max_col}{max_row}", rows=0, cols=1)

        ws.column_dimensions['A'].width = size

        wb.save(self.qc_path_xlsx)

    def display_output(self, output_df, message, cell_size, sheet_name, wrong_data_count = 1):
        if wrong_data_count != 0:
            print('*' * star_count)
            print(message)
            print(output_df.to_string())
            print('*' * star_count)
            self.qc_excel_log(output_df, message, cell_size, sheet_name)
        else:
            print(f'###{sheet_name} qc done###')

    def non_def_foul(self):
        """
        This function checks if -
        A non-defensive action(other than ST, SL, AD, GD, HB) was given a foul
        :return: None
        """
        mask = ~(self.df['action'].isin(['ST', 'SL', 'AD', 'GD', 'HB'])) & (self.df['special_attribute'].isin(['F', 'YC', 'RC']))
        non_df_action = self.df[mask]
        non_df_action_count = non_df_action['action'].count()
        message = 'A non defensive action was tagged as a foul. Please check!'
        self.display_output(non_df_action, message, 30, 'non_df_action_foul', non_df_action_count)

    def successful_def(self):
        """
         This function checks if -
         A successful defensive action was tagged as a foul
        :return: None
        """
        mask = (self.df['action'].isin(['ST', 'SL', 'AD', 'GD']))  & (self.df['notation'] == '1') & \
               (self.df['special_attribute'].isin(['F', 'YC', 'RC']))
        successful_df_action = self.df[mask]
        successful_df_action_foul_count = successful_df_action['action'].count()
        message = 'A successful defensive action was tagged as a foul. Please check!'
        self.display_output(successful_df_action, message, 30, 'successful_df_action_foul', successful_df_action_foul_count)

    def corner_qc_1(self):
        """
        The purpose of this function -
        If there are any corners which didn't start from the correct corner start grid(1,01,71)
        """

        mask = (self.df['special_attribute'] == 'CN') & ~(self.df['start_grid'].isin(['01', '1', '71']))
        false_cn = self.df[mask]
        false_cn_count = false_cn['action'].count()
        message = 'This Corner started from a false start grid(not starting from [1, 01, 71]). Please check!'
        self.display_output(false_cn, message, 40, 'corner_grid_check', false_cn_count)

    def corner_qc_2(self):
        """
        The purpose of this function -
        If there are any unassigned corners within the crosses
        """
        # To check if any crosses starting from (1, 01, 71) are corners
        mask = (self.df['special_attribute'] != 'CN') \
               & (self.df['start_grid'].isin(['1','01','02','11','61','71','72'])) \
               & (self.df['action'] == 'C')
        corner_in_cross = self.df[mask]
        corner_in_cross_count = corner_in_cross['action'].count()
        message = f'{corner_in_cross_count} cross found with corner grid. Check if they are corners'
        self.display_output(corner_in_cross, message, 30, 'cross_check', corner_in_cross_count)

    def gk_qc_1(self):
        """
        This function checks if GK is taken from outside goal area
        :return: None
        """

        mask = (self.df['special_attribute'] == 'GK') & ~(self.df['start_grid'].isin(['40', '50']))
        wrong_goalkick = self.df[mask]
        wrong_goalkick_count = wrong_goalkick['action'].count()
        message = 'GK QC-1\nThis goal kick is taken outside the goal area. Please check!'
        self.display_output(wrong_goalkick, message, 30, 'GK QC-1', wrong_goalkick_count)

    def gk_qc_2(self):
        """
        This function checks if GH or GT is taken from outside penalty area
        :return:
        """

        gk_d_grids = ['29', '30', '39', '40', '49', '50', '59', '60']
        mask = (self.df['action'].isin(['GH', 'GT'])) & ~(self.df['start_grid'].isin(gk_d_grids))
        wrong_goalkeeper = self.df[mask]
        wrong_goalkeeper_count = wrong_goalkeeper['action'].count()
        message = 'GK QC-2\nThis GH or GT taken outside penalty area. Please check!'
        self.display_output(wrong_goalkeeper, message, 30, 'GK QC-2', wrong_goalkeeper_count)

    def penalty_qc(self):
        """
        This function checks if PK is taken from the appropriate grid location(32, 42)
        :return: None
        """
        mask = (self.df['special_attribute'] == 'PK') & ~(self.df['start_grid'].isin(['32', '42']))
        wrong_pk = self.df[mask]
        wrong_pk_count = wrong_pk['action'].count()
        message = 'This penalty kick is taken outside the penalty area(32, 42). Please check!'
        self.display_output(wrong_pk, message, 30, 'Penalty_check', wrong_pk_count)

    def unsuccessful_interception(self):
        """
        This function checks if
        There are any unsuccessful interceptions(IN-0).
        :return: None
        """
        mask = (self.df['action'].isin(['IN', 'XIN'])) & (self.df['notation'] == '0')
        unsuccessful_interception = self.df[mask]
        unsuccessful_interception_count = unsuccessful_interception['action'].count()
        message = 'An unsuccessful interception was tagged. Please check!'
        self.display_output(unsuccessful_interception, message, 30, 'unsuccessful_interception_check', unsuccessful_interception_count)

    def misbehaviour_foul_count(self):
        """
        This function finds the misbehaviour foul counts
        :return:
        misbehaviour_foul_a : int -> misbehaviour foul count for team A
        misbehaviour_foul_b : int -> misbehaviour foul count for team B
        """
        misbehaviour_foul_a = 0
        misbehaviour_foul_b = 0
        # misbehaviour foul standard notation ST-0 with YC or RC
        mask_1 = (self.df['action'] == 'ST') & (self.df['notation'] == '0') & (self.df['special_attribute'].isin(['YC', 'RC']))
        misbehaviour_foul_index_list = self.df[mask_1].index

        for index in misbehaviour_foul_index_list:
            # misbehaviour foul standard notation will not have XST
            # df.index[-1] to make sure index does not run out of range
            mask_2 = (index == self.df.index[-1]) or (self.df.loc[index + 1, 'action'] != 'XST')
            if (mask_2) & (self.df.loc[index, 'team'] == 'A'):
                misbehaviour_foul_a += 1
            elif (mask_2) & (self.df.loc[index, 'team'] == 'B'):
                misbehaviour_foul_b += 1

        return misbehaviour_foul_a, misbehaviour_foul_b

    def fk_pk_foul_count(self):
        """
        finding fk-pk and fouls count
        :return:
        teama_foul : int -> team A foul total count after misbehaviour foul count is subtracted
        teama_fk_pk : int -> team A fk-pk total count
        teamb_foul : int -> team B foul total count after misbehaviour foul count is subtracted
        teamb_fk_pk : int -> team B fk-pk total count
        """
        misbehaviour_foul_a, misbehaviour_foul_b = self.misbehaviour_foul_count()
        foul_type = (self.df['action'].isin(['HB', 'OFF'])) | (self.df['special_attribute'].isin(['F', 'YC', 'RC']))
        fk_pk = self.df['special_attribute'].isin(['FK', 'PK'])

        teamb_foul = self.df[(self.df['team'] == 'B') & (foul_type)]['action'].count()
        teamb_foul = teamb_foul - misbehaviour_foul_b
        teamb_fk_pk = self.df[(self.df['team'] == 'B') & (fk_pk)]['action'].count()

        teama_foul = self.df[(self.df['team'] == 'A') & (foul_type)]['action'].count()
        teama_foul = teama_foul - misbehaviour_foul_a
        teama_fk_pk = self.df[(self.df['team'] == 'A') & (fk_pk)]['action'].count()

        return teama_foul, teama_fk_pk, teamb_foul, teamb_fk_pk

    def fk_pk_foul_output_df(self, foul_team, fk_pk_team):
        """
        finding the fk-pk or foul without their respective pairs
        :param foul_team: List[str] -> team(s) with wrong fouls
        :param fk_pk_team: List[str] -> team(s) with wrong fk-pk
        :return: self.df.iloc[error_list]: pd.DataFrame -> output dataframe with errors
        """
        foul_mask = ((self.df['team'].isin(foul_team)) & \
                     ((self.df['action'].isin(['HB', 'OFF'])) | \
                      (self.df['special_attribute'].isin(['F', 'YC', 'RC']))))
        fk_mask = ((self.df['team'].isin(fk_pk_team)) & (self.df['special_attribute'].isin(['FK', 'PK'])))
        fk_pk_foul_df = self.df[foul_mask | fk_mask].copy()

        foul_index_list = list(self.df[foul_mask].index)
        fk_pk_index_list = list(self.df[fk_mask].index)
        fk_pk_foul_df_index_list = list(fk_pk_foul_df.index)
        correct_pair_index_list = []

        # checking if an index in fk_pk_foul_df is in foul_index and its next index is in fk_pk_index
        # also checking fk-pk and foul for alternate teams
        for idx in fk_pk_foul_df_index_list[:-1]:
            if idx in foul_index_list:
                foul_index = fk_pk_foul_df_index_list.index(idx)
                fk_pk_index_val = fk_pk_foul_df_index_list[foul_index + 1]
                foul_teamm = self.df.at[idx, 'team']
                if (fk_pk_index_val in fk_pk_index_list) and (self.df.at[fk_pk_index_val, 'team'] != foul_teamm):
                    correct_pair_index_list.append(idx)
                    correct_pair_index_list.append(fk_pk_index_val)

        # removing pairs to get fk-pk or fouls without their pairs
        for val in correct_pair_index_list:
            fk_pk_foul_df_index_list.remove(val)

        error_list = fk_pk_foul_df_index_list

        return self.df.iloc[error_list]

    def fk_pk_foul_check(self):
        """
        This function finds the misbehaviour foul counts, subtracts them from total fouls and checks if total fouls equal
        total freekick-penalty
        :return: None
        """
        teama_foul, teama_fk_pk, teamb_foul, teamb_fk_pk = self.fk_pk_foul_count()

        # verifying if the foul and fk-pk count match
        if (teamb_foul == teama_fk_pk) & (teama_foul == teamb_fk_pk):
            print('###foul_fk-pk qc done###')
        else:
            teamB = (teamb_foul == teama_fk_pk)
            teamA = (teama_foul == teamb_fk_pk)
            if not (teamB | teamA):
                foul_team = ['A', 'B']
                fk_pk_team = ['A', 'B']
            elif teamB:
                foul_team = ['A']
                fk_pk_team = ['B']
            else:
                foul_team = ['B']
                fk_pk_team = ['A']

            output_df = self.fk_pk_foul_output_df(foul_team, fk_pk_team)
            message = 'Foul to fk-pk not equal\n'\
                    f'Team A FK-PK = {teama_fk_pk}, Team B Fouls = {teamb_foul}\n'\
                    f'Team B FK-PK = {teamb_fk_pk}, Team A Fouls = {teama_foul}'
            self.display_output(output_df, message, 45, 'fk_pk_foul_check')

    def receiver_not_same(self):
        """
        This function checks if the current and receiver action are done by the same player
        :return: None
        """
        error_df = pd.DataFrame()
        receiver_actions = ['ST','SL','IN','GD','AD','SP','LP','TB','C','DR','GT','THW']
        for action in receiver_actions:
            mask = self.df['action'].isin([action, f'X{action}'])
            new_df = self.df[mask]

            for tmstmp in new_df['timestamp'].unique():
                if new_df[new_df['timestamp'] == tmstmp]['team'].count() == 1:
                    continue
                elif len(new_df[new_df['timestamp'] == tmstmp]['team'].unique()) == 1 and \
                        len(new_df[new_df['timestamp'] == tmstmp]['jersey_number'].unique()) == 1:
                    error_df = pd.concat([error_df, new_df[new_df['timestamp'] == tmstmp]])

        message = 'These current and receiver actions are done by the same player. Check!'
        self.display_output(error_df, message, 30, 'current_receiver_same', error_df.shape[0])


    def calling_func(self):
        self.non_def_foul()
        self.successful_def()
        self.corner_qc_1()
        self.corner_qc_2()
        self.gk_qc_1()
        self.gk_qc_2()
        self.penalty_qc()
        self.unsuccessful_interception()
        self.fk_pk_foul_check()
        self.receiver_not_same()


# if __name__ == "__main__":
#     read_obj = Read()
#     df = read_obj.read()
#
#     match_obj = MatchDetails
#
#     qc_obj = QualityChecks(df)
#     qc_obj.calling_func()



