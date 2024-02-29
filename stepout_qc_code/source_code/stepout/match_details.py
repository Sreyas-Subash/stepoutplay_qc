import os
import datetime

from analyst_details import AnalystDetails

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
parent_dir = os.path.abspath(os.path.join(src_dir, os.pardir))
os.chdir(parent_dir)


class MatchDetails:
    def __init__(self, analyst_names):
        self.analyst_names = analyst_names
        self.match_id = int(input('Match ID please... = '))
        self.analyst_id = int(input(f'Choose the Analyst ID\n{self.analyst_names} = '))
        self.analyst_name = self.analyst_names[self.analyst_id]
        self.team_a_name = input('Team A name = ')
        self.team_b_name = input('Team B name = ')
        self.current_date = datetime.date.today()

    def game_time_pay(self):
        self.game_time = int(input("""Game time?
Type 1 for 90 minutes
Type 2 for 45 minutes
Type 3 for less than 60 minutes
Type 4 for manually entering
--->"""))

        if self.game_time == 1:
            self.renumeration = 500
            self.game_time = 90
        elif self.game_time == 2:
            self.renumeration = 250
            self.game_time = 45
        elif self.game_time == 3:
            self.renumeration = 300
            self.game_time = 'Less than 60'
        elif self.game_time == 4:
            self.renumeration = int(input("Enter renumeration : "))
            self.game_time = int(input("Enter game time : "))
        else:
            print('You have chosen an invalid option. Try again!')

        return self.renumeration, self.game_time

    def calling_func(self):
        self.renumeration, self.game_time = self.game_time_pay()

        self.data = {'team_a_name': self.team_a_name,
                     'team_b_name': self.team_b_name,
                     'match_id': self.match_id,
                     'game_time': self.game_time,
                     'current_date': self.current_date,
                     'renumeration': self.renumeration
                     }
        print(self.data)


def renumeration_func():
    '''
    This function creates a renumeration excel file as per the inputs given.
    It checks the match id to make sure no matches are duplicated.
    '''
    try:

        analyst_names = {
            1: 'Sreyas',
            2: 'Boni',
            3: 'Arpit',
            4: 'Sudhanva'
        }

        write_path_xlsx = r'..\write_string\renumeration.xlsx'
        initial_input = input('Do you wish to add match details? (y/n)')

        # Taking the match details from the user
        if initial_input.lower() == 'y':
            global team_a_name
            global team_b_name
            analyst_id = int(input(f'Choose the Analyst ID\n{analyst_names} = '))
            analyst_name = analyst_names[analyst_id]
            team_a_name = input('Team A name = ')
            team_b_name = input('Team B name = ')
            match_id = match_idd
            game_time = int(
                input('Game time?\nType 1 for 90 minutes\nType 2 for 45 minutes\nType 3 for less than 60 minutes\n'))
            current_date = datetime.date.today()

            # check to-do
            if game_time == 1:
                renumeration = 500
                game_time = 90
            elif game_time == 2:
                renumeration = 250
                game_time = 45
            elif game_time == 3:
                renumeration = 300
                game_time = 'Less than 60'
            else:
                print('You have chosen an invalid option. Try again!')

            data = {
                'team_a_name': team_a_name,
                'team_b_name': team_b_name,
                'match_id': match_id,
                'game_time': game_time,
                'current_date': current_date,
                'renumeration': renumeration
            }

            # There are 4 possible scenarios here
            # 1. The file exists
            if os.path.exists(write_path_xlsx):
                wb = load_workbook(write_path_xlsx)
                sheet_name = analyst_name
                sheet_exists = sheet_name in wb.sheetnames

                # 2. File exists but sheet doesn't
                if not sheet_exists:
                    ws = wb.create_sheet(sheet_name)
                    renumeration_df = pd.DataFrame(data, index=[0])
                    for r in dataframe_to_rows(renumeration_df, index=False, header=True):
                        ws.append(r)
                    for cell in ws[1]:
                        cell.style = 'Pandas'
                    wb.save(write_path_xlsx)

                # 3. File and sheet exists
                else:
                    renumeration_df = pd.read_excel(write_path_xlsx, sheet_name=analyst_name)
                    renumeration_df.loc[len(renumeration_df)] = data
                    if renumeration_df['match_id'].duplicated().sum() > 0:
                        display(renumeration_df[renumeration_df['match_id'].duplicated()])
                        print('This match id seems to be a duplicate. Please check!')
                        # renumeration_df = renumeration_df.drop_duplicates(subset = ['match_id'])
                    else:
                        renumeration_df = pd.DataFrame(data, index=[0])
                        for r in dataframe_to_rows(renumeration_df, index=False, header=False):
                            ws = wb[sheet_name]
                            ws.append(r)
                        wb.save(write_path_xlsx)

            # 4. File does not exists
            else:
                renumeration_df = pd.DataFrame(data, index=[0])
                renumeration_df.to_excel(write_path_xlsx, sheet_name=analyst_name, index=False)




        else:
            print('Proceeding without filling details')

    except PermissionError as e:
        print(f'{e}\nThe renumeration xlsx file might be open. Please close it and try again')

    except Exception as e:
        print(f'An error occured : {e}')


if __name__ == "__main__":
    analyst_obj = AnalystDetails()
    analyst_names = analyst_obj.analyst_names


    match_obj = MatchDetails(analyst_names)
    match_obj.calling_func()