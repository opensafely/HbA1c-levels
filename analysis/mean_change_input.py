import numpy as np
import pandas as pd

from functools import reduce
from datetime import datetime
from glob import glob

# Read in and append input files
li = []

# Demographics
demo_vars = ['age_group', 'sex', 'ethnicity', 'region',
             'imd', 'learning_disability', 'mental_illness']

# NICE thresholds
threshold_vars = ['hba1c_gt_48', 'hba1c_gt_58', 'hba1c_gt_64', 'hba1c_gt_75']

# Import variables
import_vars = threshold_vars + demo_vars + ['patient_id', 'diabetes_type', 'took_hba1c',
                                            'prev_hba1c_mmol_per_mol', 'hba1c_mmol_per_mol']

for file in glob('output/data/input_median*.csv'):
    df_temp = pd.read_csv(file)[import_vars]
    # Creates date variable based on file name
    df_temp['date'] = file[25:-4]
    df_temp['date'] = df_temp['date'].apply(lambda x: datetime.strptime(x.strip(), '%Y-%m-%d'))
    # Generates a count column
    df_temp['population'] = 1
    li.append(df_temp)
    
df_prev = pd.concat(li, axis=0, ignore_index=False).reset_index(drop=True)
df_prev_t2dm = df_prev.loc[df_prev.diabetes_type == 'T2DM']

# Get patient subset with poor glycemic control prior to the pandemic
pat_subset = df_prev_t2dm.loc[(df_prev_t2dm.prev_hba1c_mmol_per_mol > 58) & 
                              (df_prev_t2dm.hba1c_mmol_per_mol > 0)]['patient_id'].unique()
df_t2dm_subset = df_prev_t2dm.loc[df_prev_t2dm.patient_id.isin(pat_subset)]

df_t2dm_subset['hba1c_chg'] = df_t2dm_subset['prev_hba1c_mmol_per_mol'] - df_t2dm_subset['hba1c_mmol_per_mol']

# 58-74 range 
df_t2dm_subset.loc[(df_t2dm_subset.prev_hba1c_mmol_per_mol > 58) &
                   (df_t2dm_subset.prev_hba1c_mmol_per_mol < 75), 
                   'hba1c_chg_58_74'] = df_t2dm_subset['hba1c_chg']

# > 75
df_t2dm_subset.loc[(df_t2dm_subset.prev_hba1c_mmol_per_mol > 75),
                   'hba1c_chg_75'] = df_t2dm_subset['hba1c_chg']

# Get mean of changes
def gen_mean(df_in, group=''):
    if group == '':
        df_mean = df_in[['date','hba1c_chg_58_74','hba1c_chg_75']].groupby(['date']).mean().reset_index()
        df_ct_58_74 = df_in[['date','hba1c_chg_58_74']].groupby(['date']).count().reset_index().rename(
            columns={'hba1c_chg_58_74':'ct_58_74'})
        df_ct_75 = df_in[['date','hba1c_chg_75']].groupby(['date']).count().reset_index().rename(
            columns={'hba1c_chg_75':'ct_75'})
        df_out = reduce(lambda left,right: pd.merge(left,right,on=['date']), 
                        [df_mean, df_ct_58_74, df_ct_75])

    else:
        df_mean = df_in[[group] + ['date','hba1c_chg_58_74','hba1c_chg_75']].groupby(['date', group]).mean().reset_index()
        df_ct_58_74 = df_in[[group] + ['date','hba1c_chg_58_74']].groupby(['date', group]).count().reset_index().rename(
            columns={'hba1c_chg_58_74':'ct_58_74'})
        df_ct_75 = df_in[[group] + ['date','hba1c_chg_75']].groupby(['date', group]).count().reset_index().rename(
            columns={'hba1c_chg_75':'ct_75'})
        df_out = reduce(lambda left,right: pd.merge(left,right,on=['date', group]), 
                        [df_mean, df_ct_58_74, df_ct_75])
    return df_out

df_chg_t2dm = gen_mean(df_t2dm_subset)
df_chg_t2dm_age = gen_mean(df_t2dm_subset, 'age_group')
df_chg_t2dm_sex = gen_mean(df_t2dm_subset, 'sex')
df_chg_t2dm_eth = gen_mean(df_t2dm_subset, 'ethnicity')
df_chg_t2dm_reg = gen_mean(df_t2dm_subset, 'region')
df_chg_t2dm_imd = gen_mean(df_t2dm_subset, 'imd')
df_chg_t2dm_ld = gen_mean(df_t2dm_subset, 'learning_disability')
df_chg_t2dm_mi = gen_mean(df_t2dm_subset, 'mental_illness')

# Format fields
# Recode variables
dict_eth = {1: 'White', 2: 'Mixed', 3: 'Asian',
            4: 'Black', 5: 'Other', np.nan: 'Unknown',
            0: 'Unknown'}

dict_imd = {0: 'Unknown', 1: '1 Most deprived', 2: '2',
            3: '3', 4: '4', 5: '5 Least deprived'}

dict_ld = {1:'Yes', 0:'No'}

df_chg_t2dm_eth = df_chg_t2dm_eth.replace({"ethnicity": dict_eth})
df_chg_t2dm_imd = df_chg_t2dm_imd.replace({'imd': dict_imd})
df_chg_t2dm_ld = df_chg_t2dm_ld.replace({'learning_disability': dict_ld})
df_chg_t2dm_age = df_chg_t2dm_age.loc[df_chg_t2dm_age.age_group != '0-15']

# Export data
df_chg_t2dm.to_csv('output/data/input_chg_t2dm_all.csv')
df_chg_t2dm_age.to_csv('output/data/input_chg_t2dm_age.csv')
df_chg_t2dm_sex.to_csv('output/data/input_chg_t2dm_sex.csv')
df_chg_t2dm_eth.to_csv('output/data/input_chg_t2dm_eth.csv')
df_chg_t2dm_reg.to_csv('output/data/input_chg_t2dm_reg.csv')
df_chg_t2dm_imd.to_csv('output/data/input_chg_t2dm_imd.csv')
df_chg_t2dm_ld.to_csv('output/data/input_chg_t2dm_ld.csv')
df_chg_t2dm_mi.to_csv('output/data/input_chg_t2dm_mi.csv')