# to-do
# spreadsheet api integration
# stepout api endpoints integration
# option to run a one or multiple filess


import sys
import traceback
import docx
import pandas as pd
import os

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
parent_dir = os.path.abspath(os.path.join(src_dir, os.pardir))
os.chdir(parent_dir)

game_time = int(input("""Game time?
Type 1 for 90 minutes
Type 2 for 45 minutes
Type 3 for less than 60 minutes
"""))

print(game_time)