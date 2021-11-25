import pandas as pd
import os
import sys

for file in os.listdir('output/data'):
    if file.startswith('measure'):
        file_path = os.path.join('output/data', file)
        df = pd.read_csv(file_path)
        # Drop rows if population <= 5
        df = df.loc[df.population > 5]
        # Drop rows if HbA1c test counts <= 5
        if file.startswith('measure_total'):
            df = df.loc[df.took_hba1c > 5]
        elif file.startswith('measure_tests_gt48'):
            df = df.loc[df.hba1c_gt_48 > 5]
        elif file.startswith('measure_tests_gt58'):
            df = df.loc[df.hba1c_gt_58 > 5]
        elif file.startswith('measure_tests_gt64'):
            df = df.loc[df.hba1c_gt_64 > 5]
        elif file.startswith('measure_tests_gt75'):
            df = df.loc[df.hba1c_gt_75 > 5]

        df.to_csv(file_path)