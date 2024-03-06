import os
import time


src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
parent_dir = os.path.abspath(os.path.join(src_dir, os.pardir))
os.chdir(parent_dir)


class Write:

    def __init__(self, df, match_id):
        self.df = df
        self.match_id = match_id
        self.write_path = "write_string/wstring/Match_ID_" + str(self.match_id) + "_Time_" + time.strftime("%H-%M-%S") + ".txt"
        self.gd_ad_idx_list = []

    def df_to_coded_string(self, write_path, df):
        """
        This function creates a coded string from a dataframe
        :param write_path: str -> path at which coded string will be written
        :param df: pd.DataFrame -> df to be written as coded string
        :return: None
        """

        if not 'Combined' in self.df.columns:
            self.df['Combined'] = self.df.apply(lambda row: '-'.join(row), axis=1)
            cs_list = list()
            self.df['Combined'].apply(lambda x: cs_list.append(x))

            if not os.path.exists(write_path):
                with open(write_path, 'w') as file:
                    for item in cs_list:
                        if item == cs_list[-1]:
                            file.write(item)
                        else:
                            file.write(item + ',')

                print("wstring file successfully created.")

        else:
            print("Read the file again. Combined column already exists.")

        self.df.drop('Combined', axis=1, inplace=True)

    def gd_ad_idx_list_func(self, gd_ad_df):
        # finding unsuccessful AD and GD, then appending the index of last 2 rows to be corrected
        if '1' not in gd_ad_df['notation'].unique():
            for i in gd_ad_df.iloc[[-2, -1]].index:
                self.gd_ad_idx_list.append(i)

    def gd_ad_correction(self, df):
        """
        This function writes GD-0 and XGD-0 into GD-1 and XGD-1(likewise for AD) when an unsuccessful GD or AD
        takes place
        :param df: pd.DataFrame -> df to be corrected
        :return: None
        """
        for filter in [['GD', 'XGD'], ['AD', 'XAD']]:
            # finding unique timestamp of all AD and GD
            tmsp_list = df[(df['action'].isin(filter))]['timestamp'].unique()

            for tmsp in tmsp_list:
                # creating a 4 row df for each GD and AD
                gd_ad_df = df[(df['action'].isin(filter)) & (df['timestamp'] == tmsp)]
                row_count = gd_ad_df['action'].count()
                # if more than one GD or AD takes place at the same timestamp, it becomes a df of more than 4 rows
                if row_count > 4:
                    # making them separate dfs of 4 rows
                    divs = int(row_count / 4)
                    i = 1
                    while i <= divs:
                        gd_ad_dff = gd_ad_df.iloc[4 * (i - 1): 4 * i]
                        i += 1
                        self.gd_ad_idx_list_func(gd_ad_dff)
                else:
                    self.gd_ad_idx_list_func(gd_ad_df)

        # correcting the df using index list
        for idx in self.gd_ad_idx_list:
            df.at[idx, 'notation'] = '1'




    def calling_func(self):
        self.gd_ad_correction(self.df)
        self.df_to_coded_string(self.write_path, self.df)


