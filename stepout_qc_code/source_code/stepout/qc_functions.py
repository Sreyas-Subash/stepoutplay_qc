import os
import time
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

    def display_output(self, output_df, message, cell_size, sheet_name):
        print('*' * star_count)
        print(message)
        print(output_df.to_string())
        print('*' * star_count)
        self.qc_excel_log(output_df, message, cell_size, sheet_name)

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
            self.display_output(non_df_action, message, 30, 'non_df_action_foul')

    def successful_def(self):
        """
         This function checks if -
         A successful defensive action was tagged as a foul
        :return: None
        """
        mask = (self.df['action'].isin(['ST', 'SL', 'AD', 'GD']))  & (self.df['notation'] == '1') & \
               (self.df['special_attribute'].isin(['F', 'YC', 'RC']))
        successful_df_action = self.df[mask]
        successful_df_action_foul = successful_df_action['action'].count()

        if (successful_df_action_foul != 0):
            message = 'A successful defensive action was tagged as a foul. Please check!'
            self.display_output(successful_df_action, message, 30, 'successful_df_action_foul')

    def corner_qc_1(self):
        """
        The purpose of this function -
        If there are any corners which didn't start from the correct corner start grid(1,01,71)
        """

        mask = (self.df['special_attribute'] == 'CN') & ~(self.df['start_grid'].isin(['01', '1', '71']))
        false_cn = self.df[mask]
        false_cn_count = false_cn['action'].count()
        if false_cn_count != 0:
            message = 'This Corner started from a false start grid(not starting from [1, 01, 71]). Please check!'
            self.display_output(false_cn, message, 30, 'corner_grid_check')

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
        if corner_in_cross_count != 0:
            message = f'{corner_in_cross_count} cross found with corner grid. Check if they are corners'
            self.display_output(corner_in_cross, message, 30, 'cross_check')

    def gk_qc_1(self):
        """
        This function checks if GK is taken from outside goal area
        :return: None
        """

        mask = (self.df['special_attribute'] == 'GK') & ~(self.df['start_grid'].isin(['40', '50']))
        wrong_goalkick = self.df[mask]
        wrong_goalkick_count = wrong_goalkick['action'].count()
        if wrong_goalkick_count > 0:
            message = 'GK QC-1\nThis goal kick is taken outside the goal area. Please check!'
            self.display_output(wrong_goalkick, message, 30, 'GK QC-1')

    def gk_qc_2(self):
        """
        This function checks if GH or GT is taken from outside penalty area
        :return:
        """

        gk_d_grids = ['29', '30', '39', '40', '49', '50', '59', '60']
        mask = (self.df['action'].isin(['GH', 'GT'])) & ~(self.df['start_grid'].isin(gk_d_grids))
        wrong_goalkeeper = self.df[mask]
        wrong_goalkeeper_count = wrong_goalkeeper['action'].count()
        if wrong_goalkeeper_count > 0:
            message = 'GK QC-2\nThis GH or GT taken outside penalty area. Please check!'
            self.display_output(wrong_goalkeeper, message, 30, 'GK QC-2')

    def calling_func(self):
        self.non_def_foul()
        self.successful_def()
        self.corner_qc_1()
        self.corner_qc_2()
        self.gk_qc_1()
        self.gk_qc_2()


# if __name__ == "__main__":
#     read_obj = Read()
#     df = read_obj.read()
#
#     match_obj = MatchDetails
#
#     qc_obj = QualityChecks(df)
#     qc_obj.calling_func()



