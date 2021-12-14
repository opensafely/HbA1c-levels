import numpy as np
import pandas as pd

from functools import reduce
from datetime import datetime
from glob import glob


# Demographics
demo_vars = {'age_group':'age', 'sex':'sex', 'ethnicity':'eth', 'region':'reg',
             'imd':'imd', 'learning_disability':'ld', 'mental_illness':'mi'}

# NICE thresholds
threshold_vars = ['hba1c_gt_48', 'hba1c_gt_58', 'hba1c_gt_64', 'hba1c_gt_75']

# Import variables
import_vars = threshold_vars + list(demo_vars.keys()) + ['patient_id', 'diabetes_type', 'took_hba1c',
                                            'prev_hba1c_mmol_per_mol', 'hba1c_mmol_per_mol']

# Read in and append input files
li = []

for file in glob('output/data/input_median*.csv'):
    df_temp = pd.read_csv(file)[import_vars]
    # Filter to T2DM patients with previously poor glycemic control (15 months before monthly index date)
    df_temp = df_temp.loc[(df_temp.diabetes_type == 'T2DM') & 
                          (df_temp.prev_hba1c_mmol_per_mol > 58) & 
                          (df_temp.hba1c_mmol_per_mol > 0)]
    # Change from previous HbA1c result
    df_temp['hba1c_chg'] = df_temp['hba1c_mmol_per_mol'] - df_temp['prev_hba1c_mmol_per_mol']
    # 58-74 range 
    df_temp.loc[(df_temp.prev_hba1c_mmol_per_mol > 58) &
                (df_temp.prev_hba1c_mmol_per_mol < 75), 
                'hba1c_chg_58_74'] = df_temp['hba1c_chg']
    # > 75
    df_temp.loc[(df_temp.prev_hba1c_mmol_per_mol > 75),
                'hba1c_chg_75'] = df_temp['hba1c_chg']
    # Creates date variable based on file name
    df_temp['date'] = file[25:-4]
    df_temp['date'] = df_temp['date'].apply(lambda x: datetime.strptime(x.strip(), '%Y-%m-%d'))
    # Generates a count column
    df_temp['population'] = 1
    li.append(df_temp)
    
df_t2dm_subset = pd.concat(li, axis=0, ignore_index=False).reset_index(drop=True)

# Get mean of changes
def gen_mean(df_in, group=''):
    
    groups = ['date']
    if group != '': 
        groups = ['date', group]
        
    df_out = df_in.groupby(groups).agg(
                                       hba1c_chg_58_74 = ('hba1c_chg_58_74','mean'),
                                       hba1c_chg_75 = ('hba1c_chg_75','mean'),
                                       ct_58_74 = ('hba1c_chg_58_74','count'),
                                       ct_75 = ('hba1c_chg_75','count'),
                                      ).reset_index()

    return df_out


# Format fields
# Recode variables
lookup_dict = {
        "ethnicity": {1: 'White', 2: 'Mixed', 3: 'Asian',
                      4: 'Black', 5: 'Other', np.nan: 'Unknown',
                      0: 'Unknown'}, 
        "imd":      {0: 'Unknown', 1: '1 Most deprived', 2: '2',
                     3: '3', 4: '4', 5: '5 Least deprived'},
        "learning_disability":   {1:'Yes', 0:'No'}
}

df_chg_t2dm = gen_mean(df_t2dm_subset)
df_chg_t2dm.to_csv('output/data/calc_chg_t2dm_all.csv')

for g in demo_vars:
    df_tmp = gen_mean(df_t2dm_subset, g)

    if g in ['ethnicity', 'imd', 'learning_disability']:
        df_tmp = df_tmp.replace({g: lookup_dict[g]})

    elif g == "age_group":
        df_tmp = df_tmp.loc[df_tmp.age_group != '0-15']

    # Export data
    df_tmp.to_csv(f'output/data/calc_chg_t2dm_{demo_vars[g]}.csv')
