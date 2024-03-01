import os
import time

from openpyxl import load_workbook, Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Alignment
from openpyxl.utils.cell import coordinate_from_string

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

    def non_def_foul(self):
        """
        This function checks if -
        A non-defensive action(other than ST, SL, AD, GD, HB) was given a foul
        :return: None
        """
        mask = ~(self.df['action'].isin(['ST', 'SL', 'AD', 'GD', 'HB'])) & (self.df['special_attribute'].isin(['F', 'YC', 'RC']))
        non_df_action = self.df[mask]
        non_df_action_count = non_df_action['action'].count()

        if (non_df_action_count != 0):
            message = 'A non defensive action was tagged as a foul. Please check!'
            print(message)
            print(non_df_action.to_string())
            self.qc_excel_log(non_df_action, message, 30, 'non_df_action_foul')

    def calling_func(self):
        self.non_def_foul()


# if __name__ == "__main__":
#     read_obj = Read()
#     df = read_obj.read()
#
#     match_obj = MatchDetails
#
#     qc_obj = QualityChecks(df)
#     qc_obj.calling_func()




def appropriate_foul():
    '''
    This function checks if
    1. A non-defensive action(other than ST, SL, AD, GD, HB) was given a foul
    2. A successful defensive action was tagged as a foul(need to check for yc and rc)
    '''
    non_df_action = df
    [~(df['action'].isin(['ST', 'SL', 'AD', 'GD', 'HB'])) & (df['special_attribute'].isin(['F', 'YC', 'RC']))]
    non_df_action_foul = non_df_action['action'].count()

    successful_df_action = df[(df['action'].isin(['ST', 'SL', 'AD', 'GD']))  & (df['notation'] == '1') &
    (df['special_attribute'].isin(['F', 'YC', 'RC']))]
    successful_df_action_foul = successful_df_action['action'].count()

    if (non_df_action_foul != 0) | (successful_df_action_foul != 0):
        if (non_df_action_foul != 0):
            print('A non defensive action was tagged as a foul. Please check!')
            display(non_df_action)
            # logger_obj.info(f"\n\nA non defensive action was tagged as a foul. Please check! \n{write_log(non_df_action)}\n\n" + '*'*100)
            message = 'A non defensive action was tagged as a foul. Please check!'
            qc_excel_log(non_df_action, message, 30, 'non_df_action_foul')

        if (successful_df_action_foul != 0):
            print('A successful defensive action was tagged as a foul. Please check!')
            display(successful_df_action)
            # logger_obj.info(f"\n\nA successful defensive action was tagged as a foul. Please check! \n{write_log(successful_df_action)}\n\n" + '*'*100)
            message = 'A successful defensive action was tagged as a foul. Please check!'
            qc_excel_log(successful_df_action, message, 30, 'successful_df_action_foul')

    else:
        print('Appropriate foul QC done.')


