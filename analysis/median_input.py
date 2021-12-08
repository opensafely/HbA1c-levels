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
    # Creates date variable based on file name
    df_temp['date'] = file[25:-4]
    df_temp['date'] = df_temp['date'].apply(lambda x: datetime.strptime(x.strip(), '%Y-%m-%d'))
    # Generates a count column
    df_temp['population'] = 1
    li.append(df_temp)

df_median = pd.concat(li, axis=0, ignore_index=False).reset_index(drop=True)
df_median_t2dm = df_median.loc[df_median.diabetes_type == 'T2DM']

# Get patient subset with poor glycemic control prior to the pandemic
pat_subset = df_median_t2dm.loc[df_median_t2dm.prev_hba1c_mmol_per_mol > 58]['patient_id'].unique()
df_t2dm_subset = df_median_t2dm.loc[df_median_t2dm.patient_id.isin(pat_subset)]

# 58-74 range 
df_t2dm_subset.loc[(df_t2dm_subset.prev_hba1c_mmol_per_mol > 58) & 
                   (df_t2dm_subset.prev_hba1c_mmol_per_mol < 75), 
                   'hba1c_val_58_74'] = df_t2dm_subset.hba1c_mmol_per_mol

# > 75
df_t2dm_subset.loc[(df_t2dm_subset.prev_hba1c_mmol_per_mol > 75),
                   'hba1c_val_75'] = df_t2dm_subset.hba1c_mmol_per_mol

# Get median HbA1c
def gen_median(df_in, group=''):
    
    groups = ['date']
    if group != '': 
        groups = ['date', group]
        
    df_out = df_in.groupby(groups).agg(
                                       hba1c_val_58_74 = ('hba1c_val_58_74','median'),
                                       hba1c_val_75 = ('hba1c_val_75','median'),
                                       ct_58_74 = ('hba1c_val_58_74','count'),
                                       ct_75 = ('hba1c_val_75','count'),
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

df_med_t2dm = gen_median(df_t2dm_subset)
df_med_t2dm.to_csv('output/data/calc_med_t2dm_all.csv')

for g in demo_vars:
    df_tmp = gen_median(df_t2dm_subset, g)

    if g in ['ethnicity', 'imd', 'learning_disability']:
        df_tmp = df_tmp.replace({g: lookup_dict[g]})

    elif g == "age_group":
        df_tmp = df_tmp.loc[df_tmp.age_group != '0-15']

    # Export data
    df_tmp.to_csv(f'output/data/calc_med_t2dm_{demo_vars[g]}.csv')