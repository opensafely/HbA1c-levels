import pandas as pd
import os
import sys

# Pull in ethnicity file
ethnicity_df = pd.read_csv('output/data/input_ethnicity.csv')

for file in os.listdir('output/data'):
    if file.startswith(f'{sys.argv[1]}'):
        file_path = os.path.join('output/data', file)
        df = pd.read_csv(file_path)
        merged_df = df.merge(ethnicity_df, how='left', on='patient_id').set_index('patient_id')
        
        merged_df.to_csv(file_path)

# for file in os.listdir('output/data'):
#     if file == 'input.feather':
#         file_path = os.path.join('output/data', file)
#         df = pd.read_feather(file_path)
#         merged_df = df.merge(ethnicity_df, how='left', on='patient_id')
        
#         merged_df.to_feather('output/data/input_joined.feather')