import numpy as np
import pandas as pd
import re

from functools import reduce
from datetime import datetime
from glob import glob


# Demographics
demo_vars = {'age_group':'age', 'sex':'sex', 'ethnicity':'eth', 'region':'reg',
             'imd':'imd', 'learning_disability':'ld', 'mental_illness':'mi'}

# NICE thresholds
threshold_vars = ['hba1c_gt_48', 'hba1c_gt_58', 'hba1c_gt_64', 'hba1c_gt_75']

# Import variables
import_vars = threshold_vars + list(demo_vars.keys()) + ['patient_id', 'diabetes_type', 'took_hba1c', 'prev_elevated_48',
                                            'prepandemic_hba1c', 'hba1c_mmol_per_mol', 'prepandemic_prediabetes']

# Read in and append input files
li_elev = []
li_predm = []

for file in glob('output/data/input_elev*.csv'):
    df_temp = pd.read_csv(file)[import_vars]
    # Creates date variable based on file name
    df_temp['date'] = file[(re.search(r"\d",file).start()):-4]
    df_temp['date'] = df_temp['date'].apply(lambda x: datetime.strptime(x.strip(), '%Y-%m-%d'))
    # Filter to T2DM patients with elevated HbA1c pre-pandemic
    df_temp_elev = df_temp.loc[(df_temp.diabetes_type == 'T2DM') & 
                               (df_temp.prev_elevated_48 == 1) & 
                               (df_temp.hba1c_mmol_per_mol > 0)]
     # Filter to prediabetic patients pre-pandemic
    df_temp_predm = df_temp.loc[(df_temp.prepandemic_prediabetes == 1) & 
                                (df_temp.hba1c_mmol_per_mol > 0)]
    # Generates a count column
    li_elev.append(df_temp_elev)
    li_predm.append(df_temp_predm)
    
df_t2dm_elev = pd.concat(li_elev, axis=0, ignore_index=False).reset_index(drop=True)
df_predm = pd.concat(li_predm, axis=0, ignore_index=False).reset_index(drop=True)

# Get counts for each group
def gen_sum(df_in, group=''):
    
    groups = ['date']
    if group != '': 
        groups = ['date', group]
        
    df_out = df_in.groupby(groups).agg(
                                       ct_took_hba1c  = ('took_hba1c', 'sum'),
                                       ct_hba1c_gt_48 = ('hba1c_gt_48','sum'),
                                       ct_hba1c_gt_58 = ('hba1c_gt_58','sum'),
                                       ct_hba1c_gt_64 = ('hba1c_gt_64','sum'),
                                       ct_hba1c_gt_75 = ('hba1c_gt_75','sum'),
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

df_t2dm_elev_sum = gen_sum(df_t2dm_elev)
df_t2dm_elev_sum.to_csv('output/data/calc_t2dm_elev.csv')

df_predm_sum = gen_sum(df_predm)
df_predm_sum.to_csv('output/data/calc_predm.csv')

for g in demo_vars:
    df_elev_tmp = gen_sum(df_t2dm_elev, g)
    df_predm_tmp = gen_sum(df_predm, g)

    if g in ['ethnicity', 'imd', 'learning_disability']:
        df_elev_tmp = df_elev_tmp.replace({g: lookup_dict[g]})
        df_predm_tmp = df_predm_tmp.replace({g: lookup_dict[g]})

    elif g == "age_group":
        df_elev_tmp = df_elev_tmp.loc[df_elev_tmp.age_group != '0-15']
        df_predm_tmp = df_predm_tmp.loc[df_predm_tmp.age_group != '0-15']

    # Export data
    df_elev_tmp.to_csv(f'output/data/calc_t2dm_elev_{demo_vars[g]}.csv')
    df_predm_tmp.to_csv(f'output/data/calc_predm_{demo_vars[g]}.csv')